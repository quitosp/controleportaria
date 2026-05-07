using Core.ObjetoDominio;
using FluentValidation;

namespace Dominios.Transportadoras.Comandos.Entradas;

public class AlterarTransportadoraEntrada : Comand
{
    public Guid TransportadoraId { get; set; }
    public string Nome { get; set; } = string.Empty;
    public string RazaoSocial { get; set; } = string.Empty;
    public string Cnpj { get; set; } = string.Empty;
    public Guid UnidadeId { get; set; }

    public override bool EhValido()
    {
        ValidationResult = new AlterarTransportadoraValidation().Validate(this);
        return ValidationResult.IsValid;
    }

    public class AlterarTransportadoraValidation : AbstractValidator<AlterarTransportadoraEntrada>
    {
        public AlterarTransportadoraValidation()
        {
        RuleFor(l => l.TransportadoraId).NotEqual(Guid.Empty).WithMessage("Id invalido");
        RuleFor(l => l.Nome).NotEmpty().WithMessage("O nome e obrigatorio");
        RuleFor(l => l.RazaoSocial).NotEmpty().WithMessage("RazaoSocial e obrigatorio");
        RuleFor(l => l.RazaoSocial).MaximumLength(200);
        RuleFor(l => l.Cnpj).NotEmpty().WithMessage("Cnpj e obrigatorio");
        RuleFor(l => l.Cnpj).MaximumLength(14);
        RuleFor(l => l.UnidadeId).NotEqual(Guid.Empty).WithMessage("UnidadeId e obrigatorio");
        }
    }
}
