using Core.Exeptions;
using Core.ObjetoDominio;

namespace Dominios.MovimentosPortaria.Entidades;

public enum MotivoEntrada { Carga = 0, Descarga = 1, Devolucao = 2, Outro = 3 }
public enum TipoCarga { Frigorificada = 0, Seca = 1, Container = 2, Lavador = 3, Outro = 4 }
public enum DestinoPateo { Interno = 0, Externo = 1, Lavador = 2 }
public enum EstadoMovimento
{
    NoPateoExterno = 0,
    ChamadoParaInterno = 1,
    NoPateoInterno = 2,
    NoLavador = 3,
    Saiu = 100,
    Cancelado = 200,
    Desistencia = 201
}

public class MovimentoPortaria : Entity
{
    public Guid UnidadeId { get; private set; }
    public Guid PortariaChegadaId { get; private set; }
    public string PorteiroChegadaId { get; private set; } = string.Empty;
    public DateTime DataChegada { get; private set; }
    public Guid MotoristaId { get; private set; }
    public Guid CarretaId { get; private set; }
    public Guid? CavaloId { get; private set; }
    public Guid? CarretaSegundaId { get; private set; }
    public Guid? TransportadoraId { get; private set; }
    public MotivoEntrada Motivo { get; private set; }
    public TipoCarga TipoCarga { get; private set; }
    public DestinoPateo Destino { get; private set; }
    public string? AutorizadoPorChegada { get; private set; }

    public string? NumeroNFChegada { get; private set; }
    public string? Produto { get; private set; }
    public string? Setor { get; private set; }
    public string? ContratoChegada { get; private set; }
    public string? NumeroContainerChegada { get; private set; }
    public string? Observacao { get; private set; }

    public EstadoMovimento Estado { get; private set; }

    public string? LiderQueAutorizouId { get; private set; }
    public DateTime? DataChamada { get; private set; }
    public string? PorteiroEntradaId { get; private set; }
    public DateTime? DataEntrada { get; private set; }
    public string? PorteiroSaidaId { get; private set; }
    public DateTime? DataSaida { get; private set; }

    public string? NumeroNFSaida { get; private set; }
    public string? Lacre { get; private set; }
    public string? DestinoSaida { get; private set; }
    public string? NumeroContainerSaida { get; private set; }
    public string? ContratoSaida { get; private set; }

    public uint RowVersion { get; private set; }

    private readonly List<EventoFluxo> _eventos = new();
    public IReadOnlyCollection<EventoFluxo> Eventos => _eventos;
    private readonly List<Anexo> _anexos = new();
    public IReadOnlyCollection<Anexo> Anexos => _anexos;
    private readonly List<NotificacaoPendente> _notificacoes = new();
    public IReadOnlyCollection<NotificacaoPendente> NotificacoesPendentes => _notificacoes;

    protected MovimentoPortaria() { }

    public MovimentoPortaria(
        Guid unidadeId,
        Guid portariaChegadaId,
        string porteiroChegadaId,
        DateTime dataChegada,
        Guid motoristaId,
        Guid carretaId,
        Guid? cavaloId,
        Guid? carretaSegundaId,
        Guid? transportadoraId,
        MotivoEntrada motivo,
        TipoCarga tipoCarga,
        DestinoPateo destino,
        string? autorizadoPorChegada,
        string? numeroNFChegada,
        string? produto,
        string? setor,
        string? contratoChegada,
        string? numeroContainerChegada,
        string? observacao)
    {
        UnidadeId = unidadeId;
        PortariaChegadaId = portariaChegadaId;
        PorteiroChegadaId = porteiroChegadaId;
        DataChegada = dataChegada;
        MotoristaId = motoristaId;
        CarretaId = carretaId;
        CavaloId = cavaloId;
        CarretaSegundaId = carretaSegundaId;
        TransportadoraId = transportadoraId;
        Motivo = motivo;
        TipoCarga = tipoCarga;
        Destino = destino;
        AutorizadoPorChegada = autorizadoPorChegada;
        NumeroNFChegada = numeroNFChegada;
        Produto = produto;
        Setor = setor;
        ContratoChegada = contratoChegada;
        NumeroContainerChegada = numeroContainerChegada;
        Observacao = observacao;

        // RN-003 — Destino Patio Interno na chegada exige AutorizadoPor
        if (destino == DestinoPateo.Interno && string.IsNullOrWhiteSpace(autorizadoPorChegada))
            throw new DominioException("AutorizadoPor obrigatorio quando destino e Interno.");

        Estado = destino switch
        {
            DestinoPateo.Externo => EstadoMovimento.NoPateoExterno,
            DestinoPateo.Interno => EstadoMovimento.NoPateoInterno,
            DestinoPateo.Lavador => EstadoMovimento.NoLavador,
            _ => EstadoMovimento.NoPateoExterno
        };

        RegistrarEvento(TipoEventoFluxo.ChegadaRegistrada, null, Estado, porteiroChegadaId, observacao);
    }

    // RN-008 maquina de estados sem pulos | RN-011 chamar dispara notificacoes
    public void Chamar(string liderId, DateTime quando)
    {
        if (Estado != EstadoMovimento.NoPateoExterno)
            throw new DominioException($"Transicao invalida {Estado} -> ChamadoParaInterno");
        var anterior = Estado;
        Estado = EstadoMovimento.ChamadoParaInterno;
        LiderQueAutorizouId = liderId;
        DataChamada = quando;
        RegistrarEvento(TipoEventoFluxo.ChamadaAutorizada, anterior, Estado, liderId);
    }

    // RN-020 TTL 30min recancelamento volta para NoPateoExterno
    public void RecancelarChamada(string liderId)
    {
        if (Estado != EstadoMovimento.ChamadoParaInterno)
            throw new DominioException($"Transicao invalida {Estado} -> NoPateoExterno (recancelar)");
        var anterior = Estado;
        Estado = EstadoMovimento.NoPateoExterno;
        RegistrarEvento(TipoEventoFluxo.ChamadaExpirada, anterior, Estado, liderId);
    }

    public void ConfirmarEntrada(string porteiroId, DateTime quando)
    {
        if (Estado != EstadoMovimento.ChamadoParaInterno)
            throw new DominioException($"Transicao invalida {Estado} -> NoPateoInterno");
        var anterior = Estado;
        Estado = EstadoMovimento.NoPateoInterno;
        PorteiroEntradaId = porteiroId;
        DataEntrada = quando;
        RegistrarEvento(TipoEventoFluxo.EntradaConfirmada, anterior, Estado, porteiroId);
    }

    // RN-005/RN-006/RN-007 saida condicional
    public void RegistrarSaida(
        string porteiroId,
        DateTime quando,
        string? numeroNF,
        string? lacre,
        string? destinoSaida,
        string? numeroContainer,
        string? contrato)
    {
        if (Estado != EstadoMovimento.NoPateoInterno && Estado != EstadoMovimento.NoLavador)
            throw new DominioException($"Transicao invalida {Estado} -> Saiu");

        var faltantes = new List<string>();
        if (Motivo == MotivoEntrada.Carga)
        {
            if (string.IsNullOrWhiteSpace(numeroNF)) faltantes.Add("NumeroNF");
            if (string.IsNullOrWhiteSpace(lacre)) faltantes.Add("Lacre");
            if (string.IsNullOrWhiteSpace(destinoSaida)) faltantes.Add("Destino");
            if (TipoCarga == TipoCarga.Container)
            {
                if (string.IsNullOrWhiteSpace(numeroContainer)) faltantes.Add("NumeroContainer");
                if (string.IsNullOrWhiteSpace(contrato)) faltantes.Add("Contrato");
            }
        }
        if (faltantes.Count > 0)
            throw new DominioException("Campos obrigatorios na saida: " + string.Join(", ", faltantes));

        var anterior = Estado;
        Estado = EstadoMovimento.Saiu;
        PorteiroSaidaId = porteiroId;
        DataSaida = quando;
        NumeroNFSaida = numeroNF;
        Lacre = lacre;
        DestinoSaida = destinoSaida;
        NumeroContainerSaida = numeroContainer;
        ContratoSaida = contrato;
        RegistrarEvento(TipoEventoFluxo.SaidaRegistrada, anterior, Estado, porteiroId);
    }

    // RN-008/RN-009 cancel/desistir exige observacao
    public void Cancelar(string usuarioId, string observacao)
    {
        if (EstadoFinalizado())
            throw new DominioException($"Movimento ja finalizado ({Estado})");
        if (string.IsNullOrWhiteSpace(observacao))
            throw new DominioException("Observacao obrigatoria no cancelamento.");
        var anterior = Estado;
        Estado = EstadoMovimento.Cancelado;
        Observacao = observacao;
        RegistrarEvento(TipoEventoFluxo.Cancelamento, anterior, Estado, usuarioId, observacao);
    }

    public void Desistir(string usuarioId, string observacao)
    {
        if (EstadoFinalizado())
            throw new DominioException($"Movimento ja finalizado ({Estado})");
        if (string.IsNullOrWhiteSpace(observacao))
            throw new DominioException("Observacao obrigatoria na desistencia.");
        var anterior = Estado;
        Estado = EstadoMovimento.Desistencia;
        Observacao = observacao;
        RegistrarEvento(TipoEventoFluxo.Desistencia, anterior, Estado, usuarioId, observacao);
    }

    private bool EstadoFinalizado()
        => Estado == EstadoMovimento.Saiu || Estado == EstadoMovimento.Cancelado || Estado == EstadoMovimento.Desistencia;

    // RN-004 auditoria de alerta de bloqueio
    public void RegistrarAlertaBloqueioMotorista(string usuarioId, string motivo)
        => RegistrarEvento(TipoEventoFluxo.AlertaBloqueio, Estado, Estado, usuarioId, motivo);

    // RN-021 auditoria de edicao de campo
    public void RegistrarEdicaoCampo(string usuarioId, string campo, string? antes, string? depois)
        => RegistrarEvento(TipoEventoFluxo.EdicaoCampo, Estado, Estado, usuarioId, $"{campo}: {antes} -> {depois}");

    // RN-016 anexos
    public Anexo AdicionarAnexo(EstagioAnexo estagio, string url, long tamanhoBytes, string contentType, string usuarioId)
    {
        var a = new Anexo
        {
            Id = Guid.NewGuid(),
            MovimentoPortariaId = Id,
            Estagio = estagio,
            Url = url,
            TamanhoBytes = tamanhoBytes,
            ContentType = contentType,
            UsuarioUploadId = usuarioId,
            Quando = DateTime.UtcNow
        };
        _anexos.Add(a);
        return a;
    }

    // RN-011/RN-017 notificacao na mesma transacao
    public void EnfileirarNotificacao(CanalNotificacao canal, string destino, string payload)
    {
        _notificacoes.Add(new NotificacaoPendente
        {
            Id = Guid.NewGuid(),
            MovimentoPortariaId = Id,
            Canal = canal,
            Destino = destino,
            Payload = payload,
            Status = StatusNotificacao.Pendente,
            Tentativas = 0,
            ProximaTentativa = DateTime.UtcNow
        });
    }

    public void AlterarCamposComuns(
        Guid? cavaloId,
        Guid? carretaSegundaId,
        Guid? transportadoraId,
        string? numeroNFChegada,
        string? produto,
        string? setor,
        string? contratoChegada,
        string? numeroContainerChegada,
        string? observacao,
        string usuarioId)
    {
        if (CavaloId != cavaloId) RegistrarEdicaoCampo(usuarioId, nameof(CavaloId), CavaloId?.ToString(), cavaloId?.ToString());
        if (CarretaSegundaId != carretaSegundaId) RegistrarEdicaoCampo(usuarioId, nameof(CarretaSegundaId), CarretaSegundaId?.ToString(), carretaSegundaId?.ToString());
        if (TransportadoraId != transportadoraId) RegistrarEdicaoCampo(usuarioId, nameof(TransportadoraId), TransportadoraId?.ToString(), transportadoraId?.ToString());
        if (NumeroNFChegada != numeroNFChegada) RegistrarEdicaoCampo(usuarioId, nameof(NumeroNFChegada), NumeroNFChegada, numeroNFChegada);
        if (Produto != produto) RegistrarEdicaoCampo(usuarioId, nameof(Produto), Produto, produto);
        if (Setor != setor) RegistrarEdicaoCampo(usuarioId, nameof(Setor), Setor, setor);
        if (ContratoChegada != contratoChegada) RegistrarEdicaoCampo(usuarioId, nameof(ContratoChegada), ContratoChegada, contratoChegada);
        if (NumeroContainerChegada != numeroContainerChegada) RegistrarEdicaoCampo(usuarioId, nameof(NumeroContainerChegada), NumeroContainerChegada, numeroContainerChegada);
        if (Observacao != observacao) RegistrarEdicaoCampo(usuarioId, nameof(Observacao), Observacao, observacao);

        CavaloId = cavaloId;
        CarretaSegundaId = carretaSegundaId;
        TransportadoraId = transportadoraId;
        NumeroNFChegada = numeroNFChegada;
        Produto = produto;
        Setor = setor;
        ContratoChegada = contratoChegada;
        NumeroContainerChegada = numeroContainerChegada;
        Observacao = observacao;
    }

    // RN-021 — campos criticos exigem Lider+ pos-NoPateoInterno (validacao no handler)
    public void AlterarCamposCriticos(
        Guid? carretaId,
        Guid? motoristaId,
        MotivoEntrada? motivo,
        string usuarioId)
    {
        if (carretaId.HasValue && CarretaId != carretaId.Value)
        {
            RegistrarEdicaoCampo(usuarioId, nameof(CarretaId), CarretaId.ToString(), carretaId.ToString());
            CarretaId = carretaId.Value;
        }
        if (motoristaId.HasValue && MotoristaId != motoristaId.Value)
        {
            RegistrarEdicaoCampo(usuarioId, nameof(MotoristaId), MotoristaId.ToString(), motoristaId.ToString());
            MotoristaId = motoristaId.Value;
        }
        if (motivo.HasValue && Motivo != motivo.Value)
        {
            RegistrarEdicaoCampo(usuarioId, nameof(Motivo), Motivo.ToString(), motivo.ToString());
            Motivo = motivo.Value;
        }
    }

    private void RegistrarEvento(TipoEventoFluxo tipo, EstadoMovimento? de, EstadoMovimento? para, string usuarioId, string? detalhes = null)
    {
        // RN-002 registro automatico Usuario+Timestamp | RN-015 auditoria imutavel
        _eventos.Add(new EventoFluxo
        {
            Id = Guid.NewGuid(),
            MovimentoPortariaId = Id,
            Tipo = tipo,
            DeEstado = de,
            ParaEstado = para,
            UsuarioId = usuarioId,
            Quando = DateTime.UtcNow,
            Detalhes = detalhes
        });
    }
}
