using Core.ObjetoDominio;
using FluentValidation;
using FluentValidation.Results;

namespace Core.Usuarios.Comandos.Inputs
{
    public class UsuarioTrocarSenhaEntrada : Comand
    {
        public string Email { get; set; }

        public string SenhaAntiga { get; set; }
        public string SenhaNova { get; set; }

        public override bool EhValido()
        {
            ValidationResult = new UsuarioTrocarSenhaValidation().Validate(this);
            return ValidationResult.IsValid;
        }


        public class UsuarioTrocarSenhaValidation : AbstractValidator<UsuarioTrocarSenhaEntrada>
        {
            public UsuarioTrocarSenhaValidation()
            {

                RuleFor(c => c.Email)
                    .NotEmpty()
                    .WithMessage("O email não foi informado");

                RuleFor(c => c.Email)
                    .EmailAddress()
                    .WithMessage("O campo email está em formato inválido");

                RuleFor(c => c.SenhaAntiga)
                    .NotEmpty()
                    .WithMessage("A senha não foi informada");

                RuleFor(c => c.SenhaNova)
                .NotEmpty()
                .WithMessage("A senha novA não foi informada");

                //RuleFor(c => c.Senha)
                //  .MinimumLength(6)
                //  .MaximumLength(100)
                //  .WithMessage("O campo senha precisa ter entre {2} e {1} caracteres");
            }

        }
    }
}
