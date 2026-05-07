using Core.ObjetoDominio;
using FluentValidation;

namespace Dominios.Unidades.Comandos.Entradas;

public class AlterarUnidadeEntrada : Comand
{
    public Guid UnidadeId { get; set; }
    public string Nome { get; set; } = string.Empty;
    public string? ConfiguracaoEvolutionApiUrl { get; set; }
    public string? ConfiguracaoEvolutionApiToken { get; set; }

    public override bool EhValido()
    {
        ValidationResult = new AlterarUnidadeValidation().Validate(this);
        return ValidationResult.IsValid;
    }

    public class AlterarUnidadeValidation : AbstractValidator<AlterarUnidadeEntrada>
    {
        public AlterarUnidadeValidation()
        {
        RuleFor(l => l.UnidadeId).NotEqual(Guid.Empty).WithMessage("Id invalido");
        RuleFor(l => l.Nome).NotEmpty().WithMessage("O nome e obrigatorio");
        }
    }
}
