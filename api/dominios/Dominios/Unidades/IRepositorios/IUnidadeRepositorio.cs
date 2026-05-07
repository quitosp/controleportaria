using Core.Data;
using Core.ObjetoDominio;
using Dominios.Unidades.Comandos.Saidas;
using Dominios.Unidades.Entidades;

namespace Dominios.Unidades.IRepositorios;

public interface IUnidadeRepositorio : IRepository<Unidade>
{
    Unidade Salvar(Unidade entidade);
    void Alterar(Unidade entidade);
    Task<Unidade?> Existe(Guid id);
    Task<Unidade?> ObterPorNome(string valor, Guid? excluirId = null);
    Task<PagedResult<UnidadeSaida>> Listar(int pageIndex, int pageSize, string? filter = null);
}
