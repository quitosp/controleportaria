using Core.Data;
using Core.ObjetoDominio;
using Dominios.Unidades.Comandos.Saidas;
using Dominios.Unidades.Entidades;
using Dominios.Unidades.IRepositorios;
using Microsoft.EntityFrameworkCore;
using Repositorios.Contexto;

namespace Repositorios.Repositorio;

public class UnidadeRepositorio : IUnidadeRepositorio
{
    private readonly ContextoDB _context;

    public UnidadeRepositorio(ContextoDB context) => _context = context;

    public IUnitOfWork UnitOfWork => _context;

    public Unidade Salvar(Unidade entidade)
    {
        _context.ChangeTracker.Clear();
        return _context.Unidades.Add(entidade).Entity;
    }

    public void Alterar(Unidade entidade)
    {
        _context.ChangeTracker.Clear();
        _context.Unidades.Update(entidade);
    }

    public async Task<Unidade?> Existe(Guid id) =>
        await _context.Unidades.FirstOrDefaultAsync(l => l.Id == id);

    public async Task<Unidade?> ObterPorNome(string valor, Guid? excluirId = null)
    {
        var query = _context.Unidades.AsQueryable();
        if (excluirId.HasValue) query = query.Where(l => l.Id != excluirId.Value);
        return await query.FirstOrDefaultAsync(l => l.Nome == valor);
    }

    public async Task<PagedResult<UnidadeSaida>> Listar(int pageIndex, int pageSize, string? filter = null)
    {
        var query = _context.Unidades.AsQueryable();
        if (!string.IsNullOrEmpty(filter))
            query = query.Where(c => c.Nome.Contains(filter));
        var total = await query.CountAsync();
        var lista = await query
            .Skip((pageIndex - 1) * pageSize).Take(pageSize)
            .Select(l => new UnidadeSaida { UnidadeId = l.Id, Nome = l.Nome, ConfiguracaoEvolutionApiUrl = l.ConfiguracaoEvolutionApiUrl, ConfiguracaoEvolutionApiToken = l.ConfiguracaoEvolutionApiToken })
            .ToListAsync();
        return new PagedResult<UnidadeSaida>
        {
            List = lista, PageIndex = pageIndex, PageSize = pageSize,
            TotalResults = total, Query = filter
        };
    }

    public void Dispose() => _context.Dispose();
}
