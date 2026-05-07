using Dominios.Motoristas.Entidades;
using Dominios.MovimentosPortaria.Entidades;

namespace Dominios.MovimentosPortaria.Servicos;

public interface INotificacoesPortariaService
{
    void EnfileirarChamadaParaMotorista(MovimentoPortaria movimento, Motorista motorista);
    void NotificarPortariaViaSocket(MovimentoPortaria movimento);
}

public interface IAnexoStorage
{
    Task<string> Salvar(Guid unidadeId, Guid movimentoId, string nomeOriginal, byte[] conteudo);
}
