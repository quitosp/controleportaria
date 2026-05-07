using Core.Mediator;
using Core.ObjetoDominio;
using Core.ObjetoDominio.Autorizacao;
using Dominios.MovimentosPortaria.Comandos.Entradas;
using Dominios.MovimentosPortaria.Comandos.Saidas;
using Dominios.MovimentosPortaria.IRepositorios;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using WebApi.Core.Controller;

namespace Api.Controllers;

[Route("api/movimentos")]
[Authorize(Policy = PoliticasAuth.PorteiroOuMaior)]
public class MovimentoPortariaController : MainController
{
    private readonly IMediatorHandler _mediator;
    private readonly IMovimentoPortariaRepositorio _repositorio;

    public MovimentoPortariaController(IMediatorHandler mediator, IMovimentoPortariaRepositorio repositorio)
    {
        _mediator = mediator;
        _repositorio = repositorio;
    }

    // HIST-010
    [HttpPost("v1/cadastrar-chegada")]
    public async Task<IComandResult> CadastrarChegada(CadastrarChegadaEntrada cmd)
        => await _mediator.EnviarComando(cmd);

    // HIST-013
    [HttpPost("v1/{id:guid}/confirmar-entrada")]
    public async Task<IComandResult> ConfirmarEntrada(Guid id)
        => await _mediator.EnviarComando(new ConfirmarEntradaEntrada { MovimentoPortariaId = id });

    // HIST-014
    [HttpPost("v1/{id:guid}/registrar-saida")]
    public async Task<IComandResult> RegistrarSaida(Guid id, [FromBody] RegistrarSaidaEntrada cmd)
    {
        cmd.MovimentoPortariaId = id;
        return await _mediator.EnviarComando(cmd);
    }

    // HIST-011
    [HttpPost("v1/{id:guid}/chamar")]
    [Authorize(Policy = PoliticasAuth.LiderOuMaior)]
    public async Task<IComandResult> Chamar(Guid id)
        => await _mediator.EnviarComando(new ChamarVeiculoEntrada { MovimentoPortariaId = id });

    // HIST-012
    [HttpPost("v1/{id:guid}/recancelar-chamada")]
    [Authorize(Policy = PoliticasAuth.LiderOuMaior)]
    public async Task<IComandResult> RecancelarChamada(Guid id)
        => await _mediator.EnviarComando(new RecancelarChamadaEntrada { MovimentoPortariaId = id });

    // HIST-015
    [HttpPost("v1/{id:guid}/cancelar")]
    public async Task<IComandResult> Cancelar(Guid id, [FromBody] CancelarMovimentoEntrada cmd)
    {
        cmd.MovimentoPortariaId = id;
        return await _mediator.EnviarComando(cmd);
    }

    // HIST-016
    [HttpPost("v1/{id:guid}/desistir")]
    public async Task<IComandResult> Desistir(Guid id, [FromBody] DesistirMovimentoEntrada cmd)
    {
        cmd.MovimentoPortariaId = id;
        return await _mediator.EnviarComando(cmd);
    }

    // HIST-017
    [HttpPut("v1/{id:guid}")]
    public async Task<IComandResult> Alterar(Guid id, [FromBody] AlterarMovimentoEntrada cmd)
    {
        cmd.MovimentoPortariaId = id;
        return await _mediator.EnviarComando(cmd);
    }

    // HIST-018
    [HttpPost("v1/{id:guid}/anexar")]
    [RequestSizeLimit(11 * 1024 * 1024)]
    public async Task<IComandResult> Anexar(Guid id, [FromForm] IFormFile arquivo, [FromForm] int estagio)
    {
        if (arquivo == null || arquivo.Length == 0)
            return new ComandResult(false, "Arquivo nao enviado", new List<string>(), 400);
        using var ms = new MemoryStream();
        await arquivo.CopyToAsync(ms);
        var cmd = new AnexarArquivoEntrada
        {
            MovimentoPortariaId = id,
            Estagio = (Dominios.MovimentosPortaria.Entidades.EstagioAnexo)estagio,
            NomeArquivo = arquivo.FileName,
            ContentType = arquivo.ContentType,
            Conteudo = ms.ToArray()
        };
        return await _mediator.EnviarComando(cmd);
    }

    [HttpGet("v1/listar/{pageIndex:int}/{pageSize:int}")]
    public async Task<PagedResult<MovimentoPortariaSaida>> Listar(int pageIndex, int pageSize, [FromQuery] string? filter = null)
        => await _repositorio.Listar(pageIndex, pageSize, filter);

    [HttpGet("v1/{id:guid}")]
    public async Task<IActionResult> ObterPorId(Guid id)
    {
        var m = await _repositorio.ObterPorId(id);
        if (m == null) return NotFound(new ComandResult(false, "Movimento nao encontrado", new List<string>(), 404));
        return Ok(new MovimentoPortariaSaida
        {
            MovimentoPortariaId = m.Id,
            UnidadeId = m.UnidadeId,
            PortariaChegadaId = m.PortariaChegadaId,
            PorteiroChegadaId = m.PorteiroChegadaId,
            DataChegada = m.DataChegada,
            MotoristaId = m.MotoristaId,
            CarretaId = m.CarretaId,
            CavaloId = m.CavaloId,
            CarretaSegundaId = m.CarretaSegundaId,
            TransportadoraId = m.TransportadoraId,
            Motivo = m.Motivo,
            TipoCarga = m.TipoCarga,
            Destino = m.Destino,
            AutorizadoPorChegada = m.AutorizadoPorChegada,
            NumeroNFChegada = m.NumeroNFChegada,
            Produto = m.Produto,
            Setor = m.Setor,
            Observacao = m.Observacao,
            Estado = m.Estado,
            LiderQueAutorizouId = m.LiderQueAutorizouId,
            DataChamada = m.DataChamada,
            DataEntrada = m.DataEntrada,
            DataSaida = m.DataSaida,
            NumeroNFSaida = m.NumeroNFSaida,
            Lacre = m.Lacre,
            DestinoSaida = m.DestinoSaida
        });
    }

    [HttpGet("v1/{id:guid}/eventos")]
    [Authorize(Policy = PoliticasAuth.SupervisorOuMaior)]
    public async Task<List<EventoFluxoSaida>> ListarEventos(Guid id) => await _repositorio.ListarEventos(id);

    [HttpGet("v1/{id:guid}/anexos")]
    public async Task<List<AnexoSaida>> ListarAnexos(Guid id) => await _repositorio.ListarAnexos(id);

    [HttpGet("v1/buscar-por-placa/{carretaId:guid}/auto-fill")]
    public async Task<AutoFillPlacaSaida> AutoFill(Guid carretaId, [FromServices] WebApi.Core.Multitenant.IUnidadeContext unidade)
        => await _repositorio.ObterAutoFillPorPlaca(unidade.UnidadeIdObrigatoria(), carretaId);

    [HttpGet("v1/resumo-dia")]
    public async Task<ResumoDiaSaida> ResumoDia([FromServices] WebApi.Core.Multitenant.IUnidadeContext unidade)
        => await _repositorio.ResumoDia(unidade.UnidadeIdObrigatoria());
}
