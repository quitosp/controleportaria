using Core.ObjetoDominio;
using FluentValidation;

namespace Dominios.Portarias.Comandos.Entradas;

public class SalvarPortariaEntrada : Comand
{
    public string Nome { get; set; } = string.Empty;
    public Guid UnidadeId { get; set; }

    public override bool EhValido()
    {
        ValidationResult = new SalvarPortariaValidation().Validate(this);
        return ValidationResult.IsValid;
    }

    public class SalvarPortariaValidation : AbstractValidator<SalvarPortariaEntrada>
    {
        public SalvarPortariaValidation()
        {
        RuleFor(l => l.Nome).NotEmpty().WithMessage("O nome e obrigatorio");
        RuleFor(l => l.UnidadeId).NotEqual(Guid.Empty).WithMessage("UnidadeId e obrigatorio");
        }
    }
}
