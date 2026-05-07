using Core.ObjetoDominio;

namespace Dominios.Unidades.Entidades;

public class Unidade : Entity
{
    public Unidade(string nome, string? configuracaoEvolutionApiUrl, string? configuracaoEvolutionApiToken)
    {
        Nome = nome;
        ConfiguracaoEvolutionApiUrl = configuracaoEvolutionApiUrl;
        ConfiguracaoEvolutionApiToken = configuracaoEvolutionApiToken;
    }

    protected Unidade() { }

    public string Nome { get; private set; } = string.Empty;
    public string? ConfiguracaoEvolutionApiUrl { get; private set; }
    public string? ConfiguracaoEvolutionApiToken { get; private set; }

    public void Alterar(string nome, string? configuracaoEvolutionApiUrl, string? configuracaoEvolutionApiToken)
    {
        Nome = nome;
        ConfiguracaoEvolutionApiUrl = configuracaoEvolutionApiUrl;
        ConfiguracaoEvolutionApiToken = configuracaoEvolutionApiToken;
    }
}
