using Core.Data;
using Core.ObjetoDominio;
using Dominios.Motoristas.Comandos.Saidas;
using Dominios.Motoristas.Entidades;

namespace Dominios.Motoristas.IRepositorios;

public interface IMotoristaRepositorio : IRepository<Motorista>
{
    Motorista Salvar(Motorista entidade);
    void Alterar(Motorista entidade);
    Task<Motorista?> Existe(Guid id);
    Task<Motorista?> ObterPorId(Guid id);
    Task<Motorista?> ObterPorNome(string valor, Guid? excluirId = null);
    Task<Motorista?> ObterPorCpf(string valor, Guid? excluirId = null);
    Task<PagedResult<MotoristaSaida>> Listar(int pageIndex, int pageSize, string? filter = null);
}
