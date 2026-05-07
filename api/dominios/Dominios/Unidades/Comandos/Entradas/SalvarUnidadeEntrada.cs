using Core.ObjetoDominio;
using FluentValidation;

namespace Dominios.Unidades.Comandos.Entradas;

public class SalvarUnidadeEntrada : Comand
{
    public string Nome { get; set; } = string.Empty;
    public string? ConfiguracaoEvolutionApiUrl { get; set; }
    public string? ConfiguracaoEvolutionApiToken { get; set; }

    public override bool EhValido()
    {
        ValidationResult = new SalvarUnidadeValidation().Validate(this);
        return ValidationResult.IsValid;
    }

    public class SalvarUnidadeValidation : AbstractValidator<SalvarUnidadeEntrada>
    {
        public SalvarUnidadeValidation()
        {
        RuleFor(l => l.Nome).NotEmpty().WithMessage("O nome e obrigatorio");
        }
    }
}
