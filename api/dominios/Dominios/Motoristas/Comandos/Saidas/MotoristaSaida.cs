namespace Dominios.Motoristas.Comandos.Saidas;

public class MotoristaSaida
{
    public Guid MotoristaId { get; set; }
    public string Nome { get; set; } = string.Empty;
    public string Cpf { get; set; } = string.Empty;
    public string Whatsapp { get; set; } = string.Empty;
    public string? Email { get; set; }
    public int Status { get; set; }
    public string? MotivoStatus { get; set; }
    public Guid UnidadeId { get; set; }
}
