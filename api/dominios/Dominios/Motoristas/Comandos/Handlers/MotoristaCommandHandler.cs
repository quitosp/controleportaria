using Core.Mensagens;
using Core.ObjetoDominio;
using Dominios.Motoristas.Comandos.Entradas;
using Dominios.Motoristas.Entidades;
using Dominios.Motoristas.IRepositorios;
using MediatR;

namespace Dominios.Motoristas.Comandos.Handlers;

public class MotoristaCommandHandler : CommandHandler,
    IRequestHandler<SalvarMotoristaEntrada, ComandResult>,
    IRequestHandler<AlterarMotoristaEntrada, ComandResult>
{
    private readonly IMotoristaRepositorio _repositorio;

    public MotoristaCommandHandler(IMotoristaRepositorio repositorio) => _repositorio = repositorio;

    public async Task<ComandResult> Handle(SalvarMotoristaEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        if (await _repositorio.ObterPorNome(msg.Nome) is not null)
            AdicionarErro("Ja existe Motorista com este Nome");
        if (await _repositorio.ObterPorCpf(msg.Cpf) is not null)
            AdicionarErro("Ja existe Motorista com este Cpf");
        if (PossuiErros()) return new ComandResult(false, "Conflito", Erros(), 409);

        var entidade = new Motorista(msg.Nome, msg.Cpf, msg.Whatsapp, msg.Email, msg.Status, msg.MotivoStatus, msg.UnidadeId);
        _repositorio.Salvar(entidade);
        return await PersistirDados(_repositorio.UnitOfWork, "Motorista salvo com sucesso!", new { id = entidade.Id });
    }

    public async Task<ComandResult> Handle(AlterarMotoristaEntrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        var existe = await _repositorio.Existe(msg.MotoristaId);
        if (existe is null) AdicionarErro("Motorista nao encontrado");
        if (PossuiErros()) return new ComandResult(false, "Alerta", Erros(), 404);

        if (await _repositorio.ObterPorNome(msg.Nome, msg.MotoristaId) is not null)
            AdicionarErro("Ja existe outro Motorista com este Nome");
        if (await _repositorio.ObterPorCpf(msg.Cpf, msg.MotoristaId) is not null)
            AdicionarErro("Ja existe outro Motorista com este Cpf");
        if (PossuiErros()) return new ComandResult(false, "Conflito", Erros(), 409);

        existe!.Alterar(msg.Nome, msg.Cpf, msg.Whatsapp, msg.Email, msg.Status, msg.MotivoStatus, msg.UnidadeId);
        _repositorio.Alterar(existe);
        return await PersistirDados(_repositorio.UnitOfWork, "Motorista alterado com sucesso!", new { id = existe.Id });
    }
}
