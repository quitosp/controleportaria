using Core.Mensagens;
using Core.ObjetoDominio;
using Dominios.Transportadoras.Comandos.Entradas;
using Dominios.Transportadoras.Entidades;
using Dominios.Transportadoras.IRepositorios;
using MediatR;

namespace Dominios.Transportadoras.Comandos.Handlers;

public class TransportadoraCommandHandler : CommandHandler,
    IRequestHandler<SalvarTransportadoraEntrada, ComandResult>,
    IRequestHandler<AlterarTransportadoraEntrada, ComandResult>
{
    private readonly ITransportadoraRepositorio _repositorio;

    public TransportadoraCommandHandler(ITransportadoraRepositorio repositorio) => _repositorio = repositorio;

    public async Task<ComandResult> Handle(SalvarTransportadoraEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        if (await _repositorio.ObterPorNome(msg.Nome) is not null)
            AdicionarErro("Ja existe Transportadora com este Nome");
        if (await _repositorio.ObterPorCnpj(msg.Cnpj) is not null)
            AdicionarErro("Ja existe Transportadora com este Cnpj");
        if (PossuiErros()) return new ComandResult(false, "Conflito", Erros(), 409);

        var entidade = new Transportadora(msg.Nome, msg.RazaoSocial, msg.Cnpj, msg.UnidadeId);
        _repositorio.Salvar(entidade);
        return await PersistirDados(_repositorio.UnitOfWork, "Transportadora salvo com sucesso!", new { id = entidade.Id });
    }

    public async Task<ComandResult> Handle(AlterarTransportadoraEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        var existe = await _repositorio.Existe(msg.TransportadoraId);
        if (existe is null) AdicionarErro("Transportadora nao encontrado");
        if (PossuiErros()) return new ComandResult(false, "Alerta", Erros(), 404);

        if (await _repositorio.ObterPorNome(msg.Nome, msg.TransportadoraId) is not null)
            AdicionarErro("Ja existe outro Transportadora com este Nome");
        if (await _repositorio.ObterPorCnpj(msg.Cnpj, msg.TransportadoraId) is not null)
            AdicionarErro("Ja existe outro Transportadora com este Cnpj");
        if (PossuiErros()) return new ComandResult(false, "Conflito", Erros(), 409);

        existe!.Alterar(msg.Nome, msg.RazaoSocial, msg.Cnpj, msg.UnidadeId);
        _repositorio.Alterar(existe);
        return await PersistirDados(_repositorio.UnitOfWork, "Transportadora alterado com sucesso!", new { id = existe.Id });
    }
}
