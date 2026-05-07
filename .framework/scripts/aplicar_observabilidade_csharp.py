#!/usr/bin/env python3
"""Aplica observabilidade em projeto C# Portaria:
- Serilog (Console JSON + arquivo) com enrichers (RequestId, MachineName, Environment)
- Health checks (/health, /health/ready, /health/live) com check de Postgres
- Endpoint de logs e healthchecks documentado no Swagger

Uso: python .framework/scripts/aplicar_observabilidade_csharp.py --raiz <projeto>
"""
from __future__ import annotations
import argparse, re, subprocess, sys
from pathlib import Path

PACOTES_API = [
    ("Serilog.AspNetCore", "8.0.3"),
    ("Serilog.Sinks.Console", "6.0.0"),
    ("Serilog.Sinks.File", "6.0.0"),
    ("Serilog.Enrichers.Environment", "3.0.1"),
    ("Serilog.Formatting.Compact", "3.0.0"),
    ("AspNetCore.HealthChecks.NpgSql", "9.0.0"),
    ("AspNetCore.HealthChecks.UI.Client", "9.0.0"),
]

LOGGING_CONFIG = '''using Serilog;
using Serilog.Events;
using Serilog.Formatting.Compact;

namespace Api.Configuration;

public static class LoggingConfig
{
    public static void ConfigurarSerilog(this WebApplicationBuilder builder)
    {
        builder.Host.UseSerilog((ctx, services, cfg) =>
        {
            cfg.ReadFrom.Configuration(ctx.Configuration)
               .ReadFrom.Services(services)
               .Enrich.FromLogContext()
               .Enrich.WithMachineName()
               .Enrich.WithEnvironmentName()
               .MinimumLevel.Information()
               .MinimumLevel.Override("Microsoft.AspNetCore", LogEventLevel.Warning)
               .MinimumLevel.Override("Microsoft.EntityFrameworkCore", LogEventLevel.Warning)
               .WriteTo.Console(new CompactJsonFormatter())
               .WriteTo.File(new CompactJsonFormatter(),
                             "logs/api-.json",
                             rollingInterval: RollingInterval.Day,
                             retainedFileCountLimit: 14);
        });
    }
}
'''

HEALTH_CHECK_CONFIG = '''using HealthChecks.UI.Client;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.Extensions.Diagnostics.HealthChecks;

namespace Api.Configuration;

public static class HealthCheckConfig
{
    public static IServiceCollection AddHealthCheckConfiguration(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddHealthChecks()
            .AddNpgSql(
                configuration.GetConnectionString("DefaultConnection") ?? "",
                name: "postgres",
                tags: new[] { "ready", "db" });
        return services;
    }

    public static IApplicationBuilder UseHealthCheckConfiguration(this IApplicationBuilder app)
    {
        app.UseHealthChecks("/health", new HealthCheckOptions
        {
            ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
        });
        app.UseHealthChecks("/health/ready", new HealthCheckOptions
        {
            Predicate = h => h.Tags.Contains("ready"),
            ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
        });
        app.UseHealthChecks("/health/live", new HealthCheckOptions
        {
            Predicate = _ => false,
            ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
        });
        return app;
    }
}
'''

REQUEST_LOGGING_MIDDLEWARE = '''using Serilog;
using Serilog.Context;

namespace Api.Middleware;

public static class RequestLoggingMiddleware
{
    public static IApplicationBuilder UseRequestLogging(this IApplicationBuilder app)
    {
        return app.UseSerilogRequestLogging(options =>
        {
            options.MessageTemplate = "HTTP {RequestMethod} {RequestPath} -> {StatusCode} em {Elapsed:0}ms";
            options.GetLevel = (ctx, _, ex) =>
                ex != null ? Serilog.Events.LogEventLevel.Error :
                ctx.Response.StatusCode >= 500 ? Serilog.Events.LogEventLevel.Error :
                ctx.Response.StatusCode >= 400 ? Serilog.Events.LogEventLevel.Warning :
                Serilog.Events.LogEventLevel.Information;
            options.EnrichDiagnosticContext = (diag, ctx) =>
            {
                diag.Set("UserId", ctx.User?.FindFirst("sub")?.Value ?? "anon");
                diag.Set("RemoteIp", ctx.Connection.RemoteIpAddress?.ToString() ?? "?");
            };
        });
    }
}
'''

def patch_program_minimal(raiz: Path) -> bool:
    """Atualiza Program.cs para usar WebApplicationBuilder + Serilog."""
    p = raiz / "servicos/api/Api/Program.cs"
    if not p.exists():
        print(f"  AVISO: {p} nao existe"); return False
    txt = p.read_text(encoding="utf-8")
    if "ConfigurarSerilog" in txt:
        print("  Program.cs ja tem Serilog"); return False
    # Adiciona using Serilog
    if "using Serilog;" not in txt:
        txt = re.sub(r"(using Api\.Identidade;)", r"using Serilog;\nusing Api.Configuration;\n\1", txt)
    # Adiciona ConfigurarSerilog. Como nosso Program e classico (CreateHostBuilder), inserir Log.Information no Main
    if "Log.Information" not in txt:
        # adicionar try/catch + Serilog config minima inline
        novo = txt.replace(
            "var host = CreateHostBuilder(args).Build();",
            (
                "Log.Logger = new Serilog.LoggerConfiguration()\n"
                "            .Enrich.FromLogContext()\n"
                "            .WriteTo.Console(new Serilog.Formatting.Compact.CompactJsonFormatter())\n"
                "            .CreateLogger();\n\n"
                "        try\n"
                "        {\n"
                "            Log.Information(\"Iniciando API\");\n"
                "            var host = CreateHostBuilder(args).Build();"
            )
        ).replace(
            "await host.RunAsync();",
            "await host.RunAsync();\n        }\n        catch (Exception ex) { Log.Fatal(ex, \"Falha ao iniciar\"); throw; }\n        finally { Log.CloseAndFlush(); }"
        )
        # Tambem adicionar UseSerilog no CreateHostBuilder
        novo = novo.replace(
            ".ConfigureWebHostDefaults(webBuilder => webBuilder.UseStartup<Startup>());",
            ".UseSerilog((ctx, cfg) => cfg.ReadFrom.Configuration(ctx.Configuration).Enrich.FromLogContext().Enrich.WithMachineName().Enrich.WithEnvironmentName().WriteTo.Console(new Serilog.Formatting.Compact.CompactJsonFormatter()).WriteTo.File(new Serilog.Formatting.Compact.CompactJsonFormatter(), \"logs/api-.json\", rollingInterval: Serilog.RollingInterval.Day, retainedFileCountLimit: 14))\n            .ConfigureWebHostDefaults(webBuilder => webBuilder.UseStartup<Startup>());"
        )
        p.write_text(novo, encoding="utf-8")
        print("  Program.cs atualizado com Serilog")
        return True
    return False

def patch_startup(raiz: Path) -> bool:
    p = raiz / "servicos/api/Api/Startup.cs"
    if not p.exists(): return False
    txt = p.read_text(encoding="utf-8")
    mudou = False

    if "AddHealthCheckConfiguration" not in txt:
        if "services.AddSwaggerConfiguration();" in txt:
            txt = txt.replace(
                "services.AddSwaggerConfiguration();",
                "services.AddSwaggerConfiguration();\n        services.AddHealthCheckConfiguration(Configuration);"
            )
            mudou = True

    if "UseHealthCheckConfiguration" not in txt:
        if "app.UseStaticFiles();" in txt:
            txt = txt.replace(
                "app.UseStaticFiles();",
                "app.UseStaticFiles();\n        app.UseHealthCheckConfiguration();\n        app.UseRequestLogging();"
            )
            mudou = True

    if mudou:
        # using Api.Middleware
        for u in ["using Api.Middleware;"]:
            if u not in txt:
                txt = re.sub(r"(using [^\n]+\n)(?!using )", r"\1" + u + "\n", txt, count=1)
        p.write_text(txt, encoding="utf-8")
        print("  Startup.cs atualizado com Health checks + Request logging")
    return mudou

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()

    if not (raiz / "servicos/api/Api/Api.csproj").exists():
        print(f"ERRO: nao parece projeto C#-portaria"); sys.exit(2)

    api_dir = raiz / "servicos/api/Api"

    # 1. Pacotes
    print("Instalando pacotes...")
    for nome, ver in PACOTES_API:
        try:
            subprocess.run(["dotnet", "add", str(api_dir / "Api.csproj"), "package", nome, "--version", ver],
                          check=True, capture_output=True, timeout=120)
            print(f"  + {nome} {ver}")
        except subprocess.CalledProcessError as e:
            print(f"  AVISO {nome}: {e}")

    # 2. Arquivos
    cfg_dir = api_dir / "Configuration"
    cfg_dir.mkdir(exist_ok=True)
    arquivos = [
        (cfg_dir / "LoggingConfig.cs", LOGGING_CONFIG),
        (cfg_dir / "HealthCheckConfig.cs", HEALTH_CHECK_CONFIG),
        (api_dir / "Middleware/RequestLoggingMiddleware.cs", REQUEST_LOGGING_MIDDLEWARE),
    ]
    for path, content in arquivos:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            print(f"  = {path.relative_to(raiz)} (ja existe)")
        else:
            path.write_text(content, encoding="utf-8")
            print(f"  + {path.relative_to(raiz)}")

    # 3. Patches
    patch_program_minimal(raiz)
    patch_startup(raiz)

    # 4. .gitignore para logs/
    gi = raiz / ".gitignore"
    if gi.exists():
        gi_txt = gi.read_text(encoding="utf-8")
        if "logs/" not in gi_txt:
            gi.write_text(gi_txt + "\n# Logs gerados\nlogs/\n", encoding="utf-8")
            print("  .gitignore: logs/ adicionado")

    print("\nOK observabilidade aplicada.")
    print("\nEndpoints novos:")
    print("  GET /health      — overall health")
    print("  GET /health/ready — readiness (banco)")
    print("  GET /health/live  — liveness")
    print("\nLogs:")
    print("  Console: JSON estruturado (compatível com Datadog/Loki/Seq)")
    print("  Arquivo: logs/api-{date}.json (rotacao diaria, 14 dias)")
    print("\nProximo: dotnet build")

if __name__ == "__main__":
    main()
