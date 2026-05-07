using Core.Data;
using Core.ObjetoDominio;
using Dominios.Portarias.Comandos.Saidas;
using Dominios.Portarias.Entidades;
using Dominios.Portarias.IRepositorios;
using Microsoft.EntityFrameworkCore;
using Repositorios.Contexto;

namespace Repositorios.Repositorio;

public class PortariaRepositorio : IPortariaRepositorio
{
    private readonly ContextoDB _context;

    public PortariaRepositorio(ContextoDB context) => _context = context;

    public IUnitOfWork UnitOfWork => _context;

    public Portaria Salvar(Portaria entidade)
    {
        _context.ChangeTracker.Clear();
        return _context.Portarias.Add(entidade).Entity;
    }

    public void Alterar(Portaria entidade)
    {
        _context.ChangeTracker.Clear();
        _context.Portarias.Update(entidade);
    }

    public async Task<Portaria?> Existe(Guid id) =>
        await _context.Portarias.FirstOrDefaultAsync(l => l.Id == id);

    public async Task<Portaria?> ObterPorNome(string valor, Guid? excluirId = null)
    {
        var query = _context.Portarias.AsQueryable();
        if (excluirId.HasValue) query = query.Where(l => l.Id != excluirId.Value);
        return await query.FirstOrDefaultAsync(l => l.Nome == valor);
    }

    public async Task<PagedResult<PortariaSaida>> Listar(int pageIndex, int pageSize, string? filter = null)
    {
        var query = _context.Portarias.AsQueryable();
        if (!string.IsNullOrEmpty(filter))
            query = query.Where(c => c.Nome.Contains(filter));
        var total = await query.CountAsync();
        var lista = await query
            .Skip((pageIndex - 1) * pageSize).Take(pageSize)
            .Select(l => new PortariaSaida { PortariaId = l.Id, Nome = l.Nome, UnidadeId = l.UnidadeId })
            .ToListAsync();
        return new PagedResult<PortariaSaida>
        {
            List = lista, PageIndex = pageIndex, PageSize = pageSize,
            TotalResults = total, Query = filter
        };
    }

    public void Dispose() => _context.Dispose();
}
