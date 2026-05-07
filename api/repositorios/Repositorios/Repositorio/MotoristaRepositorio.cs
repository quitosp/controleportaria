using Core.Data;
using Core.ObjetoDominio;
using Dominios.Motoristas.Comandos.Saidas;
using Dominios.Motoristas.Entidades;
using Dominios.Motoristas.IRepositorios;
using Microsoft.EntityFrameworkCore;
using Repositorios.Contexto;

namespace Repositorios.Repositorio;

public class MotoristaRepositorio : IMotoristaRepositorio
{
    private readonly ContextoDB _context;

    public MotoristaRepositorio(ContextoDB context) => _context = context;

    public IUnitOfWork UnitOfWork => _context;

    public Motorista Salvar(Motorista entidade)
    {
        _context.ChangeTracker.Clear();
        return _context.Motoristas.Add(entidade).Entity;
    }

    public void Alterar(Motorista entidade)
    {
        _context.ChangeTracker.Clear();
        _context.Motoristas.Update(entidade);
    }

    public async Task<Motorista?> Existe(Guid id) =>
        await _context.Motoristas.FirstOrDefaultAsync(l => l.Id == id);

    public async Task<Motorista?> ObterPorId(Guid id) =>
        await _context.Motoristas.FirstOrDefaultAsync(l => l.Id == id);

    public async Task<Motorista?> ObterPorNome(string valor, Guid? excluirId = null)
    {
        var query = _context.Motoristas.AsQueryable();
        if (excluirId.HasValue) query = query.Where(l => l.Id != excluirId.Value);
        return await query.FirstOrDefaultAsync(l => l.Nome == valor);
    }

    public async Task<Motorista?> ObterPorCpf(string valor, Guid? excluirId = null)
    {
        var query = _context.Motoristas.AsQueryable();
        if (excluirId.HasValue) query = query.Where(l => l.Id != excluirId.Value);
        return await query.FirstOrDefaultAsync(l => l.Cpf == valor);
    }

    public async Task<PagedResult<MotoristaSaida>> Listar(int pageIndex, int pageSize, string? filter = null)
    {
        var query = _context.Motoristas.AsQueryable();
        if (!string.IsNullOrEmpty(filter))
            query = query.Where(c => c.Nome.Contains(filter));
        var total = await query.CountAsync();
        var lista = await query
            .Skip((pageIndex - 1) * pageSize).Take(pageSize)
            .Select(l => new MotoristaSaida { MotoristaId = l.Id, Nome = l.Nome, Cpf = l.Cpf, Whatsapp = l.Whatsapp, Email = l.Email, Status = l.Status, MotivoStatus = l.MotivoStatus, UnidadeId = l.UnidadeId })
            .ToListAsync();
        return new PagedResult<MotoristaSaida>
        {
            List = lista, PageIndex = pageIndex, PageSize = pageSize,
            TotalResults = total, Query = filter
        };
    }

    public void Dispose() => _context.Dispose();
}
