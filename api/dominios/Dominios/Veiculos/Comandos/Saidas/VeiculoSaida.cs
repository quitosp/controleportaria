namespace Dominios.Veiculos.Comandos.Saidas;

public class VeiculoSaida
{
    public Guid VeiculoId { get; set; }
    public string Nome { get; set; } = string.Empty;
    public string Placa { get; set; } = string.Empty;
    public int Tipo { get; set; }
    public Guid? TransportadoraId { get; set; }
    public Guid UnidadeId { get; set; }
}
