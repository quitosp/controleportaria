using Core.Mensagens;
using Core.ObjetoDominio;
using Dominios.Portarias.Comandos.Entradas;
using Dominios.Portarias.Entidades;
using Dominios.Portarias.IRepositorios;
using MediatR;

namespace Dominios.Portarias.Comandos.Handlers;

public class PortariaCommandHandler : CommandHandler,
    IRequestHandler<SalvarPortariaEntrada, ComandResult>,
    IRequestHandler<AlterarPortariaEntrada, ComandResult>
{
    private readonly IPortariaRepositorio _repositorio;

    public PortariaCommandHandler(IPortariaRepositorio repositorio) => _repositorio = repositorio;

    public async Task<ComandResult> Handle(SalvarPortariaEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        if (await _repositorio.ObterPorNome(msg.Nome) is not null)
            AdicionarErro("Ja existe Portaria com este Nome");
        if (PossuiErros()) return new ComandResult(false, "Conflito", Erros(), 409);

        var entidade = new Portaria(msg.Nome, msg.UnidadeId);
        _repositorio.Salvar(entidade);
        return await PersistirDados(_repositorio.UnitOfWork, "Portaria salvo com sucesso!", new { id = entidade.Id });
    }

    public async Task<ComandResult> Handle(AlterarPortariaEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        var existe = await _repositorio.Existe(msg.PortariaId);
        if (existe is null) AdicionarErro("Portaria nao encontrado");
        if (PossuiErros()) return new ComandResult(false, "Alerta", Erros(), 404);

        if (await _repositorio.ObterPorNome(msg.Nome, msg.PortariaId) is not null)
            AdicionarErro("Ja existe outro Portaria com este Nome");
        if (PossuiErros()) return new ComandResult(false, "Conflito", Erros(), 409);

        existe!.Alterar(msg.Nome, msg.UnidadeId);
        _repositorio.Alterar(existe);
        return await PersistirDados(_repositorio.UnitOfWork, "Portaria alterado com sucesso!", new { id = existe.Id });
    }
}
