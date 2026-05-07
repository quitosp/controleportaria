using Core.Data;
using Core.Mediator;
using Core.Mensagens;
using Core.ObjetoDominio;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using NetDevPack.Security.JwtSigningCredentials;
using NetDevPack.Security.JwtSigningCredentials.Store.EntityFrameworkCore;
using WebApi.Core.Usuario;
using Dominios.Unidades.Entidades;
using Repositorios.Mapeamentos;
using Dominios.Portarias.Entidades;
using Dominios.Transportadoras.Entidades;
using Dominios.Veiculos.Entidades;
using Dominios.Motoristas.Entidades;
using Dominios.MovimentosPortaria.Entidades;

namespace Repositorios.Contexto;

public class ContextoDB : IdentityDbContext<Usuario>, ISecurityKeyContext, IUnitOfWork
{
    private readonly IMediatorHandler _mediatorHandler;

    public DbSet<SecurityKeyWithPrivate> SecurityKeys { get; set; }
    public DbSet<MovimentoPortaria> MovimentosPortaria { get; set; }
    public DbSet<Motorista> Motoristas { get; set; }
    public DbSet<Veiculo> Veiculos { get; set; }
    public DbSet<Transportadora> Transportadoras { get; set; }
    public DbSet<Portaria> Portarias { get; set; }
    public DbSet<Unidade> Unidades { get; set; }
    public DbSet<RefreshToken> RefreshTokens { get; set; }

    public ContextoDB(DbContextOptions<ContextoDB> options, IMediatorHandler mediatorHandler) : base(options)
    {
        _mediatorHandler = mediatorHandler;
        ChangeTracker.QueryTrackingBehavior = QueryTrackingBehavior.NoTracking;
        ChangeTracker.AutoDetectChangesEnabled = false;
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Ignore<ComandResult>();
        modelBuilder.Ignore<Event>();

        // strings sem HasColumnType explicito ficam como text (sem limite)
        // — Maps especificos (gerados pelo scaffold) usam varchar(N) onde necessario
        foreach (var property in modelBuilder.Model.GetEntityTypes().SelectMany(
            e => e.GetProperties().Where(p => p.ClrType == typeof(DateTime) || p.ClrType == typeof(DateTime?))))
            property.SetColumnType("timestamp without time zone");

        foreach (var relationship in modelBuilder.Model.GetEntityTypes()
            .SelectMany(e => e.GetForeignKeys())) relationship.DeleteBehavior = DeleteBehavior.ClientSetNull;

        modelBuilder.ApplyConfigurationsFromAssembly(typeof(ContextoDB).Assembly);
        modelBuilder.ApplyConfiguration(new MovimentoPortariaMaps());
        modelBuilder.ApplyConfiguration(new EventoFluxoMaps());
        modelBuilder.ApplyConfiguration(new AnexoMaps());
        modelBuilder.ApplyConfiguration(new NotificacaoPendenteMaps());
        modelBuilder.ApplyConfiguration(new MotoristaMaps());
        modelBuilder.ApplyConfiguration(new VeiculoMaps());
        modelBuilder.ApplyConfiguration(new TransportadoraMaps());
        modelBuilder.ApplyConfiguration(new PortariaMaps());
        modelBuilder.ApplyConfiguration(new UnidadeMaps());

        base.OnModelCreating(modelBuilder);
    }

    public async Task<bool> Commit()
    {
        var sucesso = await base.SaveChangesAsync() > 0;
        if (sucesso) await _mediatorHandler.PublicarEventos(this);
        return sucesso;
    }
}

public static class MediatorExtension
{
    public static async Task PublicarEventos<T>(this IMediatorHandler mediator, T ctx) where T : DbContext
    {
        var domainEntities = ctx.ChangeTracker
            .Entries<Entity>()
            .Where(x => x.Entity.Notificacoes != null && x.Entity.Notificacoes.Any());

        var domainEvents = domainEntities
            .SelectMany(x => x.Entity.Notificacoes)
            .ToList();

        domainEntities.ToList().ForEach(entity => entity.Entity.LimparEventos());

        var tasks = domainEvents.Select(async (domainEvent) =>
        {
            await mediator.PublicarEvento(domainEvent);
        });

        await Task.WhenAll(tasks);
    }
}
