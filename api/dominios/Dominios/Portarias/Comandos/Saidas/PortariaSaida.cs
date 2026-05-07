namespace Dominios.Portarias.Comandos.Saidas;

public class PortariaSaida
{
    public Guid PortariaId { get; set; }
    public string Nome { get; set; } = string.Empty;
    public Guid UnidadeId { get; set; }
}
