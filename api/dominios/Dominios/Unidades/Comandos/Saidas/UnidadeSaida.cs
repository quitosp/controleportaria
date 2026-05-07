namespace Dominios.Unidades.Comandos.Saidas;

public class UnidadeSaida
{
    public Guid UnidadeId { get; set; }
    public string Nome { get; set; } = string.Empty;
    public string? ConfiguracaoEvolutionApiUrl { get; set; }

    private string? _configuracaoEvolutionApiToken;
    public string? ConfiguracaoEvolutionApiToken
    {
        get => Mascarar(_configuracaoEvolutionApiToken);
        set => _configuracaoEvolutionApiToken = value;
    }

    public bool TemTokenConfigurado => !string.IsNullOrEmpty(_configuracaoEvolutionApiToken);

    private static string? Mascarar(string? valor)
    {
        if (string.IsNullOrEmpty(valor)) return valor;
        if (valor.Length <= 4) return new string('*', valor.Length);
        return new string('*', valor.Length - 4) + valor[^4..];
    }
}
