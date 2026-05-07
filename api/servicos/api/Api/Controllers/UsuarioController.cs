using Core.ObjetoDominio;
using Core.ObjetoDominio.Autorizacao;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WebApi.Core.Controller;
using WebApi.Core.Usuario;

namespace Api.Controllers;

[Route("api/usuarios")]
[Authorize(Policy = PoliticasAuth.SomenteAdmin)]
public class UsuarioController : MainController
{
    private readonly UserManager<Usuario> _userManager;

    public UsuarioController(UserManager<Usuario> userManager) => _userManager = userManager;

    [HttpGet("v1/listar/{pageIndex:int}/{pageSize:int}")]
    public async Task<object> Listar(int pageIndex, int pageSize, [FromQuery] string? filter = null)
    {
        var query = _userManager.Users.AsNoTracking();
        if (!string.IsNullOrEmpty(filter))
            query = query.Where(u => u.Nome.Contains(filter) || u.Email.Contains(filter));
        var total = await query.CountAsync();
        var lista = await query
            .OrderBy(u => u.Nome)
            .Skip((pageIndex - 1) * pageSize).Take(pageSize)
            .Select(u => new
            {
                u.Id, u.Nome, u.Email, u.UserName,
                Papel = u.Papel.ToString(),
                u.UnidadeId, u.PortariaPadraoId, u.Status
            })
            .ToListAsync();

        return new { TotalResults = total, PageIndex = pageIndex, PageSize = pageSize, List = lista };
    }

    [HttpPut("v1/{id}/papel")]
    public async Task<IComandResult> AlterarPapel(string id, [FromBody] AlterarPapelEntrada body)
    {
        var user = await _userManager.FindByIdAsync(id);
        if (user is null) return new ComandResult(false, "Usuario nao encontrado", new List<string>(), 404);

        user.DefinirPapel(body.Papel);
        user.DefinirUnidade(body.UnidadeId, body.PortariaPadraoId);
        await _userManager.UpdateAsync(user);
        return new ComandResult(true, "Papel alterado.", new { id }, 200);
    }
}

public class AlterarPapelEntrada
{
    public PapelUsuario Papel { get; set; }
    public Guid? UnidadeId { get; set; }
    public Guid? PortariaPadraoId { get; set; }
}
