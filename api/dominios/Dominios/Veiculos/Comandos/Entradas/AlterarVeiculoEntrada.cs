using Core.ObjetoDominio;
using FluentValidation;

namespace Dominios.Veiculos.Comandos.Entradas;

public class AlterarVeiculoEntrada : Comand
{
    public Guid VeiculoId { get; set; }
    public string Nome { get; set; } = string.Empty;
    public string Placa { get; set; } = string.Empty;
    public int Tipo { get; set; }
    public Guid? TransportadoraId { get; set; }
    public Guid UnidadeId { get; set; }

    public override bool EhValido()
    {
        ValidationResult = new AlterarVeiculoValidation().Validate(this);
        return ValidationResult.IsValid;
    }

    public class AlterarVeiculoValidation : AbstractValidator<AlterarVeiculoEntrada>
    {
        public AlterarVeiculoValidation()
        {
        RuleFor(l => l.VeiculoId).NotEqual(Guid.Empty).WithMessage("Id invalido");
        RuleFor(l => l.Nome).NotEmpty().WithMessage("O nome e obrigatorio");
        RuleFor(l => l.Placa).NotEmpty().WithMessage("Placa e obrigatorio");
        RuleFor(l => l.Placa).MaximumLength(8);
        RuleFor(l => l.Tipo).GreaterThan(0).WithMessage("Tipo deve ser maior que zero");
        RuleFor(l => l.UnidadeId).NotEqual(Guid.Empty).WithMessage("UnidadeId e obrigatorio");
        }
    }
}
