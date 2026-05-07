using Core.Mediator;
using Core.ObjetoDominio.Autorizacao;
using Microsoft.AspNetCore.Authorization;
using Core.ObjetoDominio;
using Dominios.Motoristas.Comandos.Entradas;
using Dominios.Motoristas.Comandos.Saidas;
using Dominios.Motoristas.IRepositorios;
using Microsoft.AspNetCore.Mvc;
using WebApi.Core.Controller;

namespace Api.Controllers;

[Route("api/[controller]")]
[Authorize(Policy = PoliticasAuth.PorteiroOuMaior)]
public class MotoristaController : MainController
{
    private readonly IMediatorHandler _mediator;
    private readonly IMotoristaRepositorio _repositorio;

    public MotoristaController(IMediatorHandler mediator, IMotoristaRepositorio repositorio)
    {
        _mediator = mediator;
        _repositorio = repositorio;
    }

    [HttpPost("v1/salvar")]
    public async Task<IComandResult> Salvar(SalvarMotoristaEntrada cmd) => await _mediator.EnviarComando(cmd);

    [HttpPut("v1/alterar")]
    public async Task<IComandResult> Alterar(AlterarMotoristaEntrada cmd) => await _mediator.EnviarComando(cmd);

    [HttpGet("v1/listar/{pageIndex:int}/{pageSize:int}")]
    public async Task<PagedResult<MotoristaSaida>> Listar(int pageIndex, int pageSize, [FromQuery] string? filter = null)
        => await _repositorio.Listar(pageIndex, pageSize, filter);

    [HttpGet("v1/{id:guid}")]
    public async Task<IActionResult> ObterPorId(Guid id)
    {
        var m = await _repositorio.ObterPorId(id);
        if (m == null) return NotFound();
        return Ok(new
        {
            id = m.Id, nome = m.Nome, cpf = m.Cpf, whatsapp = m.Whatsapp, email = m.Email,
            status = m.Status, motivoStatus = m.MotivoStatus, unidadeId = m.UnidadeId
        });
    }

    // HIST-009 — Bloquear/desbloquear motorista (Supervisor+)
    [HttpPut("v1/{id:guid}/status")]
    [Authorize(Policy = PoliticasAuth.SupervisorOuMaior)]
    public async Task<IComandResult> AlterarStatus(Guid id, [FromBody] AlterarStatusMotoristaEntrada body)
    {
        var motorista = await _repositorio.ObterPorId(id);
        if (motorista == null) return new ComandResult(false, "Motorista nao encontrado", new List<string>(), 404);

        // RN-004 — bloqueio exige motivo
        if (body.Status == 2 && string.IsNullOrWhiteSpace(body.MotivoStatus))
            return new ComandResult(false, "Motivo obrigatorio ao bloquear motorista.", new List<string>(), 400);

        motorista.Alterar(motorista.Nome, motorista.Cpf, motorista.Whatsapp, motorista.Email,
            body.Status, body.MotivoStatus, motorista.UnidadeId);
        _repositorio.Alterar(motorista);
        await _repositorio.UnitOfWork.Commit();
        return new ComandResult(true, "Status alterado.", new { id, status = body.Status }, 200);
    }
}

public class AlterarStatusMotoristaEntrada
{
    public int Status { get; set; }
    public string? MotivoStatus { get; set; }
}
