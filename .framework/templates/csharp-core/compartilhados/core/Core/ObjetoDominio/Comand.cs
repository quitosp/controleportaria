using Core.Mensagens;
using FluentValidation.Results;
using MediatR;
using System.Text.Json.Serialization;

namespace Core.ObjetoDominio
{
    public class Comand : Message, IRequest<ComandResult>
    {
        public DateTime Timestamp { get; private set; }

        //public ComandResult ValidationResult { get; set; }
        [JsonIgnore]
        public ValidationResult ValidationResult { get; set; }

        protected Comand()
        {
            Timestamp = DateTime.Now;
        }

        public virtual bool EhValido()
        {
            throw new NotImplementedException();
        }
    }
}
