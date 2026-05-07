using Core.Data;
using Core.ObjetoDominio;
using Dominios.MovimentosPortaria.Comandos.Saidas;
using Dominios.MovimentosPortaria.Entidades;

namespace Dominios.MovimentosPortaria.IRepositorios;

public interface IMovimentoPortariaRepositorio : IRepository<MovimentoPortaria>
{
    void Salvar(MovimentoPortaria entidade);
    void Alterar(MovimentoPortaria entidade);
    Task<MovimentoPortaria?> ObterPorId(Guid id);
    Task<MovimentoPortaria?> ObterCarretaComMovimentoAberto(Guid unidadeId, Guid carretaId);
    Task<AutoFillPlacaSaida> ObterAutoFillPorPlaca(Guid unidadeId, Guid carretaId);
    Task<PagedResult<MovimentoPortariaSaida>> Listar(int pageIndex, int pageSize, string? filter = null);
    Task<List<PainelChamadaItemSaida>> ListarPainelChamada(Guid unidadeId, int ttlMinutos);
    Task<List<EventoFluxoSaida>> ListarEventos(Guid movimentoId);
    Task<List<AnexoSaida>> ListarAnexos(Guid movimentoId);
    Task<ResumoDiaSaida> ResumoDia(Guid unidadeId);
}
