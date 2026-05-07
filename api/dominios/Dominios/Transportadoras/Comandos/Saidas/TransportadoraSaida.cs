namespace Dominios.Transportadoras.Comandos.Saidas;

public class TransportadoraSaida
{
    public Guid TransportadoraId { get; set; }
    public string Nome { get; set; } = string.Empty;
    public string RazaoSocial { get; set; } = string.Empty;
    public string Cnpj { get; set; } = string.Empty;
    public Guid UnidadeId { get; set; }
}
