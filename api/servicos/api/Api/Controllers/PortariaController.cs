using Core.Mediator;
using Core.ObjetoDominio.Autorizacao;
using Microsoft.AspNetCore.Authorization;
using Core.ObjetoDominio;
using Dominios.Portarias.Comandos.Entradas;
using Dominios.Portarias.Comandos.Saidas;
using Dominios.Portarias.IRepositorios;
using Microsoft.AspNetCore.Mvc;
using WebApi.Core.Controller;

namespace Api.Controllers;

[Route("api/[controller]")]
[Authorize(Policy = PoliticasAuth.SomenteAdmin)]
public class PortariaController : MainController
{
    private readonly IMediatorHandler _mediator;
    private readonly IPortariaRepositorio _repositorio;

    public PortariaController(IMediatorHandler mediator, IPortariaRepositorio repositorio)
    {
        _mediator = mediator;
        _repositorio = repositorio;
    }

    [HttpPost("v1/salvar")]
    public async Task<IComandResult> Salvar(SalvarPortariaEntrada cmd) => await _mediator.EnviarComando(cmd);

    [HttpPut("v1/alterar")]
    public async Task<IComandResult> Alterar(AlterarPortariaEntrada cmd) => await _mediator.EnviarComando(cmd);

    [HttpGet("v1/listar/{pageIndex:int}/{pageSize:int}")]
    public async Task<PagedResult<PortariaSaida>> Listar(int pageIndex, int pageSize, [FromQuery] string? filter = null)
        => await _repositorio.Listar(pageIndex, pageSize, filter);
}
