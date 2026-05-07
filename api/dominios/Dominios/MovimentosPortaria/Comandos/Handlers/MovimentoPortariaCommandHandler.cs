using Core.Exeptions;
using Core.Mensagens;
using Core.ObjetoDominio;
using Dominios.MovimentosPortaria.Comandos.Entradas;
using Dominios.MovimentosPortaria.Entidades;
using Dominios.MovimentosPortaria.IRepositorios;
using Dominios.MovimentosPortaria.Servicos;
using Dominios.Motoristas.IRepositorios;
using MediatR;
using Microsoft.EntityFrameworkCore;
using WebApi.Core.Multitenant;
using WebApi.Core.Usuario;

namespace Dominios.MovimentosPortaria.Comandos.Handlers;

public class MovimentoPortariaCommandHandler : CommandHandler,
    IRequestHandler<CadastrarChegadaEntrada, ComandResult>,
    IRequestHandler<ChamarVeiculoEntrada, ComandResult>,
    IRequestHandler<RecancelarChamadaEntrada, ComandResult>,
    IRequestHandler<ConfirmarEntradaEntrada, ComandResult>,
    IRequestHandler<RegistrarSaidaEntrada, ComandResult>,
    IRequestHandler<CancelarMovimentoEntrada, ComandResult>,
    IRequestHandler<DesistirMovimentoEntrada, ComandResult>,
    IRequestHandler<AlterarMovimentoEntrada, ComandResult>,
    IRequestHandler<AnexarArquivoEntrada, ComandResult>
{
    private readonly IMovimentoPortariaRepositorio _movimentos;
    private readonly IMotoristaRepositorio _motoristas;
    private readonly IUnidadeContext _unidade;
    private readonly IAspNetUser _usuario;
    private readonly INotificacoesPortariaService _notificacoes;
    private readonly IAnexoStorage _anexoStorage;

    public MovimentoPortariaCommandHandler(
        IMovimentoPortariaRepositorio movimentos,
        IMotoristaRepositorio motoristas,
        IUnidadeContext unidade,
        IAspNetUser usuario,
        INotificacoesPortariaService notificacoes,
        IAnexoStorage anexoStorage)
    {
        _movimentos = movimentos;
        _motoristas = motoristas;
        _unidade = unidade;
        _usuario = usuario;
        _notificacoes = notificacoes;
        _anexoStorage = anexoStorage;
    }

    // === HIST-010 — Cadastrar chegada ===
    public async Task<ComandResult> Handle(CadastrarChegadaEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        var unidadeId = _unidade.UnidadeIdObrigatoria(); // RN-014
        var porteiroId = _usuario.ObterUserId().ToString(); // RN-002

        // RN-012 — carreta com movimento aberto bloqueia nova chegada
        var aberto = await _movimentos.ObterCarretaComMovimentoAberto(unidadeId, msg.CarretaId);
        if (aberto != null)
            return new ComandResult(false, $"Carreta com movimento aberto (Id={aberto.Id}, Estado={aberto.Estado}). Resolva-o antes.", new List<string>(), 409);

        // RN-004 — Motorista bloqueado: alerta + observacao obrigatoria
        var motorista = await _motoristas.ObterPorId(msg.MotoristaId);
        if (motorista == null)
            return new ComandResult(false, "Motorista nao encontrado", new List<string>(), 404);

        var bloqueado = motorista.Status == 2; // 2 = Bloqueado
        if (bloqueado && string.IsNullOrWhiteSpace(msg.Observacao))
            return new ComandResult(false, "Motorista bloqueado: observacao obrigatoria.", new List<string>(), 400);

        try
        {
            var movimento = new MovimentoPortaria(
                unidadeId,
                msg.PortariaChegadaId,
                porteiroId,
                DateTime.UtcNow,
                msg.MotoristaId,
                msg.CarretaId,
                msg.CavaloId,
                msg.CarretaSegundaId,
                msg.TransportadoraId,
                msg.Motivo,
                msg.TipoCarga,
                msg.Destino,
                msg.AutorizadoPorChegada,
                msg.NumeroNFChegada, // RN-018 NF opcional na chegada
                msg.Produto,
                msg.Setor,
                msg.ContratoChegada,
                msg.NumeroContainerChegada,
                msg.Observacao);

            // RN-004 evento de alerta
            if (bloqueado)
                movimento.RegistrarAlertaBloqueioMotorista(porteiroId, motorista.MotivoStatus ?? "Bloqueado");

            _movimentos.Salvar(movimento);
            return await PersistirDados(_movimentos.UnitOfWork, "Chegada registrada com sucesso!", new { id = movimento.Id, estado = movimento.Estado.ToString() });
        }
        catch (DominioException ex)
        {
            return new ComandResult(false, ex.Message, new List<string>(), 400);
        }
    }

    // === HIST-011 — Chamar veiculo ===
    public async Task<ComandResult> Handle(ChamarVeiculoEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        var liderId = _usuario.ObterUserId().ToString();
        var movimento = await _movimentos.ObterPorId(msg.MovimentoPortariaId);
        if (movimento == null)
            return new ComandResult(false, "Movimento nao encontrado", new List<string>(), 404);

        try
        {
            // RN-013 — lock otimista (RowVersion) sera tratado pelo SaveChanges
            movimento.Chamar(liderId, DateTime.UtcNow);

            // RN-011/RN-017 — enfileira notificacoes (assincronas, nao bloqueiam)
            var motorista = await _motoristas.ObterPorId(movimento.MotoristaId);
            if (motorista != null)
            {
                _notificacoes.EnfileirarChamadaParaMotorista(movimento, motorista);
            }
            _notificacoes.NotificarPortariaViaSocket(movimento);

            _movimentos.Alterar(movimento);
            return await PersistirDados(_movimentos.UnitOfWork, "Veiculo chamado.", new { id = movimento.Id });
        }
        catch (DbUpdateConcurrencyException)
        {
            return new ComandResult(false, "Movimento ja liberado por outro usuario.", new List<string>(), 409);
        }
        catch (DominioException ex)
        {
            return new ComandResult(false, ex.Message, new List<string>(), 400);
        }
    }

    // === HIST-012 — Recancelar chamada ===
    public async Task<ComandResult> Handle(RecancelarChamadaEntrada msg, CancellationToken ct)
    {
        var liderId = _usuario.ObterUserId().ToString();
        var movimento = await _movimentos.ObterPorId(msg.MovimentoPortariaId);
        if (movimento == null) return new ComandResult(false, "Movimento nao encontrado", new List<string>(), 404);
        try { movimento.RecancelarChamada(liderId); }
        catch (DominioException ex) { return new ComandResult(false, ex.Message, new List<string>(), 400); }
        _movimentos.Alterar(movimento);
        return await PersistirDados(_movimentos.UnitOfWork, "Chamada recancelada.", new { id = movimento.Id });
    }

    // === HIST-013 — Confirmar entrada ===
    public async Task<ComandResult> Handle(ConfirmarEntradaEntrada msg, CancellationToken ct)
    {
        var porteiroId = _usuario.ObterUserId().ToString();
        var movimento = await _movimentos.ObterPorId(msg.MovimentoPortariaId);
        if (movimento == null) return new ComandResult(false, "Movimento nao encontrado", new List<string>(), 404);
        try { movimento.ConfirmarEntrada(porteiroId, DateTime.UtcNow); }
        catch (DominioException ex) { return new ComandResult(false, ex.Message, new List<string>(), 400); }
        _movimentos.Alterar(movimento);
        return await PersistirDados(_movimentos.UnitOfWork, "Entrada confirmada.", new { id = movimento.Id });
    }

    // === HIST-014 — Registrar saida ===
    public async Task<ComandResult> Handle(RegistrarSaidaEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        var porteiroId = _usuario.ObterUserId().ToString();
        var movimento = await _movimentos.ObterPorId(msg.MovimentoPortariaId);
        if (movimento == null) return new ComandResult(false, "Movimento nao encontrado", new List<string>(), 404);
        try
        {
            movimento.RegistrarSaida(porteiroId, DateTime.UtcNow,
                msg.NumeroNF, msg.Lacre, msg.Destino, msg.NumeroContainer, msg.Contrato);
        }
        catch (DominioException ex) { return new ComandResult(false, ex.Message, new List<string>(), 400); }
        _movimentos.Alterar(movimento);
        return await PersistirDados(_movimentos.UnitOfWork, "Saida registrada.", new { id = movimento.Id });
    }

    // === HIST-015 — Cancelar ===
    public async Task<ComandResult> Handle(CancelarMovimentoEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        var usuarioId = _usuario.ObterUserId().ToString();
        var movimento = await _movimentos.ObterPorId(msg.MovimentoPortariaId);
        if (movimento == null) return new ComandResult(false, "Movimento nao encontrado", new List<string>(), 404);
        try { movimento.Cancelar(usuarioId, msg.Observacao); }
        catch (DominioException ex) { return new ComandResult(false, ex.Message, new List<string>(), 400); }
        _movimentos.Alterar(movimento);
        return await PersistirDados(_movimentos.UnitOfWork, "Movimento cancelado.", new { id = movimento.Id });
    }

    // === HIST-016 — Desistir ===
    public async Task<ComandResult> Handle(DesistirMovimentoEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        var usuarioId = _usuario.ObterUserId().ToString();
        var movimento = await _movimentos.ObterPorId(msg.MovimentoPortariaId);
        if (movimento == null) return new ComandResult(false, "Movimento nao encontrado", new List<string>(), 404);
        try { movimento.Desistir(usuarioId, msg.Observacao); }
        catch (DominioException ex) { return new ComandResult(false, ex.Message, new List<string>(), 400); }
        _movimentos.Alterar(movimento);
        return await PersistirDados(_movimentos.UnitOfWork, "Desistencia registrada.", new { id = movimento.Id });
    }

    // === HIST-017 — Editar com auditoria ===
    public async Task<ComandResult> Handle(AlterarMovimentoEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        var usuarioId = _usuario.ObterUserId().ToString();
        var papel = _unidade.Papel;
        var movimento = await _movimentos.ObterPorId(msg.MovimentoPortariaId);
        if (movimento == null) return new ComandResult(false, "Movimento nao encontrado", new List<string>(), 404);

        // RN-021 — campos criticos pos-NoPateoInterno exigem Lider+
        var alterouCriticos = msg.CarretaId.HasValue || msg.MotoristaId.HasValue || msg.Motivo.HasValue;
        var posInterno = movimento.Estado == EstadoMovimento.NoPateoInterno
                         || movimento.Estado == EstadoMovimento.NoLavador
                         || movimento.Estado == EstadoMovimento.Saiu;
        if (alterouCriticos && posInterno && !PapelEhLiderOuMaior(papel))
            return new ComandResult(false, "Apenas Lider ou superior pode alterar campos criticos pos-entrada.", new List<string>(), 403);

        movimento.AlterarCamposComuns(
            msg.CavaloId, msg.CarretaSegundaId, msg.TransportadoraId,
            msg.NumeroNFChegada, msg.Produto, msg.Setor,
            msg.ContratoChegada, msg.NumeroContainerChegada, msg.Observacao,
            usuarioId);

        movimento.AlterarCamposCriticos(msg.CarretaId, msg.MotoristaId, msg.Motivo, usuarioId);

        _movimentos.Alterar(movimento);
        return await PersistirDados(_movimentos.UnitOfWork, "Movimento alterado.", new { id = movimento.Id });
    }

    private static bool PapelEhLiderOuMaior(string? papel)
        => papel == "Lider" || papel == "Supervisor" || papel == "Admin";

    // === HIST-018 — Anexar arquivo ===
    public async Task<ComandResult> Handle(AnexarArquivoEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        var usuarioId = _usuario.ObterUserId().ToString();
        var movimento = await _movimentos.ObterPorId(msg.MovimentoPortariaId);
        if (movimento == null) return new ComandResult(false, "Movimento nao encontrado", new List<string>(), 404);

        var url = await _anexoStorage.Salvar(movimento.UnidadeId, movimento.Id, msg.NomeArquivo, msg.Conteudo);
        movimento.AdicionarAnexo(msg.Estagio, url, msg.Conteudo.LongLength, msg.ContentType, usuarioId);

        _movimentos.Alterar(movimento);
        return await PersistirDados(_movimentos.UnitOfWork, "Anexo salvo.", new { url });
    }
}

