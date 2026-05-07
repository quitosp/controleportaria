using Core.ObjetoDominio;
using FluentValidation;
using FluentValidation.Results;

namespace Core.Usuarios.EntradaSaidaDados.Entrada
{
    public class UsuarioLoginEntrada : Comand
    {
        //[Required(ErrorMessage = "O campo {0} é obrigatório")]
        //[EmailAddress(ErrorMessage = "O campo {0} está em formato inválido")]
        public string Email { get; set; }

        //[Required(ErrorMessage = "O campo {0} é obrigatório")]
        //[StringLength(100, ErrorMessage = "O campo {0} precisa ter entre {2} e {1} caracteres", MinimumLength = 6)]
        public string Senha { get; set; }

        public override bool EhValido()
        {
            ValidationResult = new UsuarioLoginValidation().Validate(this);
            return ValidationResult.IsValid;
        }


        public class UsuarioLoginValidation : AbstractValidator<UsuarioLoginEntrada>
        {
            public UsuarioLoginValidation()
            {

                RuleFor(c => c.Email)
                    .NotEmpty()
                    .WithMessage("O email não foi informado");

                RuleFor(c => c.Email)
                    .EmailAddress()
                    .WithMessage("O campo email está em formato inválido");

                RuleFor(c => c.Senha)
                    .NotEmpty()
                    .WithMessage("A senha não foi informada");

                //RuleFor(c => c.Senha)
                //  .MinimumLength(6)
                //  .MaximumLength(100)
                //  .WithMessage("O campo senha precisa ter entre {2} e {1} caracteres");
            }

        }
    }
}
