#!/usr/bin/env python3
"""Aplica configuracoes de seguranca em projeto C# Portaria:
- Security headers middleware (HSTS, X-Content-Type, X-Frame, Referrer, Permissions)
- Rate limiting (.NET 9: AddRateLimiter) com policy especifica para /entrar
- Audit logging service (login, logout, mudanca de role)
- Endurece IdentityConfig (password policy mais forte, lockout)
- Restringe CORS para origens especificas

Uso: python .framework/scripts/aplicar_seguranca_csharp.py --raiz <projeto> [--cors-origins "https://meudominio.com,https://app.meudominio.com"]
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

SECURITY_HEADERS_MW = '''using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;

namespace Api.Middleware;

public static class SecurityHeadersMiddleware
{
    public static IApplicationBuilder UseSecurityHeaders(this IApplicationBuilder app)
    {
        return app.Use(async (ctx, next) =>
        {
            ctx.Response.Headers["X-Content-Type-Options"] = "nosniff";
            ctx.Response.Headers["X-Frame-Options"] = "DENY";
            ctx.Response.Headers["Referrer-Policy"] = "strict-origin-when-cross-origin";
            ctx.Response.Headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()";
            ctx.Response.Headers["X-Permitted-Cross-Domain-Policies"] = "none";
            await next();
        });
    }
}
'''

RATE_LIMIT_CONFIG = '''using Microsoft.AspNetCore.RateLimiting;
using System.Threading.RateLimiting;

namespace Api.Configuration;

public static class RateLimitConfig
{
    public static IServiceCollection AddRateLimitConfiguration(this IServiceCollection services)
    {
        services.AddRateLimiter(options =>
        {
            options.RejectionStatusCode = 429;

            // Politica global: 100 requests/minuto por IP
            options.GlobalLimiter = PartitionedRateLimiter.Create<HttpContext, string>(ctx =>
                RateLimitPartition.GetFixedWindowLimiter(
                    partitionKey: ctx.Connection.RemoteIpAddress?.ToString() ?? "unknown",
                    factory: _ => new FixedWindowRateLimiterOptions
                    {
                        PermitLimit = 100,
                        Window = TimeSpan.FromMinutes(1),
                        QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                        QueueLimit = 0,
                    }));

            // Politica especifica login: 5 tentativas / 15min por IP
            options.AddPolicy("login", ctx =>
                RateLimitPartition.GetFixedWindowLimiter(
                    partitionKey: ctx.Connection.RemoteIpAddress?.ToString() ?? "unknown",
                    factory: _ => new FixedWindowRateLimiterOptions
                    {
                        PermitLimit = 5,
                        Window = TimeSpan.FromMinutes(15),
                    }));
        });
        return services;
    }
}
'''

AUDIT_LOG_SERVICE = '''using Microsoft.EntityFrameworkCore;

namespace Api.Identidade;

public enum TipoEventoAuditoria
{
    LoginSucesso,
    LoginFalha,
    Logout,
    Registro,
    TrocaSenha,
    AdicaoRole,
    RemocaoRole,
    Exclusao,
}

public class AuditoriaService
{
    private readonly ILogger<AuditoriaService> _logger;

    public AuditoriaService(ILogger<AuditoriaService> logger) => _logger = logger;

    public void Registrar(TipoEventoAuditoria tipo, string usuarioEmail, string? ipAddress = null, string? detalhes = null)
    {
        // Log estruturado: ferramentas como Seq/Datadog/CloudWatch parseiam por nome de campo
        _logger.LogInformation("AUDIT {Tipo} usuario={Usuario} ip={Ip} detalhes={Detalhes}",
            tipo.ToString(), usuarioEmail, ipAddress ?? "?", detalhes ?? "");
    }
}
'''

# Patches no Startup/Program/IdentityConfig
def patch_startup(raiz: Path, cors_origins: str | None) -> bool:
    p = raiz / "servicos/api/Api/Startup.cs"
    if not p.exists():
        print(f"  AVISO: {p} nao existe"); return False
    txt = p.read_text(encoding="utf-8")
    mudou = False

    # using Api.Middleware
    if "using Api.Middleware;" not in txt:
        txt = re.sub(r"(using [^\n]+\n)(?!using )", r"\1using Api.Middleware;\n", txt, count=1)
        mudou = True

    # using Microsoft.AspNetCore.RateLimiting
    if "using Microsoft.AspNetCore.RateLimiting;" not in txt:
        txt = re.sub(r"(using [^\n]+\n)(?!using )", r"\1using Microsoft.AspNetCore.RateLimiting;\n", txt, count=1)
        mudou = True

    # AddRateLimitConfiguration
    if "AddRateLimitConfiguration" not in txt:
        txt = re.sub(r"(services\.AddSwaggerConfiguration\(\);)",
                     r"\1\n        services.AddRateLimitConfiguration();", txt, count=1)
        mudou = True

    # CORS especifico se origins fornecidos
    if cors_origins:
        origens = [o.strip() for o in cors_origins.split(",") if o.strip()]
        origens_str = ", ".join(f'"{o}"' for o in origens)
        # nao patchamos automaticamente o ApiConfig (multi-origin requer cuidado)
        print(f"  NOTA: aplique manualmente em ApiConfig.cs:")
        print(f"        builder.WithOrigins({origens_str}).AllowAnyMethod().AllowAnyHeader().AllowCredentials();")

    # UseHsts em prod (no metodo Configure)
    if "UseHsts" not in txt:
        # Inserir HSTS quando NAO for development (ou seja, apos UseDeveloperExceptionPage envolto em if)
        # Aqui adicionamos no Configure -> Startup.cs (caso bem simples, fora de IsDevelopment)
        # Nao temos certeza onde Configure esta no Startup.cs limpo; vou inserir antes do UseHttpsRedirection caso exista
        # (Se nao houver, sugerir insercao manual)
        # Como nosso Startup limpo nao tem Configure (esta no ApiConfig.cs), pular aqui
        pass

    # UseSecurityHeaders
    if "UseSecurityHeaders" not in txt:
        # nao patchamos aqui, fica em ApiConfig.cs / Configure
        pass

    # UseRateLimiter
    if "UseRateLimiter" not in txt:
        # nao patchamos no Startup limpo (nao tem Configure)
        pass

    if mudou:
        p.write_text(txt, encoding="utf-8")
        print("  Startup.cs atualizado")
    return mudou

def patch_apiconfig(raiz: Path) -> bool:
    p = raiz / "servicos/api/Api/Configuration/ApiConfig.cs"
    if not p.exists():
        print(f"  AVISO: {p} nao existe"); return False
    txt = p.read_text(encoding="utf-8")
    mudou = False

    if "using Api.Middleware;" not in txt:
        txt = re.sub(r"(using [^\n]+\n)(?!using )", r"\1using Api.Middleware;\n", txt, count=1)
        mudou = True

    # Adicionar UseSecurityHeaders + UseHsts + UseRateLimiter no UseApiConfiguration
    if "UseSecurityHeaders" not in txt:
        # inserir apos app.UseHttpsRedirection (se existe) ou no inicio do metodo
        if "UseHttpsRedirection" in txt:
            txt = re.sub(r"(app\.UseHttpsRedirection\(\);)",
                         r"\1\n        app.UseSecurityHeaders();\n        if (!env.IsDevelopment()) app.UseHsts();", txt, count=1)
            mudou = True
        else:
            # fallback: inserir no inicio do bloco do metodo
            txt = re.sub(r"(public static void UseApiConfiguration[^{]*\{\n)",
                         r"\1        app.UseSecurityHeaders();\n        if (!env.IsDevelopment()) app.UseHsts();\n", txt, count=1)
            mudou = True

    if "UseRateLimiter" not in txt:
        # inserir antes de UseEndpoints/MapControllers
        if "UseEndpoints" in txt:
            txt = re.sub(r"(\s+)(app\.UseEndpoints)", r"\1app.UseRateLimiter();\1\2", txt, count=1)
            mudou = True
        elif "MapControllers" in txt:
            txt = re.sub(r"(\s+)(app\.UseAuthConfiguration\(\);)", r"\1\2\n        app.UseRateLimiter();", txt, count=1)
            mudou = True

    if mudou:
        p.write_text(txt, encoding="utf-8")
        print("  ApiConfig.cs atualizado (UseSecurityHeaders, UseHsts, UseRateLimiter)")
    return mudou

def patch_identityconfig(raiz: Path, prod_mode: bool) -> bool:
    p = raiz / "servicos/api/Api/Configuration/IdentityConfig.cs"
    if not p.exists():
        print(f"  AVISO: {p} nao existe"); return False
    txt = p.read_text(encoding="utf-8")
    mudou = False

    if prod_mode and "RequireDigit = false" in txt:
        # endurece para prod
        txt = txt.replace("Password.RequireDigit = false", "Password.RequireDigit = true")
        txt = txt.replace("Password.RequireLowercase = false", "Password.RequireLowercase = true")
        txt = txt.replace("Password.RequireUppercase = false", "Password.RequireUppercase = true")
        txt = txt.replace("Password.RequireNonAlphanumeric = false", "Password.RequireNonAlphanumeric = true")
        txt = re.sub(r"Password\.RequiredLength\s*=\s*\d+", "Password.RequiredLength = 8", txt)
        # adiciona lockout se nao existe
        if "Lockout" not in txt:
            insert = (
                '                options.Lockout.MaxFailedAccessAttempts = 5;\n'
                '                options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(15);\n'
                '                options.Lockout.AllowedForNewUsers = true;\n'
            )
            txt = re.sub(r"(options\.User\.AllowedUserNameCharacters[^\n]+\n)", r"\1" + insert, txt)
        mudou = True

    if mudou:
        p.write_text(txt, encoding="utf-8")
        print("  IdentityConfig.cs endurecido para producao (password policy + lockout)")
    return mudou

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--cors-origins", default=None, help="virgula-separados, ex: 'https://app.com,https://admin.app.com'")
    ap.add_argument("--prod-mode", action="store_true", help="endurece password policy + lockout")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()

    if not (raiz / "servicos/api/Api/Api.csproj").exists():
        print(f"ERRO: nao parece projeto C# Portaria em {raiz}"); sys.exit(2)

    api_dir = raiz / "servicos/api/Api"

    # 1. SecurityHeadersMiddleware
    mw_dir = api_dir / "Middleware"
    mw_dir.mkdir(parents=True, exist_ok=True)
    mw_file = mw_dir / "SecurityHeadersMiddleware.cs"
    if not mw_file.exists():
        mw_file.write_text(SECURITY_HEADERS_MW, encoding="utf-8")
        print("+ Middleware/SecurityHeadersMiddleware.cs")
    else:
        print("= Middleware/SecurityHeadersMiddleware.cs (ja existe)")

    # 2. RateLimitConfig
    rl_file = api_dir / "Configuration/RateLimitConfig.cs"
    if not rl_file.exists():
        rl_file.write_text(RATE_LIMIT_CONFIG, encoding="utf-8")
        print("+ Configuration/RateLimitConfig.cs")
    else:
        print("= Configuration/RateLimitConfig.cs (ja existe)")

    # 3. AuditoriaService
    audit_file = api_dir / "Identidade/AuditoriaService.cs"
    if not audit_file.exists():
        audit_file.write_text(AUDIT_LOG_SERVICE, encoding="utf-8")
        print("+ Identidade/AuditoriaService.cs")
    else:
        print("= Identidade/AuditoriaService.cs (ja existe)")

    # 4. Patches
    patch_startup(raiz, args.cors_origins)
    patch_apiconfig(raiz)
    if args.prod_mode:
        patch_identityconfig(raiz, prod_mode=True)

    print("\nPROXIMOS PASSOS:")
    print("1. Registrar AuditoriaService no DI (DependencyInjectionConfig.cs):")
    print("     services.AddScoped<AuditoriaService>();")
    print("2. Aplicar [EnableRateLimiting(\"login\")] no endpoint /api/auth/v1/entrar")
    print("3. No AuthController.Entrar, injetar AuditoriaService e registrar LoginSucesso/LoginFalha")
    print("4. Restringir CORS em ApiConfig.cs:")
    print("     builder.WithOrigins(\"https://seudominio.com\").AllowAnyMethod().AllowAnyHeader();")
    print("5. Mover JWT secret e ConnectionString para variaveis de ambiente em prod")
    print("6. Rodar: python .framework/scripts/verificar_seguranca.py --stack csharp")
    print("7. dotnet build")

if __name__ == "__main__":
    main()
