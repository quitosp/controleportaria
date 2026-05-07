using Core.Mediator;
using Core.ObjetoDominio;
using Core.ObjetoDominio.Autorizacao;
using Dominios.Unidades.Comandos.Entradas;
using Dominios.Unidades.Comandos.Saidas;
using Dominios.Unidades.IRepositorios;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using WebApi.Core.Controller;

namespace Api.Controllers;

[Route("api/[controller]")]
[Authorize(Policy = PoliticasAuth.SomenteAdmin)]
public class UnidadeController : MainController
{
    private readonly IMediatorHandler _mediator;
    private readonly IUnidadeRepositorio _repositorio;

    public UnidadeController(IMediatorHandler mediator, IUnidadeRepositorio repositorio)
    {
        _mediator = mediator;
        _repositorio = repositorio;
    }

    [HttpPost("v1/salvar")]
    public async Task<IComandResult> Salvar(SalvarUnidadeEntrada cmd) => await _mediator.EnviarComando(cmd);

    [HttpPut("v1/alterar")]
    public async Task<IComandResult> Alterar(AlterarUnidadeEntrada cmd) => await _mediator.EnviarComando(cmd);

    [HttpGet("v1/listar/{pageIndex:int}/{pageSize:int}")]
    public async Task<PagedResult<UnidadeSaida>> Listar(int pageIndex, int pageSize, [FromQuery] string? filter = null)
        => await _repositorio.Listar(pageIndex, pageSize, filter);
}
