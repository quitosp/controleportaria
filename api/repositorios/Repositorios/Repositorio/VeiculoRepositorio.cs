using Core.Data;
using Core.ObjetoDominio;
using Dominios.Veiculos.Comandos.Saidas;
using Dominios.Veiculos.Entidades;
using Dominios.Veiculos.IRepositorios;
using Microsoft.EntityFrameworkCore;
using Repositorios.Contexto;

namespace Repositorios.Repositorio;

public class VeiculoRepositorio : IVeiculoRepositorio
{
    private readonly ContextoDB _context;

    public VeiculoRepositorio(ContextoDB context) => _context = context;

    public IUnitOfWork UnitOfWork => _context;

    public Veiculo Salvar(Veiculo entidade)
    {
        _context.ChangeTracker.Clear();
        return _context.Veiculos.Add(entidade).Entity;
    }

    public void Alterar(Veiculo entidade)
    {
        _context.ChangeTracker.Clear();
        _context.Veiculos.Update(entidade);
    }

    public async Task<Veiculo?> Existe(Guid id) =>
        await _context.Veiculos.FirstOrDefaultAsync(l => l.Id == id);

    public async Task<Veiculo?> ObterPorNome(string valor, Guid? excluirId = null)
    {
        var query = _context.Veiculos.AsQueryable();
        if (excluirId.HasValue) query = query.Where(l => l.Id != excluirId.Value);
        return await query.FirstOrDefaultAsync(l => l.Nome == valor);
    }

    public async Task<Veiculo?> ObterPorPlaca(string valor, Guid? excluirId = null)
    {
        var query = _context.Veiculos.AsQueryable();
        if (excluirId.HasValue) query = query.Where(l => l.Id != excluirId.Value);
        return await query.FirstOrDefaultAsync(l => l.Placa == valor);
    }

    public async Task<PagedResult<VeiculoSaida>> Listar(int pageIndex, int pageSize, string? filter = null)
    {
        var query = _context.Veiculos.AsQueryable();
        if (!string.IsNullOrEmpty(filter))
            query = query.Where(c => c.Nome.Contains(filter));
        var total = await query.CountAsync();
        var lista = await query
            .Skip((pageIndex - 1) * pageSize).Take(pageSize)
            .Select(l => new VeiculoSaida { VeiculoId = l.Id, Nome = l.Nome, Placa = l.Placa, Tipo = l.Tipo, TransportadoraId = l.TransportadoraId, UnidadeId = l.UnidadeId })
            .ToListAsync();
        return new PagedResult<VeiculoSaida>
        {
            List = lista, PageIndex = pageIndex, PageSize = pageSize,
            TotalResults = total, Query = filter
        };
    }

    public void Dispose() => _context.Dispose();
}
