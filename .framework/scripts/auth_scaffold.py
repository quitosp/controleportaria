#!/usr/bin/env python3
"""Scaffold de autenticacao Identity + JWT (NetDevPack) num projeto C# padrao Portaria.
Gera AuthController, atualiza DI, garante AppTokenSettings em appsettings.

Uso: python .framework/scripts/auth_scaffold.py [--raiz .] [--admin-email admin@local] [--admin-senha Admin@123]
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

AUTH_CONTROLLER = '''using Api.Identidade.Servicos;
using Core.ObjetoDominio;
using Core.Usuarios.Comandos.Inputs;
using Core.Usuarios.EntradaSaidaDados.Entrada;
using Core.Usuarios.Entidade;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Repositorios.Contexto;
using WebApi.Core.Controller;
using WebApi.Core.Usuario;

namespace Api.Controllers;

[Route("api/[controller]")]
[AllowAnonymous]
public class AuthController : MainController
{
    private readonly AuthenticationService _auth;
    private readonly ContextoDB _context;

    public AuthController(AuthenticationService auth, ContextoDB context)
    {
        _auth = auth;
        _context = context;
    }

    [HttpPost("v1/registrar")]
    public async Task<IComandResult> Registrar(UsuarioRegistroEntrada cmd)
    {
        var user = new Usuario { UserName = cmd.Email, Email = cmd.Email, EmailConfirmed = true, Nome = cmd.Nome ?? "", SobreNome = "" };
        var result = await _auth.UserManager.CreateAsync(user, cmd.Senha);

        if (!result.Succeeded)
        {
            var erros = result.Errors.Select(e => e.Description).ToList();
            return new ComandResult(false, "Falha ao registrar", erros, 400);
        }

        var jwt = await _auth.GerarJwt(cmd.Email);
        return new ComandResult(true, "Usuario registrado com sucesso!", jwt, 200);
    }

    [HttpPost("v1/entrar")]
    public async Task<IComandResult> Entrar(UsuarioLoginEntrada cmd)
    {
        var result = await _auth.SignInManager.PasswordSignInAsync(cmd.Email, cmd.Senha, false, false);

        if (result.IsLockedOut)
            return new ComandResult(false, "Usuario bloqueado por tentativas invalidas", new List<string>(), 423);

        if (!result.Succeeded)
            return new ComandResult(false, "Email ou senha invalidos", new List<string>(), 401);

        var jwt = await _auth.GerarJwt(cmd.Email);
        return new ComandResult(true, "Login efetuado com sucesso!", jwt, 200);
    }

    [HttpPost("v1/refresh")]
    public async Task<IComandResult> Refresh([FromBody] RefreshTokenEntrada cmd)
    {
        if (string.IsNullOrEmpty(cmd?.RefreshToken))
            return new ComandResult(false, "Refresh token nao fornecido", new List<string>(), 400);

        if (!Guid.TryParse(cmd.RefreshToken, out var token))
            return new ComandResult(false, "Refresh token invalido", new List<string>(), 400);

        var refresh = await _auth.ObterRefreshToken(token);
        if (refresh is null)
            return new ComandResult(false, "Refresh token expirado ou invalido", new List<string>(), 401);

        var jwt = await _auth.GerarJwt(refresh.Username);
        return new ComandResult(true, "Token renovado", jwt, 200);
    }

    [HttpPost("v1/trocar-senha")]
    [Authorize]
    public async Task<IComandResult> TrocarSenha(UsuarioTrocarSenhaEntrada cmd)
    {
        var user = await _auth.UserManager.FindByEmailAsync(cmd.Email);
        if (user is null) return new ComandResult(false, "Usuario nao encontrado", new List<string>(), 404);

        var result = await _auth.UserManager.ChangePasswordAsync(user, cmd.SenhaAntiga, cmd.SenhaNova);
        if (!result.Succeeded)
        {
            var erros = result.Errors.Select(e => e.Description).ToList();
            return new ComandResult(false, "Falha ao trocar senha", erros, 400);
        }

        return new ComandResult(true, "Senha alterada com sucesso!", new List<string>(), 200);
    }
}

public class RefreshTokenEntrada
{
    public string RefreshToken { get; set; } = string.Empty;
}
'''

SEED_ADMIN = '''using Microsoft.AspNetCore.Identity;
using WebApi.Core.Usuario;

namespace Api.Identidade;

public static class SeedAdmin
{
    public static async Task Executar(IServiceProvider sp, string email, string senha, string[] roles)
    {
        using var scope = sp.CreateScope();
        var userManager = scope.ServiceProvider.GetRequiredService<UserManager<Usuario>>();
        var roleManager = scope.ServiceProvider.GetRequiredService<RoleManager<IdentityRole>>();

        foreach (var role in roles)
            if (!await roleManager.RoleExistsAsync(role))
                await roleManager.CreateAsync(new IdentityRole(role));

        var user = await userManager.FindByEmailAsync(email);
        if (user is null)
        {
            user = new Usuario { UserName = email, Email = email, EmailConfirmed = true, Nome = "Admin", SobreNome = "Sistema" };
            var result = await userManager.CreateAsync(user, senha);
            if (!result.Succeeded) return;
        }

        foreach (var role in roles)
            if (!await userManager.IsInRoleAsync(user, role))
                await userManager.AddToRoleAsync(user, role);
    }
}
'''

def patch_appsettings(raiz: Path):
    """Garante AppTokenSettings.RefreshTokenExpiration no appsettings."""
    for nome in ["appsettings.json", "appsettings.Development.json"]:
        p = raiz / "servicos/api/Api" / nome
        if not p.exists(): continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  AVISO: {nome} nao parseou, pule")
            continue
        if "AppTokenSettings" not in data:
            data["AppTokenSettings"] = {"RefreshTokenExpiration": 24}
            p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  {nome}: AppTokenSettings adicionado")

def patch_di(raiz: Path):
    """Adiciona AppTokenSettings binding + AuthenticationService (com FQN para evitar ambiguidade)."""
    p = raiz / "servicos/api/Api/Configuration/DependencyInjectionConfig.cs"
    if not p.exists():
        print("  AVISO: DI nao encontrado"); return
    txt = p.read_text(encoding="utf-8")
    mudou = False

    if "using WebApi.Core.Usuario;" not in txt:
        txt = re.sub(r"(using [^\n]+\n)(?!using )", r"\1using WebApi.Core.Usuario;\n", txt, count=1)
        mudou = True

    bloco_extras = ""
    if "AppTokenSettings" not in txt:
        bloco_extras += '        services.Configure<AppTokenSettings>(options => { options.RefreshTokenExpiration = 24; });\n'
    if "Api.Identidade.Servicos.AuthenticationService" not in txt:
        bloco_extras += '        services.AddScoped<Api.Identidade.Servicos.AuthenticationService>();\n'
    if bloco_extras:
        txt = re.sub(r"(public static void RegisterServices[^{]*\{\n)", r"\1" + bloco_extras, txt, count=1)
        mudou = True

    if mudou:
        p.write_text(txt, encoding="utf-8")
        print("  DI: AppTokenSettings + AuthenticationService (FQN) configurados")

def patch_program(raiz: Path, admin_email: str, admin_senha: str, roles: list[str]):
    """Adiciona chamada SeedAdmin.Executar no Program.cs."""
    p = raiz / "servicos/api/Api/Program.cs"
    if not p.exists(): return
    txt = p.read_text(encoding="utf-8")
    if "SeedAdmin" in txt: return

    novo = f'''using Api.Identidade;

namespace Api;

public class Program
{{
    public static async Task Main(string[] args)
    {{
        // permite Npgsql aceitar qualquer Kind (Utc/Local/Unspecified) em timestamp without time zone
        AppContext.SetSwitch("Npgsql.EnableLegacyTimestampBehavior", true);

        var host = CreateHostBuilder(args).Build();
        await SeedAdmin.Executar(host.Services, "{admin_email}", "{admin_senha}", new[] {{ {", ".join(f'"{r}"' for r in roles)} }});
        await host.RunAsync();
    }}

    public static IHostBuilder CreateHostBuilder(string[] args) =>
        Host.CreateDefaultBuilder(args)
            .ConfigureWebHostDefaults(webBuilder => webBuilder.UseStartup<Startup>());
}}
'''
    p.write_text(novo, encoding="utf-8")
    print("  Program.cs: SeedAdmin adicionado")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--admin-email", default="admin@local")
    ap.add_argument("--admin-senha", default="Admin@123")
    ap.add_argument("--roles", default="admin", help="virgula-separados")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()
    roles = [r.strip() for r in args.roles.split(",") if r.strip()]

    if not (raiz / "servicos/api/Api/Api.csproj").exists():
        print(f"ERRO: nao parece projeto C# em {raiz}"); sys.exit(2)

    # 1. AuthController
    auth_path = raiz / "servicos/api/Api/Controllers/AuthController.cs"
    if auth_path.exists():
        print(f"= AuthController.cs ja existe")
    else:
        auth_path.parent.mkdir(parents=True, exist_ok=True)
        auth_path.write_text(AUTH_CONTROLLER, encoding="utf-8")
        print(f"+ Controllers/AuthController.cs")

    # 2. SeedAdmin
    seed_path = raiz / "servicos/api/Api/Identidade/SeedAdmin.cs"
    if seed_path.exists():
        print(f"= SeedAdmin.cs ja existe")
    else:
        seed_path.parent.mkdir(parents=True, exist_ok=True)
        seed_path.write_text(SEED_ADMIN, encoding="utf-8")
        print(f"+ Identidade/SeedAdmin.cs")

    # 3. appsettings
    patch_appsettings(raiz)

    # 4. DI
    patch_di(raiz)

    # 5. Program.cs com seed
    patch_program(raiz, args.admin_email, args.admin_senha, roles)

    print(f"\nOK auth scaffolded.")
    print(f"  Admin seed: {args.admin_email} / {args.admin_senha}")
    print(f"  Roles: {', '.join(roles)}")
    print(f"  Endpoints: POST /api/auth/v1/registrar, /entrar, /refresh, /trocar-senha")

if __name__ == "__main__":
    main()
