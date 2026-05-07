using Api.Hubs;
using Api.Integracoes;
using Dominios.MovimentosPortaria.Entidades;
using Dominios.Unidades.Entidades;
using Microsoft.AspNetCore.SignalR;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Repositorios.Contexto;

namespace Api.BackgroundServices;

// HIST-022 — RN-017: notificacoes assincronas com retry exponencial
public class NotificacaoWorker : BackgroundService
{
    private readonly IServiceScopeFactory _scopes;
    private readonly ILogger<NotificacaoWorker> _logger;
    private static readonly TimeSpan[] Backoff = { TimeSpan.FromMinutes(1), TimeSpan.FromMinutes(5), TimeSpan.FromMinutes(15), TimeSpan.FromHours(1) };
    private static readonly int MaxTentativas = 8;

    public NotificacaoWorker(IServiceScopeFactory scopes, ILogger<NotificacaoWorker> logger)
    {
        _scopes = scopes;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try { await ProcessarPendentes(stoppingToken); }
            catch (Exception ex) { _logger.LogError(ex, "Erro no NotificacaoWorker"); }
            try { await Task.Delay(TimeSpan.FromSeconds(30), stoppingToken); }
            catch (TaskCanceledException) { }
        }
    }

    private async Task ProcessarPendentes(CancellationToken ct)
    {
        using var scope = _scopes.CreateScope();
        var ctx = scope.ServiceProvider.GetRequiredService<ContextoDB>();
        var hub = scope.ServiceProvider.GetService<IHubContext<PainelChamadaHub>>();
        var evolution = scope.ServiceProvider.GetRequiredService<IEvolutionApiClient>();
        var email = scope.ServiceProvider.GetRequiredService<IEmailSender>();
        var agora = DateTime.UtcNow;

        ctx.ChangeTracker.AutoDetectChangesEnabled = true;

        var pendentes = await ctx.Set<NotificacaoPendente>()
            .Where(n => (n.Status == StatusNotificacao.Pendente || n.Status == StatusNotificacao.Falhou)
                        && (n.ProximaTentativa == null || n.ProximaTentativa <= agora))
            .Take(50)
            .ToListAsync(ct);

        if (pendentes.Count == 0) return;

        // Cache de unidades para evitar N queries em batch
        var unidadeIds = pendentes.Select(n => n.MovimentoPortariaId).Distinct().ToList();
        var movsToUnidade = await ctx.MovimentosPortaria
            .Where(m => unidadeIds.Contains(m.Id))
            .Select(m => new { m.Id, m.UnidadeId })
            .ToDictionaryAsync(m => m.Id, m => m.UnidadeId, ct);

        var cacheUnidade = new Dictionary<Guid, Unidade?>();

        foreach (var n in pendentes)
        {
            try
            {
                if (n.Canal == CanalNotificacao.Socket)
                {
                    if (hub != null)
                    {
                        var grupo = ExtrairGrupoUnidade(n.Destino);
                        await hub.Clients.Group(grupo).SendAsync("evento", n.Payload, ct);
                    }
                }
                else if (n.Canal == CanalNotificacao.Whatsapp)
                {
                    var unidadeId = movsToUnidade.GetValueOrDefault(n.MovimentoPortariaId);
                    var unidade = await ResolverUnidade(ctx, cacheUnidade, unidadeId, ct);
                    if (unidade == null || string.IsNullOrWhiteSpace(unidade.ConfiguracaoEvolutionApiUrl) || string.IsNullOrWhiteSpace(unidade.ConfiguracaoEvolutionApiToken))
                        throw new InvalidOperationException("Unidade sem Evolution API configurada");

                    var instancia = unidade.Nome; // convencao: nome da instancia = nome da unidade
                    await evolution.EnviarMensagem(unidade.ConfiguracaoEvolutionApiUrl!, unidade.ConfiguracaoEvolutionApiToken!, instancia, n.Destino, n.Payload, ct);
                }
                else if (n.Canal == CanalNotificacao.Email)
                {
                    await email.Enviar(n.Destino, "Frigoestrela — Convocacao", n.Payload, ct);
                }

                n.Status = StatusNotificacao.Enviada;
                n.Tentativas++;
                n.UltimoErro = null;
                ctx.Set<NotificacaoPendente>().Update(n);
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Falha ao enviar notificacao {Id} ({Canal})", n.Id, n.Canal);
                n.Tentativas++;
                n.UltimoErro = ex.Message[..Math.Min(2000, ex.Message.Length)];
                if (n.Tentativas >= MaxTentativas)
                {
                    n.Status = StatusNotificacao.Descartada;
                    n.ProximaTentativa = null;
                }
                else
                {
                    n.Status = StatusNotificacao.Falhou;
                    var idx = Math.Min(n.Tentativas - 1, Backoff.Length - 1);
                    n.ProximaTentativa = agora + Backoff[idx];
                }
                ctx.Set<NotificacaoPendente>().Update(n);
            }
        }
        await ctx.SaveChangesAsync(ct);
    }

    private static async Task<Unidade?> ResolverUnidade(ContextoDB ctx, Dictionary<Guid, Unidade?> cache, Guid unidadeId, CancellationToken ct)
    {
        if (cache.TryGetValue(unidadeId, out var u)) return u;
        u = await ctx.Unidades.FirstOrDefaultAsync(x => x.Id == unidadeId, ct);
        cache[unidadeId] = u;
        return u;
    }

    private static string ExtrairGrupoUnidade(string destino)
    {
        // formato: "unidade:{guid}:portaria:{guid}"
        var partes = destino.Split(':');
        return partes.Length >= 2 ? $"unidade:{partes[1]}" : destino;
    }
}

// HIST-023 — sinaliza chamadas expiradas (TTL e calculado dinamicamente em PainelChamadaItemSaida.ChamadaExpirada)
public class ChamadaExpiradaWorker : BackgroundService
{
    private readonly ILogger<ChamadaExpiradaWorker> _logger;

    public ChamadaExpiradaWorker(ILogger<ChamadaExpiradaWorker> logger) => _logger = logger;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            _logger.LogDebug("ChamadaExpiradaWorker tick");
            try { await Task.Delay(TimeSpan.FromMinutes(1), stoppingToken); } catch (TaskCanceledException) { }
        }
    }
}
