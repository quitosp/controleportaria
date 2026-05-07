using Core.Data;
using Core.ObjetoDominio;
using FluentValidation.Results;

namespace Core.Mensagens
{
    public abstract class CommandHandler
    {
        protected ValidationResult ValidationResult;

        protected CommandHandler()
        {
            ValidationResult = new ValidationResult();
        }

        protected void AdicionarErro(string mensagem,string propriedade = null)
        {
            ValidationResult.Errors.Add(new ValidationFailure(propriedade, mensagem));
        }
        public void AdicionarErros(IEnumerable<ValidationFailure> errors)
        {
            foreach (var erro in errors)
            {
                AdicionarErro(erro.ErrorMessage);
            }
        }
        protected bool PossuiErros()
        {
            return ValidationResult.Errors.Count >= 1;
        }

        protected Core.ObjetoDominio.Data Errors(string titulo)
        {
            var erros = new List<Error>();
            var retorno = ValidationResult.Errors.Count >= 1;

            if (retorno)
            {
                
                foreach (var item in Erros())
                {
                    var error = new Error(titulo, item,"400");
                    erros.Add(error);
                }
            }

            var data = new Core.ObjetoDominio.Data(erros);

            return data;
        }

        protected List<string> Erros()
        {
            var lista = new List<string>();

            foreach (var erro in ValidationResult.Errors)
            {
                lista.Add(erro.ErrorMessage);
            }

            return lista;
        }

        protected List<string> Erros(ValidationResult v)
        {
            var lista = new List<string>();

            foreach (var erro in v.Errors)
            {
                lista.Add(erro.ErrorMessage);
            }

            return lista;
        }

        protected async Task<ComandResult> PersistirDados(IUnitOfWork uow,string mensagem,dynamic retorno = null,bool persistirDados = true,string propriedade = null)
        {
            if (persistirDados)
            {
                if (!await uow.Commit())
                {
                    AdicionarErro("Houve um erro ao persistir os dados",propriedade);

                    return new ComandResult(false, "Erro!!", Erros());
                }
            }

            return new ComandResult(true,mensagem,retorno);
        }
        protected async Task<ValidationResult> PersistirDados(IUnitOfWork uow)
        {
            if (!await uow.Commit()) AdicionarErro("Houve um erro ao persistir os dados");

            return ValidationResult;
        }
    }
}
