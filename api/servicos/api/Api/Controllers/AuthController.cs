using Api.Identidade.Servicos;
using Core.ObjetoDominio;
using Core.ObjetoDominio.Autorizacao;
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
    [Authorize(Policy = PoliticasAuth.SomenteAdmin)]
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
    [AllowAnonymous]
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
    [AllowAnonymous]
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
