using Core.Mensagens;
using Core.ObjetoDominio;
using Dominios.Veiculos.Comandos.Entradas;
using Dominios.Veiculos.Entidades;
using Dominios.Veiculos.IRepositorios;
using MediatR;

namespace Dominios.Veiculos.Comandos.Handlers;

public class VeiculoCommandHandler : CommandHandler,
    IRequestHandler<SalvarVeiculoEntrada, ComandResult>,
    IRequestHandler<AlterarVeiculoEntrada, ComandResult>
{
    private readonly IVeiculoRepositorio _repositorio;

    public VeiculoCommandHandler(IVeiculoRepositorio repositorio) => _repositorio = repositorio;

    public async Task<ComandResult> Handle(SalvarVeiculoEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        if (await _repositorio.ObterPorNome(msg.Nome) is not null)
            AdicionarErro("Ja existe Veiculo com este Nome");
        if (await _repositorio.ObterPorPlaca(msg.Placa) is not null)
            AdicionarErro("Ja existe Veiculo com este Placa");
        if (PossuiErros()) return new ComandResult(false, "Conflito", Erros(), 409);

        var entidade = new Veiculo(msg.Nome, msg.Placa, msg.Tipo, msg.TransportadoraId, msg.UnidadeId);
        _repositorio.Salvar(entidade);
        return await PersistirDados(_repositorio.UnitOfWork, "Veiculo salvo com sucesso!", new { id = entidade.Id });
    }

    public async Task<ComandResult> Handle(AlterarVeiculoEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        var existe = await _repositorio.Existe(msg.VeiculoId);
        if (existe is null) AdicionarErro("Veiculo nao encontrado");
        if (PossuiErros()) return new ComandResult(false, "Alerta", Erros(), 404);

        if (await _repositorio.ObterPorNome(msg.Nome, msg.VeiculoId) is not null)
            AdicionarErro("Ja existe outro Veiculo com este Nome");
        if (await _repositorio.ObterPorPlaca(msg.Placa, msg.VeiculoId) is not null)
            AdicionarErro("Ja existe outro Veiculo com este Placa");
        if (PossuiErros()) return new ComandResult(false, "Conflito", Erros(), 409);

        existe!.Alterar(msg.Nome, msg.Placa, msg.Tipo, msg.TransportadoraId, msg.UnidadeId);
        _repositorio.Alterar(existe);
        return await PersistirDados(_repositorio.UnitOfWork, "Veiculo alterado com sucesso!", new { id = existe.Id });
    }
}
