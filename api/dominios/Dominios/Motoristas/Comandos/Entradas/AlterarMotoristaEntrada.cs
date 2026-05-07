using Core.ObjetoDominio;
using FluentValidation;

namespace Dominios.Motoristas.Comandos.Entradas;

public class AlterarMotoristaEntrada : Comand
{
    public Guid MotoristaId { get; set; }
    public string Nome { get; set; } = string.Empty;
    public string Cpf { get; set; } = string.Empty;
    public string Whatsapp { get; set; } = string.Empty;
    public string? Email { get; set; }
    public int Status { get; set; }
    public string? MotivoStatus { get; set; }
    public Guid UnidadeId { get; set; }

    public override bool EhValido()
    {
        ValidationResult = new AlterarMotoristaValidation().Validate(this);
        return ValidationResult.IsValid;
    }

    public class AlterarMotoristaValidation : AbstractValidator<AlterarMotoristaEntrada>
    {
        public AlterarMotoristaValidation()
        {
        RuleFor(l => l.MotoristaId).NotEqual(Guid.Empty).WithMessage("Id invalido");
        RuleFor(l => l.Nome).NotEmpty().WithMessage("O nome e obrigatorio");
        RuleFor(l => l.Cpf).NotEmpty().WithMessage("Cpf e obrigatorio");
        RuleFor(l => l.Cpf).MaximumLength(11);
        RuleFor(l => l.Whatsapp).NotEmpty().WithMessage("Whatsapp e obrigatorio");
        RuleFor(l => l.Whatsapp).MaximumLength(20);
        RuleFor(l => l.Status).GreaterThan(0).WithMessage("Status deve ser maior que zero");
        RuleFor(l => l.UnidadeId).NotEqual(Guid.Empty).WithMessage("UnidadeId e obrigatorio");
        }
    }
}
