using Core.ObjetoDominio;

namespace Dominios.Portarias.Entidades;

public class Portaria : Entity
{
    public Portaria(string nome, Guid unidadeId)
    {
        Nome = nome;
        UnidadeId = unidadeId;
    }

    protected Portaria() { }

    public string Nome { get; private set; } = string.Empty;
    public Guid UnidadeId { get; private set; }

    public void Alterar(string nome, Guid unidadeId)
    {
        Nome = nome;
        UnidadeId = unidadeId;
    }
}
