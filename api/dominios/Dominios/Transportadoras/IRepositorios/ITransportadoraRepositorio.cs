using Core.Data;
using Core.ObjetoDominio;
using Dominios.Transportadoras.Comandos.Saidas;
using Dominios.Transportadoras.Entidades;

namespace Dominios.Transportadoras.IRepositorios;

public interface ITransportadoraRepositorio : IRepository<Transportadora>
{
    Transportadora Salvar(Transportadora entidade);
    void Alterar(Transportadora entidade);
    Task<Transportadora?> Existe(Guid id);
    Task<Transportadora?> ObterPorNome(string valor, Guid? excluirId = null);
    Task<Transportadora?> ObterPorCnpj(string valor, Guid? excluirId = null);
    Task<PagedResult<TransportadoraSaida>> Listar(int pageIndex, int pageSize, string? filter = null);
}
