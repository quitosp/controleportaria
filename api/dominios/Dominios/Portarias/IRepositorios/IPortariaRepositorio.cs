using Core.Data;
using Core.ObjetoDominio;
using Dominios.Portarias.Comandos.Saidas;
using Dominios.Portarias.Entidades;

namespace Dominios.Portarias.IRepositorios;

public interface IPortariaRepositorio : IRepository<Portaria>
{
    Portaria Salvar(Portaria entidade);
    void Alterar(Portaria entidade);
    Task<Portaria?> Existe(Guid id);
    Task<Portaria?> ObterPorNome(string valor, Guid? excluirId = null);
    Task<PagedResult<PortariaSaida>> Listar(int pageIndex, int pageSize, string? filter = null);
}
