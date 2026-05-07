namespace Dominios.MovimentosPortaria.Entidades;

public enum EstagioAnexo { Chegada = 0, Entrada = 1, Saida = 2 }

public class Anexo
{
    public Guid Id { get; set; }
    public Guid MovimentoPortariaId { get; set; }
    public EstagioAnexo Estagio { get; set; }
    public string Url { get; set; } = string.Empty;
    public long TamanhoBytes { get; set; }
    public string ContentType { get; set; } = string.Empty;
    public string UsuarioUploadId { get; set; } = string.Empty;
    public DateTime Quando { get; set; }
}
