using Core.Data;
using Core.ObjetoDominio;
using Dominios.Veiculos.Comandos.Saidas;
using Dominios.Veiculos.Entidades;

namespace Dominios.Veiculos.IRepositorios;

public interface IVeiculoRepositorio : IRepository<Veiculo>
{
    Veiculo Salvar(Veiculo entidade);
    void Alterar(Veiculo entidade);
    Task<Veiculo?> Existe(Guid id);
    Task<Veiculo?> ObterPorNome(string valor, Guid? excluirId = null);
    Task<Veiculo?> ObterPorPlaca(string valor, Guid? excluirId = null);
    Task<PagedResult<VeiculoSaida>> Listar(int pageIndex, int pageSize, string? filter = null);
}
