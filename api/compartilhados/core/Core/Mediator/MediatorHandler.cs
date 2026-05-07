using Core.Mensagens;
using Core.ObjetoDominio;
using MediatR;

namespace Core.Mediator
{
    public class MediatorHandler : IMediatorHandler
    {
        private readonly IMediator _mediator;

        public MediatorHandler(IMediator mediator)
        {
            _mediator = mediator;
        }

        public async Task<ComandResult> EnviaComando<T>(T comando) where T : Comand
        {
            return await _mediator.Send(comando);
        }

        public async Task<ComandResult> EnviarComando<T>(T comando) where T : Comand
        {
            return await _mediator.Send(comando);
        }
        public async Task<dynamic?> Enviar<T>(T comando) where T : class
        {
            return await _mediator.Send(comando);
        }

        //public async Task<ValidationResult> EnviarComando<T>(T comando) where T : Command
        //{
        //    return await _mediator.Send(comando);
        //}

        public async Task PublicarEvento<T>(T evento) where T : Event
        {
            await _mediator.Publish(evento);
        }
    }
}
