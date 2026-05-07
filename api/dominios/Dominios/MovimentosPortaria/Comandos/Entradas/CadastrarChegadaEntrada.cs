using Core.Mensagens;
using Core.ObjetoDominio;
using Dominios.MovimentosPortaria.Entidades;
using FluentValidation;

namespace Dominios.MovimentosPortaria.Comandos.Entradas;

public class CadastrarChegadaEntrada : Comand
{
    public Guid PortariaChegadaId { get; set; }
    public Guid MotoristaId { get; set; }
    public Guid CarretaId { get; set; }
    public Guid? CavaloId { get; set; }
    public Guid? CarretaSegundaId { get; set; }
    public Guid? TransportadoraId { get; set; }
    public MotivoEntrada Motivo { get; set; }
    public TipoCarga TipoCarga { get; set; }
    public DestinoPateo Destino { get; set; }
    public string? AutorizadoPorChegada { get; set; }
    public string? NumeroNFChegada { get; set; }
    public string? Produto { get; set; }
    public string? Setor { get; set; }
    public string? ContratoChegada { get; set; }
    public string? NumeroContainerChegada { get; set; }
    public string? Observacao { get; set; }

    public override bool EhValido()
    {
        ValidationResult = new CadastrarChegadaValidation().Validate(this);
        return ValidationResult.IsValid;
    }
}

public class CadastrarChegadaValidation : AbstractValidator<CadastrarChegadaEntrada>
{
    public CadastrarChegadaValidation()
    {
        RuleFor(x => x.PortariaChegadaId).NotEmpty();
        RuleFor(x => x.MotoristaId).NotEmpty();
        RuleFor(x => x.CarretaId).NotEmpty();
        RuleFor(x => x.AutorizadoPorChegada)
            .NotEmpty().When(x => x.Destino == DestinoPateo.Interno)
            .WithMessage("AutorizadoPor obrigatorio quando destino e Interno.");
    }
}
