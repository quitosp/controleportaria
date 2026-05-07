namespace Api.Integracoes;

public interface IEvolutionApiClient
{
    Task EnviarMensagem(string urlBase, string token, string instancia, string telefone, string mensagem, CancellationToken ct);
}

public interface IEmailSender
{
    Task Enviar(string para, string assunto, string corpo, CancellationToken ct);
}
