using Core.Data;
using Core.ObjetoDominio;
using Dominios.Transportadoras.Comandos.Saidas;
using Dominios.Transportadoras.Entidades;
using Dominios.Transportadoras.IRepositorios;
using Microsoft.EntityFrameworkCore;
using Repositorios.Contexto;

namespace Repositorios.Repositorio;

public class TransportadoraRepositorio : ITransportadoraRepositorio
{
    private readonly ContextoDB _context;

    public TransportadoraRepositorio(ContextoDB context) => _context = context;

    public IUnitOfWork UnitOfWork => _context;

    public Transportadora Salvar(Transportadora entidade)
    {
        _context.ChangeTracker.Clear();
        return _context.Transportadoras.Add(entidade).Entity;
    }

    public void Alterar(Transportadora entidade)
    {
        _context.ChangeTracker.Clear();
        _context.Transportadoras.Update(entidade);
    }

    public async Task<Transportadora?> Existe(Guid id) =>
        await _context.Transportadoras.FirstOrDefaultAsync(l => l.Id == id);

    public async Task<Transportadora?> ObterPorNome(string valor, Guid? excluirId = null)
    {
        var query = _context.Transportadoras.AsQueryable();
        if (excluirId.HasValue) query = query.Where(l => l.Id != excluirId.Value);
        return await query.FirstOrDefaultAsync(l => l.Nome == valor);
    }

    public async Task<Transportadora?> ObterPorCnpj(string valor, Guid? excluirId = null)
    {
        var query = _context.Transportadoras.AsQueryable();
        if (excluirId.HasValue) query = query.Where(l => l.Id != excluirId.Value);
        return await query.FirstOrDefaultAsync(l => l.Cnpj == valor);
    }

    public async Task<PagedResult<TransportadoraSaida>> Listar(int pageIndex, int pageSize, string? filter = null)
    {
        var query = _context.Transportadoras.AsQueryable();
        if (!string.IsNullOrEmpty(filter))
            query = query.Where(c => c.Nome.Contains(filter));
        var total = await query.CountAsync();
        var lista = await query
            .Skip((pageIndex - 1) * pageSize).Take(pageSize)
            .Select(l => new TransportadoraSaida { TransportadoraId = l.Id, Nome = l.Nome, RazaoSocial = l.RazaoSocial, Cnpj = l.Cnpj, UnidadeId = l.UnidadeId })
            .ToListAsync();
        return new PagedResult<TransportadoraSaida>
        {
            List = lista, PageIndex = pageIndex, PageSize = pageSize,
            TotalResults = total, Query = filter
        };
    }

    public void Dispose() => _context.Dispose();
}
