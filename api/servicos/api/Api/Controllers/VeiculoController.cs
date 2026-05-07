using Core.Mediator;
using Core.ObjetoDominio.Autorizacao;
using Microsoft.AspNetCore.Authorization;
using Core.ObjetoDominio;
using Dominios.Veiculos.Comandos.Entradas;
using Dominios.Veiculos.Comandos.Saidas;
using Dominios.Veiculos.IRepositorios;
using Microsoft.AspNetCore.Mvc;
using WebApi.Core.Controller;

namespace Api.Controllers;

[Route("api/[controller]")]
[Authorize(Policy = PoliticasAuth.PorteiroOuMaior)]
public class VeiculoController : MainController
{
    private readonly IMediatorHandler _mediator;
    private readonly IVeiculoRepositorio _repositorio;

    public VeiculoController(IMediatorHandler mediator, IVeiculoRepositorio repositorio)
    {
        _mediator = mediator;
        _repositorio = repositorio;
    }

    [HttpPost("v1/salvar")]
    public async Task<IComandResult> Salvar(SalvarVeiculoEntrada cmd) => await _mediator.EnviarComando(cmd);

    [HttpPut("v1/alterar")]
    public async Task<IComandResult> Alterar(AlterarVeiculoEntrada cmd) => await _mediator.EnviarComando(cmd);

    [HttpGet("v1/listar/{pageIndex:int}/{pageSize:int}")]
    public async Task<PagedResult<VeiculoSaida>> Listar(int pageIndex, int pageSize, [FromQuery] string? filter = null)
        => await _repositorio.Listar(pageIndex, pageSize, filter);
}
