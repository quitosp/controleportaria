#!/usr/bin/env python3
"""Copia Core e WebApi.Core base para um projeto C# novo.

Por default usa o template interno em `.framework/templates/csharp-core/` (47 arquivos).
Pode usar `--portaria <path>` para sobrescrever com versao mais nova de um Portaria-master local.

Gera versoes limpas de ContextoDB.cs, ApiConfig.cs (Postgres), DependencyInjectionConfig.cs.

Uso:
  python .framework/scripts/copiar_core_base.py --destino <path-do-projeto> [--portaria <path>] [--com-evolution]
"""
from __future__ import annotations
import argparse, shutil, sys
from pathlib import Path

# Whitelist Core (relativo a compartilhados/core/Core/)
CORE_WHITELIST = [
    "Communication/ResponseResult.cs",
    "Data/IRepository.cs",
    "Data/IUnitOfWork.cs",
    "Exeptions/ApiException.cs",
    "Mediator/IMediatorHandler.cs",
    "Mediator/MediatorHandler.cs",
    "Mensagens/Message.cs",
    "Mensagens/CommandHandler.cs",
    "Mensagens/Event.cs",
    "Mensagens/Integrations/IntegrationEvent.cs",
    "Mensagens/Integrations/ResponseMessage.cs",
    "ObjetoDominio/Entity.cs",
    "ObjetoDominio/IAggregateRoot.cs",
    "ObjetoDominio/Comand.cs",
    "ObjetoDominio/ComandResult.cs",
    "ObjetoDominio/ComandResponse.cs",
    "ObjetoDominio/IComandResult.cs",
    "ObjetoDominio/PagedResult.cs",
    "ObjetoDominio/Paginacao.cs",
    "ObjetoDominio/Data.cs",
    "ObjetoDominio/Usuarios/Comandos/Inputs/UsuarioLoginEntrada.cs",
    "ObjetoDominio/Usuarios/Comandos/Inputs/UsuarioRegistroEntrada.cs",
    "ObjetoDominio/Usuarios/Comandos/Inputs/UsuarioTrocarSenhaEntrada.cs",
    "ObjetoDominio/Usuarios/Entidade/UsuarioClaim.cs",
    "ObjetoDominio/Usuarios/Entidade/UsuarioRespostaLogin.cs",
    "ObjetoDominio/Usuarios/Entidade/UsuarioToken.cs",
    "Paginacao/PaginacaoOutput.cs",
    "Paginacao/QueryableExtensions.cs",
    "Services/BaseApiService.cs",
    "Util/DataBrasilia.cs",
    "Util/CustomHttpRequestException.cs",
    "Exeptions/ApiException.cs",
    "Exeptions/DominioException.cs",
]

# Whitelist WebApi.Core (relativo a compartilhados/webApi.core/WebApi.Core/)
WEBAPI_WHITELIST = [
    "Controller/MainController.cs",
    "Identidade/AppSettings.cs",
    "Identidade/CustomAuthorization.cs",
    "Identidade/JwtConfig.cs",
    "Usuario/AppTokenSettings.cs",
    "Usuario/AspNetUser.cs",
    "Usuario/ClaimsPrincipalExtensions.cs",
    "Usuario/IAspNetUser.cs",
    "Usuario/RefreshToken.cs",
    "Usuario/Usuario.cs",
    "Util/ConfigurationExtensions.cs",
    "Util/UtilService.cs",
    "Middleware/ExceptionMiddleware.cs",
]

# Adicional se --com-evolution
EVOLUTION_EXTRA = {
    "core": [
        "ObjetoDominio/BotMessage.cs",
        # pasta inteira Evolution
        "ObjetoDominio/Evolution/",
        "ObjetoDominio/Flowise/",
        "ObjetoDominio/TypeBot/",
        "Util/UploadAudio.cs",
        "Util/UploadImagem.cs",
        "Util/UrlService.cs",
        "Enuns/EFormaPagamento.cs",
    ],
    "webapi": [
        "Models/",
        "Services/EvolutionService.cs",
        "Services/EvolutionV2Service.cs",
        "Services/FlowiseService.cs",
        "Services/IAService.cs",
        "Services/IEvolutionService.cs",
        "Services/IEvolutionV2Service.cs",
        "Services/TypeBotService.cs",
    ]
}

# Configuration files do Api (gerados limpos, nao copiados)
CONTEXTO_LIMPO = """using Core.Data;
using Core.Mediator;
using Core.Mensagens;
using Core.ObjetoDominio;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using NetDevPack.Security.JwtSigningCredentials;
using NetDevPack.Security.JwtSigningCredentials.Store.EntityFrameworkCore;
using WebApi.Core.Usuario;

namespace Repositorios.Contexto;

public class ContextoDB : IdentityDbContext<Usuario>, ISecurityKeyContext, IUnitOfWork
{
    private readonly IMediatorHandler _mediatorHandler;

    public DbSet<SecurityKeyWithPrivate> SecurityKeys { get; set; }
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
"""

API_CONFIG_POSTGRES = """using Microsoft.EntityFrameworkCore;
using NetDevPack.Security.JwtSigningCredentials.AspNetCore;
using Repositorios.Contexto;
using System.Text.Json.Serialization;
using WebApi.Core.Middleware;
using WebAPI.Core.Identidade;

namespace Api.Configuration;

public static class ApiConfig
{
    public static void AddApiConfiguration(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddDbContext<ContextoDB>(options =>
            options.UseNpgsql(configuration.GetConnectionString("DefaultConnection")));

        services.AddControllers().AddJsonOptions(options =>
        {
            options.JsonSerializerOptions.ReferenceHandler = ReferenceHandler.IgnoreCycles;
            options.JsonSerializerOptions.WriteIndented = true;
        });

        // CORS: SetIsOriginAllowed + AllowCredentials e o que funciona com JWT em browser moderno.
        // AllowAnyOrigin() e incompativel com AllowCredentials() — Chrome bloqueia.
        // Em dev libera localhost:* (qualquer porta). Em prod, restrinja via appsettings > Cors:Origens.
        services.AddCors(options =>
        {
            options.AddPolicy("Total", builder => builder
                .SetIsOriginAllowed(origin =>
                {
                    if (string.IsNullOrEmpty(origin)) return false;
                    var configuradas = configuration.GetSection("Cors:Origens").Get<string[]>() ?? Array.Empty<string>();
                    if (configuradas.Contains(origin)) return true;
                    return origin.StartsWith("http://localhost:") || origin.StartsWith("https://localhost:");
                })
                .AllowAnyMethod()
                .AllowAnyHeader()
                .AllowCredentials());
        });
    }

    public static void UseApiConfiguration(this IApplicationBuilder app, IWebHostEnvironment env)
    {
        app.UseTratamentoErros();
        // HTTPS redirect SO em producao — em dev, redirect quebra preflight OPTIONS do CORS
        // (browser nao aceita 307 em preflight). Em dev voce roda na porta http normal.
        if (!env.IsDevelopment()) app.UseHttpsRedirection();
        app.UseRouting();
        app.UseCors("Total");
        app.UseAuthConfiguration();
        app.UseEndpoints(endpoints => endpoints.MapControllers());
        app.UseJwksDiscovery();
    }
}
"""

DI_LIMPO = """using Core.Mediator;
using Core.ObjetoDominio;
using MediatR;
using Repositorios.Contexto;
using WebApi.Core.Usuario;
using WebAPI.Core.Identidade;

namespace Api.Configuration;

public static class DependencyInjectionConfig
{
    public static void RegisterServices(this IServiceCollection services)
    {
        services.AddSingleton<IHttpContextAccessor, HttpContextAccessor>();
        services.AddScoped<IAspNetUser, AspNetUser>();
        services.AddScoped<IMediatorHandler, MediatorHandler>();

        services.AddScoped<ContextoDB>();
    }
}
"""

STARTUP_LIMPO = """using Api.Configuration;
using Microsoft.AspNetCore.Mvc;
using WebAPI.Core.Identidade;

namespace Api;

public class Startup
{
    public IConfiguration Configuration { get; }

    public Startup(IHostEnvironment hostEnvironment)
    {
        var builder = new ConfigurationBuilder()
            .SetBasePath(hostEnvironment.ContentRootPath)
            .AddJsonFile("appsettings.json", true, true)
            .AddJsonFile($"appsettings.{hostEnvironment.EnvironmentName}.json", true, true)
            .AddEnvironmentVariables();

        if (hostEnvironment.IsDevelopment()) builder.AddUserSecrets<Startup>();
        Configuration = builder.Build();
    }

    public void ConfigureServices(IServiceCollection services)
    {
        services.AddIdentityConfiguration(Configuration);
        services.AddApiConfiguration(Configuration);
        services.AddJwtConfiguration(Configuration);
        services.AddSwaggerConfiguration();

        var handlers = AppDomain.CurrentDomain.Load("Dominios");
        services.AddMediatR(cfg => cfg.RegisterServicesFromAssemblies(handlers));

        services.RegisterServices();

        services.Configure<ApiBehaviorOptions>(options =>
        {
            options.SuppressModelStateInvalidFilter = true;
        });
    }

    public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
    {
        app.UseSwaggerConfiguration();
        app.UseApiConfiguration(env);
        app.UseStaticFiles();
    }
}
"""

PROGRAM_LIMPO = """namespace Api;

public class Program
{
    public static void Main(string[] args)
    {
        // permite Npgsql aceitar qualquer Kind (Utc/Local/Unspecified) em timestamp without time zone
        AppContext.SetSwitch("Npgsql.EnableLegacyTimestampBehavior", true);

        CreateHostBuilder(args).Build().Run();
    }

    public static IHostBuilder CreateHostBuilder(string[] args) =>
        Host.CreateDefaultBuilder(args)
            .ConfigureWebHostDefaults(webBuilder => webBuilder.UseStartup<Startup>());
}
"""

def copiar_arquivo(origem: Path, destino: Path):
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, destino)

def copiar_pasta(origem: Path, destino: Path):
    if not origem.exists(): return
    for f in origem.rglob("*"):
        if f.is_file() and "/obj/" not in str(f).replace("\\","/") and "/bin/" not in str(f).replace("\\","/"):
            rel = f.relative_to(origem)
            copiar_arquivo(f, destino / rel)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--destino", required=True, help="raiz do projeto C# alvo")
    ap.add_argument("--portaria", default=None, help="opcional: usar Portaria-master ao inves do template interno")
    ap.add_argument("--com-evolution", action="store_true", help="incluir tipos Evolution/Flowise/TypeBot (WhatsApp/IA)")
    args = ap.parse_args()

    destino = Path(args.destino).resolve()

    # Default: template interno em .framework/templates/csharp-core
    template_interno = Path(__file__).parent.parent / "templates/csharp-core"
    if args.portaria:
        fonte = Path(args.portaria).resolve()
        modo = "Portaria-master"
    elif template_interno.exists():
        fonte = template_interno.resolve()
        modo = "template interno"
    else:
        # fallback: tentar Portaria-master irmao
        fallback = Path("Portaria-master").resolve()
        if fallback.exists():
            fonte = fallback; modo = "Portaria-master (fallback)"
        else:
            print(f"ERRO: nem template interno em {template_interno} nem Portaria-master encontrados"); sys.exit(2)

    print(f"Fonte: {modo} ({fonte})")

    core_src = fonte / "compartilhados/core/Core"
    core_dst = destino / "compartilhados/core/Core"
    web_src = fonte / "compartilhados/webApi.core/WebApi.Core"
    web_dst = destino / "compartilhados/webApi.core/WebApi.Core"

    # Whitelist Core
    for rel in CORE_WHITELIST:
        src = core_src / rel
        if src.exists(): copiar_arquivo(src, core_dst / rel)
        else: print(f"  AVISO: {rel} nao existe na fonte")

    # Whitelist WebApi.Core
    for rel in WEBAPI_WHITELIST:
        src = web_src / rel
        if src.exists(): copiar_arquivo(src, web_dst / rel)

    # Evolution opcional
    if args.com_evolution:
        for rel in EVOLUTION_EXTRA["core"]:
            src = core_src / rel
            if src.is_dir(): copiar_pasta(src, core_dst / rel)
            elif src.exists(): copiar_arquivo(src, core_dst / rel)
        for rel in EVOLUTION_EXTRA["webapi"]:
            src = web_src / rel
            if src.is_dir(): copiar_pasta(src, web_dst / rel)
            elif src.exists(): copiar_arquivo(src, web_dst / rel)

    # Gerar arquivos limpos (Contexto, ApiConfig Postgres, DI, Startup, Program)
    (destino / "repositorios/Repositorios/Contexto").mkdir(parents=True, exist_ok=True)
    (destino / "repositorios/Repositorios/Contexto/ContextoDB.cs").write_text(CONTEXTO_LIMPO, encoding="utf-8")

    api_dir = destino / "servicos/api/Api"
    (api_dir / "Configuration").mkdir(parents=True, exist_ok=True)
    (api_dir / "Configuration/ApiConfig.cs").write_text(API_CONFIG_POSTGRES, encoding="utf-8")
    (api_dir / "Configuration/DependencyInjectionConfig.cs").write_text(DI_LIMPO, encoding="utf-8")
    (api_dir / "Startup.cs").write_text(STARTUP_LIMPO, encoding="utf-8")
    (api_dir / "Program.cs").write_text(PROGRAM_LIMPO, encoding="utf-8")

    # Copiar IdentityConfig, SwaggerConfig, AuthenticationService se existem
    for rel in ["Configuration/IdentityConfig.cs", "Configuration/SwaggerConfig.cs",
                "Identidade/Servicos/AuthenticationService.cs",
                "Identidade/Extensions/IdentityMensagensPortugues.cs"]:
        src = fonte / "servicos/api/Api" / rel
        if src.exists(): copiar_arquivo(src, api_dir / rel)

    # Patch IdentityConfig: SqlServer -> Npgsql
    ic = api_dir / "Configuration/IdentityConfig.cs"
    if ic.exists():
        txt = ic.read_text(encoding="utf-8")
        if "UseSqlServer" in txt:
            txt = txt.replace("UseSqlServer", "UseNpgsql")
            ic.write_text(txt, encoding="utf-8")
            print("OK IdentityConfig.cs patcheado: UseSqlServer -> UseNpgsql")

    total_core = sum(1 for r in CORE_WHITELIST if (core_src / r).exists())
    total_web = sum(1 for r in WEBAPI_WHITELIST if (web_src / r).exists())
    print(f"OK Core: {total_core} arquivos copiados")
    print(f"OK WebApi.Core: {total_web} arquivos copiados")
    print(f"OK ContextoDB.cs gerado limpo (Postgres, sem DbSets de agregados)")
    print(f"OK ApiConfig.cs gerado com UseNpgsql")
    print(f"OK DependencyInjectionConfig.cs gerado limpo")
    print(f"OK Startup.cs e Program.cs gerados")
    if args.com_evolution: print("OK Evolution/Flowise/TypeBot incluidos")

if __name__ == "__main__":
    main()
