namespace Dominios.MovimentosPortaria.Entidades;

public enum TipoEventoFluxo
{
    ChegadaRegistrada = 0,
    AlertaBloqueio = 1,
    ChamadaAutorizada = 2,
    ChamadaExpirada = 3,
    EntradaConfirmada = 4,
    SaidaRegistrada = 5,
    Cancelamento = 6,
    Desistencia = 7,
    EdicaoCampo = 8
}

public class EventoFluxo
{
    public Guid Id { get; set; }
    public Guid MovimentoPortariaId { get; set; }
    public TipoEventoFluxo Tipo { get; set; }
    public EstadoMovimento? DeEstado { get; set; }
    public EstadoMovimento? ParaEstado { get; set; }
    public string UsuarioId { get; set; } = string.Empty;
    public DateTime Quando { get; set; }
    public string? Detalhes { get; set; }
}
