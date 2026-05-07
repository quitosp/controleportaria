using Core.Mensagens;
using Core.ObjetoDominio;
using Dominios.Unidades.Comandos.Entradas;
using Dominios.Unidades.Entidades;
using Dominios.Unidades.IRepositorios;
using MediatR;

namespace Dominios.Unidades.Comandos.Handlers;

public class UnidadeCommandHandler : CommandHandler,
    IRequestHandler<SalvarUnidadeEntrada, ComandResult>,
    IRequestHandler<AlterarUnidadeEntrada, ComandResult>
{
    private readonly IUnidadeRepositorio _repositorio;

    public UnidadeCommandHandler(IUnidadeRepositorio repositorio) => _repositorio = repositorio;

    public async Task<ComandResult> Handle(SalvarUnidadeEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        if (await _repositorio.ObterPorNome(msg.Nome) is not null)
            AdicionarErro("Ja existe Unidade com este Nome");
        if (PossuiErros()) return new ComandResult(false, "Conflito", Erros(), 409);

        var entidade = new Unidade(msg.Nome, msg.ConfiguracaoEvolutionApiUrl, msg.ConfiguracaoEvolutionApiToken);
        _repositorio.Salvar(entidade);
        return await PersistirDados(_repositorio.UnitOfWork, "Unidade salvo com sucesso!", new { id = entidade.Id });
    }

    public async Task<ComandResult> Handle(AlterarUnidadeEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        var existe = await _repositorio.Existe(msg.UnidadeId);
        if (existe is null) AdicionarErro("Unidade nao encontrado");
        if (PossuiErros()) return new ComandResult(false, "Alerta", Erros(), 404);

        if (await _repositorio.ObterPorNome(msg.Nome, msg.UnidadeId) is not null)
            AdicionarErro("Ja existe outro Unidade com este Nome");
        if (PossuiErros()) return new ComandResult(false, "Conflito", Erros(), 409);

        existe!.Alterar(msg.Nome, msg.ConfiguracaoEvolutionApiUrl, msg.ConfiguracaoEvolutionApiToken);
        _repositorio.Alterar(existe);
        return await PersistirDados(_repositorio.UnitOfWork, "Unidade alterado com sucesso!", new { id = existe.Id });
    }
}
