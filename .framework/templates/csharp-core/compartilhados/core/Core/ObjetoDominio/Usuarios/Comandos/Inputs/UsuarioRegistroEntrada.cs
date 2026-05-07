using Core.ObjetoDominio;
using FluentValidation;

namespace Core.Usuarios.Comandos.Inputs
{
    public class UsuarioRegistroEntrada : Comand
    {

        public string Nome { get; set; }

        public string Email { get; set; }
        public string SenhaConfirmacao { get; set; }
        public string Senha { get; set; }

        public string[] RolesNames { get; set; }


        public override bool EhValido()
        {
            ValidationResult = new UsuarioRegistroValidation().Validate(this);
            return ValidationResult.IsValid;
        }

        public class UsuarioRegistroValidation : AbstractValidator<UsuarioRegistroEntrada>
        {
            public UsuarioRegistroValidation()
            {
                //RuleFor(c => c.ClienteId)
                //    .NotEqual(Guid.Empty)
                //    .WithMessage("Id do cliente inválido");

                RuleFor(c => c.Nome)
                    .NotEmpty()
                    .WithMessage("O nome não foi informado");

                //RuleFor(c => c.NomeUsuario)
                //   .NotEmpty()
                //   .WithMessage("O nome de usuário não foi informado");

                RuleFor(c => c.Email)
                    .NotEmpty()
                    .WithMessage("O email não foi informado!");

                RuleFor(c => c.Email)
                    .MaximumLength(256)
                    .WithMessage("O email deve ter no máximo 256 caracter!");

                RuleFor(c => c.Email)
                    .EmailAddress()
                    .WithMessage("O campo email está em formato inválido!");

                RuleFor(c => c.Senha)
                    .NotEmpty()
                    .WithMessage("A senha não foi informada!");

                RuleFor(c => c.Senha)
                  .MinimumLength(6)
                  .MaximumLength(100)
                  .WithMessage("O campo senha precisa ter entre {1} e {2} caracteres!");
            }

        }
    }
}
