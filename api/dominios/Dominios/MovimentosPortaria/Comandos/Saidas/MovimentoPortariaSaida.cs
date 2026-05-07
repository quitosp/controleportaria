using Dominios.MovimentosPortaria.Entidades;

namespace Dominios.MovimentosPortaria.Comandos.Saidas;

public class MovimentoPortariaSaida
{
    public Guid MovimentoPortariaId { get; set; }
    public Guid UnidadeId { get; set; }
    public Guid PortariaChegadaId { get; set; }
    public string? PorteiroChegadaId { get; set; }
    public DateTime DataChegada { get; set; }
    public Guid MotoristaId { get; set; }
    public Guid CarretaId { get; set; }
    public Guid? CavaloId { get; set; }
    public Guid? CarretaSegundaId { get; set; }
    public Guid? TransportadoraId { get; set; }
    public MotivoEntrada Motivo { get; set; }
    public TipoCarga TipoCarga { get; set; }
    public DestinoPateo Destino { get; set; }
    public string? AutorizadoPorChegada { get; set; }
    public string? NumeroNFChegada { get; set; }
    public string? Produto { get; set; }
    public string? Setor { get; set; }
    public string? Observacao { get; set; }
    public EstadoMovimento Estado { get; set; }
    public string? LiderQueAutorizouId { get; set; }
    public DateTime? DataChamada { get; set; }
    public DateTime? DataEntrada { get; set; }
    public DateTime? DataSaida { get; set; }
    public string? NumeroNFSaida { get; set; }
    public string? Lacre { get; set; }
    public string? DestinoSaida { get; set; }
}

public class PainelChamadaItemSaida
{
    public Guid MovimentoPortariaId { get; set; }
    public Guid PortariaChegadaId { get; set; }
    public Guid CarretaId { get; set; }
    public Guid? TransportadoraId { get; set; }
    public Guid MotoristaId { get; set; }
    public MotivoEntrada Motivo { get; set; }
    public TipoCarga TipoCarga { get; set; }
    public string? Produto { get; set; }
    public string? Setor { get; set; }
    public DateTime DataChegada { get; set; }
    public int MinutosEspera { get; set; }
    public bool ChamadaExpirada { get; set; }
    public EstadoMovimento Estado { get; set; }
}

public class EventoFluxoSaida
{
    public Guid Id { get; set; }
    public TipoEventoFluxo Tipo { get; set; }
    public EstadoMovimento? DeEstado { get; set; }
    public EstadoMovimento? ParaEstado { get; set; }
    public string UsuarioId { get; set; } = string.Empty;
    public DateTime Quando { get; set; }
    public string? Detalhes { get; set; }
}

public class AnexoSaida
{
    public Guid Id { get; set; }
    public EstagioAnexo Estagio { get; set; }
    public string Url { get; set; } = string.Empty;
    public string ContentType { get; set; } = string.Empty;
    public long TamanhoBytes { get; set; }
    public DateTime Quando { get; set; }
}

public class AutoFillPlacaSaida
{
    public Guid? TransportadoraId { get; set; }
    public TipoCarga? TipoCargaSugerida { get; set; }
    public bool TemHistorico => TransportadoraId.HasValue || TipoCargaSugerida.HasValue;
}

public class ResumoDiaSaida
{
    public int NoPateoExterno { get; set; }
    public int NoPateoInterno { get; set; }
    public int SaiuHoje { get; set; }
    public int CanceladosHoje { get; set; }
    public int Total { get; set; }
}
