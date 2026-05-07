using Core.Mensagens;
using Core.ObjetoDominio;
using FluentValidation;

namespace Dominios.MovimentosPortaria.Comandos.Entradas;

public class ChamarVeiculoEntrada : Comand
{
    public Guid MovimentoPortariaId { get; set; }

    public override bool EhValido()
    {
        ValidationResult = new ChamarVeiculoValidation().Validate(this);
        return ValidationResult.IsValid;
    }
}

public class ChamarVeiculoValidation : AbstractValidator<ChamarVeiculoEntrada>
{
    public ChamarVeiculoValidation() => RuleFor(x => x.MovimentoPortariaId).NotEmpty();
}

public class RecancelarChamadaEntrada : Comand
{
    public Guid MovimentoPortariaId { get; set; }
    public override bool EhValido() { ValidationResult = new RecancelarChamadaValidation().Validate(this); return ValidationResult.IsValid; }
}
public class RecancelarChamadaValidation : AbstractValidator<RecancelarChamadaEntrada>
{
    public RecancelarChamadaValidation() => RuleFor(x => x.MovimentoPortariaId).NotEmpty();
}

public class ConfirmarEntradaEntrada : Comand
{
    public Guid MovimentoPortariaId { get; set; }
    public override bool EhValido() { ValidationResult = new ConfirmarEntradaValidation().Validate(this); return ValidationResult.IsValid; }
}
public class ConfirmarEntradaValidation : AbstractValidator<ConfirmarEntradaEntrada>
{
    public ConfirmarEntradaValidation() => RuleFor(x => x.MovimentoPortariaId).NotEmpty();
}

public class CancelarMovimentoEntrada : Comand
{
    public Guid MovimentoPortariaId { get; set; }
    public string Observacao { get; set; } = string.Empty;
    public override bool EhValido() { ValidationResult = new CancelarMovimentoValidation().Validate(this); return ValidationResult.IsValid; }
}
public class CancelarMovimentoValidation : AbstractValidator<CancelarMovimentoEntrada>
{
    public CancelarMovimentoValidation()
    {
        RuleFor(x => x.MovimentoPortariaId).NotEmpty();
        RuleFor(x => x.Observacao).NotEmpty().WithMessage("Observacao obrigatoria.");
    }
}

public class DesistirMovimentoEntrada : Comand
{
    public Guid MovimentoPortariaId { get; set; }
    public string Observacao { get; set; } = string.Empty;
    public override bool EhValido() { ValidationResult = new DesistirMovimentoValidation().Validate(this); return ValidationResult.IsValid; }
}
public class DesistirMovimentoValidation : AbstractValidator<DesistirMovimentoEntrada>
{
    public DesistirMovimentoValidation()
    {
        RuleFor(x => x.MovimentoPortariaId).NotEmpty();
        RuleFor(x => x.Observacao).NotEmpty().WithMessage("Observacao obrigatoria.");
    }
}
