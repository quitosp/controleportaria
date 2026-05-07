using Core.Data;
using Core.ObjetoDominio;
using Dominios.MovimentosPortaria.Comandos.Saidas;
using Dominios.MovimentosPortaria.Entidades;
using Dominios.MovimentosPortaria.IRepositorios;
using Microsoft.EntityFrameworkCore;
using Repositorios.Contexto;

namespace Repositorios.Repositorio;

public class MovimentoPortariaRepositorio : IMovimentoPortariaRepositorio
{
    private readonly ContextoDB _context;

    public MovimentoPortariaRepositorio(ContextoDB context) => _context = context;

    public IUnitOfWork UnitOfWork => _context;

    public void Salvar(MovimentoPortaria entidade)
    {
        _context.ChangeTracker.Clear();
        _context.MovimentosPortaria.Add(entidade);
    }

    public void Alterar(MovimentoPortaria entidade)
    {
        _context.ChangeTracker.Clear();
        _context.MovimentosPortaria.Update(entidade);
    }

    public async Task<MovimentoPortaria?> ObterPorId(Guid id)
        => await _context.MovimentosPortaria
            .Include(m => m.Eventos.OrderBy(e => e.Quando))
            .FirstOrDefaultAsync(l => l.Id == id);

    // RN-012 — carreta com movimento aberto bloqueia nova chegada
    public async Task<MovimentoPortaria?> ObterCarretaComMovimentoAberto(Guid unidadeId, Guid carretaId)
    {
        return await _context.MovimentosPortaria
            .Where(m => m.UnidadeId == unidadeId
                     && m.CarretaId == carretaId
                     && m.Estado != EstadoMovimento.Saiu
                     && m.Estado != EstadoMovimento.Cancelado
                     && m.Estado != EstadoMovimento.Desistencia)
            .FirstOrDefaultAsync();
    }

    // RN-010 — auto-fill por placa
    public async Task<AutoFillPlacaSaida> ObterAutoFillPorPlaca(Guid unidadeId, Guid carretaId)
    {
        var ultimo = await _context.MovimentosPortaria
            .Where(m => m.UnidadeId == unidadeId && m.CarretaId == carretaId)
            .OrderByDescending(m => m.DataChegada)
            .Select(m => new { m.TransportadoraId, m.TipoCarga })
            .FirstOrDefaultAsync();
        return new AutoFillPlacaSaida
        {
            TransportadoraId = ultimo?.TransportadoraId,
            TipoCargaSugerida = ultimo == null ? null : ultimo.TipoCarga
        };
    }

    public async Task<PagedResult<MovimentoPortariaSaida>> Listar(int pageIndex, int pageSize, string? filter = null)
    {
        var query = _context.MovimentosPortaria.AsQueryable();
        var total = await query.CountAsync();
        var lista = await query
            .OrderByDescending(m => m.DataChegada)
            .Skip((pageIndex - 1) * pageSize).Take(pageSize)
            .Select(MapearSaida())
            .ToListAsync();
        return new PagedResult<MovimentoPortariaSaida>
        {
            List = lista, PageIndex = pageIndex, PageSize = pageSize,
            TotalResults = total, Query = filter
        };
    }

    // Painel chamada — apenas movimentos NoPateoExterno e ChamadoParaInterno
    public async Task<List<PainelChamadaItemSaida>> ListarPainelChamada(Guid unidadeId, int ttlMinutos)
    {
        var agora = DateTime.UtcNow;
        var movs = await _context.MovimentosPortaria
            .Where(m => m.UnidadeId == unidadeId
                     && (m.Estado == EstadoMovimento.NoPateoExterno
                         || m.Estado == EstadoMovimento.ChamadoParaInterno))
            .OrderBy(m => m.DataChegada)
            .ToListAsync();

        return movs.Select(m => new PainelChamadaItemSaida
        {
            MovimentoPortariaId = m.Id,
            PortariaChegadaId = m.PortariaChegadaId,
            CarretaId = m.CarretaId,
            TransportadoraId = m.TransportadoraId,
            MotoristaId = m.MotoristaId,
            Motivo = m.Motivo,
            TipoCarga = m.TipoCarga,
            Produto = m.Produto,
            Setor = m.Setor,
            DataChegada = m.DataChegada,
            MinutosEspera = (int)(agora - m.DataChegada).TotalMinutes,
            Estado = m.Estado,
            ChamadaExpirada = m.Estado == EstadoMovimento.ChamadoParaInterno
                              && m.DataChamada.HasValue
                              && (agora - m.DataChamada.Value).TotalMinutes > ttlMinutos
        }).ToList();
    }

    public async Task<List<EventoFluxoSaida>> ListarEventos(Guid movimentoId)
    {
        return await _context.Set<EventoFluxo>()
            .Where(e => e.MovimentoPortariaId == movimentoId)
            .OrderBy(e => e.Quando)
            .Select(e => new EventoFluxoSaida
            {
                Id = e.Id, Tipo = e.Tipo, DeEstado = e.DeEstado, ParaEstado = e.ParaEstado,
                UsuarioId = e.UsuarioId, Quando = e.Quando, Detalhes = e.Detalhes
            })
            .ToListAsync();
    }

    public async Task<List<AnexoSaida>> ListarAnexos(Guid movimentoId)
    {
        return await _context.Set<Anexo>()
            .Where(a => a.MovimentoPortariaId == movimentoId)
            .OrderBy(a => a.Quando)
            .Select(a => new AnexoSaida
            {
                Id = a.Id, Estagio = a.Estagio, Url = a.Url,
                ContentType = a.ContentType, TamanhoBytes = a.TamanhoBytes, Quando = a.Quando
            })
            .ToListAsync();
    }

    public async Task<ResumoDiaSaida> ResumoDia(Guid unidadeId)
    {
        var inicioDia = DateTime.UtcNow.Date;
        var fimDia = inicioDia.AddDays(1);
        var query = _context.MovimentosPortaria.Where(m => m.UnidadeId == unidadeId);

        return new ResumoDiaSaida
        {
            NoPateoExterno = await query.CountAsync(m => m.Estado == EstadoMovimento.NoPateoExterno),
            NoPateoInterno = await query.CountAsync(m => m.Estado == EstadoMovimento.NoPateoInterno
                                                      || m.Estado == EstadoMovimento.NoLavador
                                                      || m.Estado == EstadoMovimento.ChamadoParaInterno),
            SaiuHoje = await query.CountAsync(m => m.Estado == EstadoMovimento.Saiu
                                                && m.DataSaida >= inicioDia && m.DataSaida < fimDia),
            CanceladosHoje = await query.CountAsync(m => (m.Estado == EstadoMovimento.Cancelado || m.Estado == EstadoMovimento.Desistencia)
                                                      && m.DataChegada >= inicioDia && m.DataChegada < fimDia),
            Total = await query.CountAsync(m => m.DataChegada >= inicioDia && m.DataChegada < fimDia)
        };
    }

    private static System.Linq.Expressions.Expression<Func<MovimentoPortaria, MovimentoPortariaSaida>> MapearSaida()
        => m => new MovimentoPortariaSaida
        {
            MovimentoPortariaId = m.Id,
            UnidadeId = m.UnidadeId,
            PortariaChegadaId = m.PortariaChegadaId,
            PorteiroChegadaId = m.PorteiroChegadaId,
            DataChegada = m.DataChegada,
            MotoristaId = m.MotoristaId,
            CarretaId = m.CarretaId,
            CavaloId = m.CavaloId,
            CarretaSegundaId = m.CarretaSegundaId,
            TransportadoraId = m.TransportadoraId,
            Motivo = m.Motivo,
            TipoCarga = m.TipoCarga,
            Destino = m.Destino,
            AutorizadoPorChegada = m.AutorizadoPorChegada,
            NumeroNFChegada = m.NumeroNFChegada,
            Produto = m.Produto,
            Setor = m.Setor,
            Observacao = m.Observacao,
            Estado = m.Estado,
            LiderQueAutorizouId = m.LiderQueAutorizouId,
            DataChamada = m.DataChamada,
            DataEntrada = m.DataEntrada,
            DataSaida = m.DataSaida,
            NumeroNFSaida = m.NumeroNFSaida,
            Lacre = m.Lacre,
            DestinoSaida = m.DestinoSaida
        };

    public void Dispose() => _context.Dispose();
}
