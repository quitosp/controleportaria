using Core.Mediator;
using Core.ObjetoDominio.Autorizacao;
using Microsoft.AspNetCore.Authorization;
using Core.ObjetoDominio;
using Dominios.Transportadoras.Comandos.Entradas;
using Dominios.Transportadoras.Comandos.Saidas;
using Dominios.Transportadoras.IRepositorios;
using Microsoft.AspNetCore.Mvc;
using WebApi.Core.Controller;

namespace Api.Controllers;

[Route("api/[controller]")]
[Authorize(Policy = PoliticasAuth.PorteiroOuMaior)]
public class TransportadoraController : MainController
{
    private readonly IMediatorHandler _mediator;
    private readonly ITransportadoraRepositorio _repositorio;

    public TransportadoraController(IMediatorHandler mediator, ITransportadoraRepositorio repositorio)
    {
        _mediator = mediator;
        _repositorio = repositorio;
    }

    [HttpPost("v1/salvar")]
    public async Task<IComandResult> Salvar(SalvarTransportadoraEntrada cmd) => await _mediator.EnviarComando(cmd);

    [HttpPut("v1/alterar")]
    public async Task<IComandResult> Alterar(AlterarTransportadoraEntrada cmd) => await _mediator.EnviarComando(cmd);

    [HttpGet("v1/listar/{pageIndex:int}/{pageSize:int}")]
    public async Task<PagedResult<TransportadoraSaida>> Listar(int pageIndex, int pageSize, [FromQuery] string? filter = null)
        => await _repositorio.Listar(pageIndex, pageSize, filter);
}
