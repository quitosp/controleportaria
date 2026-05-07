using Core.Mensagens;
using Core.ObjetoDominio;

namespace Core.Mediator
{
    public interface IMediatorHandler
    {
        Task PublicarEvento<T>(T evento) where T : Event;
        //Task<ValidationResult> EnviarComando<T>(T comando) where T : Comand;

        Task<ComandResult> EnviarComando<T>(T comando) where T : Comand;
        Task<dynamic?> Enviar<T>(T comando) where T : class;
    }
}
