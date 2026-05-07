using Dominios.Motoristas.Entidades;
using Dominios.MovimentosPortaria.Entidades;
using Dominios.MovimentosPortaria.Servicos;

namespace Api.Integracoes;

// RN-011/RN-017 — apenas enfileira NotificacaoPendente; envio real e do worker (HIST-022)
public class NotificacoesPortariaService : INotificacoesPortariaService
{
    public void EnfileirarChamadaParaMotorista(MovimentoPortaria movimento, Motorista motorista)
    {
        var msg = $"Frigoestrela: dirija-se a portaria. Movimento {movimento.Id}.";

        if (!string.IsNullOrEmpty(motorista.Whatsapp))
            movimento.EnfileirarNotificacao(CanalNotificacao.Whatsapp, motorista.Whatsapp, msg);

        if (!string.IsNullOrEmpty(motorista.Email))
            movimento.EnfileirarNotificacao(CanalNotificacao.Email, motorista.Email!, msg);
    }

    public void NotificarPortariaViaSocket(MovimentoPortaria movimento)
    {
        movimento.EnfileirarNotificacao(CanalNotificacao.Socket,
            $"unidade:{movimento.UnidadeId}:portaria:{movimento.PortariaChegadaId}",
            $"chamada-autorizada:{movimento.Id}");
    }
}
