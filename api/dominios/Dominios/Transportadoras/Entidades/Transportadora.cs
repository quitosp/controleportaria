using Core.ObjetoDominio;

namespace Dominios.Transportadoras.Entidades;

public class Transportadora : Entity
{
    public Transportadora(string nome, string razaoSocial, string cnpj, Guid unidadeId)
    {
        Nome = nome;
        RazaoSocial = razaoSocial;
        Cnpj = cnpj;
        UnidadeId = unidadeId;
    }

    protected Transportadora() { }

    public string Nome { get; private set; } = string.Empty;
    public string RazaoSocial { get; private set; } = string.Empty;
    public string Cnpj { get; private set; } = string.Empty;
    public Guid UnidadeId { get; private set; }

    public void Alterar(string nome, string razaoSocial, string cnpj, Guid unidadeId)
    {
        Nome = nome;
        RazaoSocial = razaoSocial;
        Cnpj = cnpj;
        UnidadeId = unidadeId;
    }
}
