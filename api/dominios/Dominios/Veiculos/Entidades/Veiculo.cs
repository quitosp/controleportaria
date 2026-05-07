using Core.ObjetoDominio;

namespace Dominios.Veiculos.Entidades;

public class Veiculo : Entity
{
    public Veiculo(string nome, string placa, int tipo, Guid? transportadoraId, Guid unidadeId)
    {
        Nome = nome;
        Placa = placa;
        Tipo = tipo;
        TransportadoraId = transportadoraId;
        UnidadeId = unidadeId;
    }

    protected Veiculo() { }

    public string Nome { get; private set; } = string.Empty;
    public string Placa { get; private set; } = string.Empty;
    public int Tipo { get; private set; }
    public Guid? TransportadoraId { get; private set; }
    public Guid UnidadeId { get; private set; }

    public void Alterar(string nome, string placa, int tipo, Guid? transportadoraId, Guid unidadeId)
    {
        Nome = nome;
        Placa = placa;
        Tipo = tipo;
        TransportadoraId = transportadoraId;
        UnidadeId = unidadeId;
    }
}
