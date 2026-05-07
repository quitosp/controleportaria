using Core.Mensagens;
using Core.ObjetoDominio;
using Dominios.MovimentosPortaria.Entidades;
using FluentValidation;

namespace Dominios.MovimentosPortaria.Comandos.Entradas;

public class RegistrarSaidaEntrada : Comand
{
    public Guid MovimentoPortariaId { get; set; }
    public string? NumeroNF { get; set; }
    public string? Lacre { get; set; }
    public string? Destino { get; set; }
    public string? NumeroContainer { get; set; }
    public string? Contrato { get; set; }
    public string? Observacao { get; set; }

    public override bool EhValido()
    {
        ValidationResult = new RegistrarSaidaValidation().Validate(this);
        return ValidationResult.IsValid;
    }
}

public class RegistrarSaidaValidation : AbstractValidator<RegistrarSaidaEntrada>
{
    public RegistrarSaidaValidation()
    {
        RuleFor(x => x.MovimentoPortariaId).NotEmpty();
    }
}

public class AlterarMovimentoEntrada : Comand
{
    public Guid MovimentoPortariaId { get; set; }
    public Guid? CarretaId { get; set; }
    public Guid? CavaloId { get; set; }
    public Guid? CarretaSegundaId { get; set; }
    public Guid? TransportadoraId { get; set; }
    public Guid? MotoristaId { get; set; }
    public MotivoEntrada? Motivo { get; set; }
    public string? NumeroNFChegada { get; set; }
    public string? Produto { get; set; }
    public string? Setor { get; set; }
    public string? ContratoChegada { get; set; }
    public string? NumeroContainerChegada { get; set; }
    public string? Observacao { get; set; }

    public override bool EhValido()
    {
        ValidationResult = new AlterarMovimentoValidation().Validate(this);
        return ValidationResult.IsValid;
    }
}

public class AlterarMovimentoValidation : AbstractValidator<AlterarMovimentoEntrada>
{
    public AlterarMovimentoValidation() => RuleFor(x => x.MovimentoPortariaId).NotEmpty();
}

public class AnexarArquivoEntrada : Comand
{
    public Guid MovimentoPortariaId { get; set; }
    public EstagioAnexo Estagio { get; set; }
    public string NomeArquivo { get; set; } = string.Empty;
    public string ContentType { get; set; } = string.Empty;
    public byte[] Conteudo { get; set; } = Array.Empty<byte>();
    public override bool EhValido()
    {
        ValidationResult = new AnexarArquivoValidation().Validate(this);
        return ValidationResult.IsValid;
    }
}

public class AnexarArquivoValidation : AbstractValidator<AnexarArquivoEntrada>
{
    private static readonly HashSet<string> Permitidos = new(StringComparer.OrdinalIgnoreCase)
    {
        "image/jpeg", "image/jpg", "image/png", "application/pdf"
    };

    public AnexarArquivoValidation()
    {
        RuleFor(x => x.MovimentoPortariaId).NotEmpty();
        RuleFor(x => x.NomeArquivo).NotEmpty();
        RuleFor(x => x.ContentType)
            .Must(c => Permitidos.Contains(c))
            .WithMessage("Formato invalido. Aceitos: jpg, jpeg, png, pdf.");
        RuleFor(x => x.Conteudo)
            .Must(c => c != null && c.Length > 0 && c.Length <= 10 * 1024 * 1024)
            .WithMessage("Arquivo deve ter ate 10MB.");
    }
}
