using Core.ObjetoDominio;
using FluentValidation;

namespace Dominios.Portarias.Comandos.Entradas;

public class AlterarPortariaEntrada : Comand
{
    public Guid PortariaId { get; set; }
    public string Nome { get; set; } = string.Empty;
    public Guid UnidadeId { get; set; }

    public override bool EhValido()
    {
        ValidationResult = new AlterarPortariaValidation().Validate(this);
        return ValidationResult.IsValid;
    }

    public class AlterarPortariaValidation : AbstractValidator<AlterarPortariaEntrada>
    {
        public AlterarPortariaValidation()
        {
        RuleFor(l => l.PortariaId).NotEqual(Guid.Empty).WithMessage("Id invalido");
        RuleFor(l => l.Nome).NotEmpty().WithMessage("O nome e obrigatorio");
        RuleFor(l => l.UnidadeId).NotEqual(Guid.Empty).WithMessage("UnidadeId e obrigatorio");
        }
    }
}
