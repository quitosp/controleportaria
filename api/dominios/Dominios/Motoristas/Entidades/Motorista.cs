using Core.ObjetoDominio;

namespace Dominios.Motoristas.Entidades;

public class Motorista : Entity
{
    public Motorista(string nome, string cpf, string whatsapp, string? email, int status, string? motivoStatus, Guid unidadeId)
    {
        Nome = nome;
        Cpf = cpf;
        Whatsapp = whatsapp;
        Email = email;
        Status = status;
        MotivoStatus = motivoStatus;
        UnidadeId = unidadeId;
    }

    protected Motorista() { }

    public string Nome { get; private set; } = string.Empty;
    public string Cpf { get; private set; } = string.Empty;
    public string Whatsapp { get; private set; } = string.Empty;
    public string? Email { get; private set; }
    public int Status { get; private set; }
    public string? MotivoStatus { get; private set; }
    public Guid UnidadeId { get; private set; }

    public void Alterar(string nome, string cpf, string whatsapp, string? email, int status, string? motivoStatus, Guid unidadeId)
    {
        Nome = nome;
        Cpf = cpf;
        Whatsapp = whatsapp;
        Email = email;
        Status = status;
        MotivoStatus = motivoStatus;
        UnidadeId = unidadeId;
    }
}
