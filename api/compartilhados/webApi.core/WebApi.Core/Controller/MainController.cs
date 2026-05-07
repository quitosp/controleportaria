using Core.ObjetoDominio;
using FluentValidation.Results;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.ModelBinding;
using System.Text.Json;

namespace WebApi.Core.Controller
{
    [Route("api/[controller]")]
    [ApiController]
    public abstract class MainController : ControllerBase
    {
        protected ICollection<string> Erros = new List<string>();


        protected ComandResult CustomResponse(object result = null)
        {
            if (OperacaoValida())
            {
                return new ComandResult(true, "Ok", result);
            }

            return new ComandResult(false, "Mensagens", Erros.ToArray());

            //return BadRequest(new ValidationProblemDetails(new Dictionary<string, string[]>
            //{
            //    { "Mensagens", Erros.ToArray() }
            //}));
        }

        protected ComandResult CustomResponse(bool success, string mensagem,dynamic dados = null)
        {
            if (OperacaoValida())
            {
                return new ComandResult(success, mensagem,dados);
            }

            return new ComandResult(false, "Mensagens", Erros.ToArray());

            //return BadRequest(new ValidationProblemDetails(new Dictionary<string, string[]>
            //{
            //    { "Mensagens", Erros.ToArray() }
            //}));
        }

        protected ComandResult CustomResponse(ModelStateDictionary modelState)
        {
            var erros = modelState.Values.SelectMany(e => e.Errors);
            foreach (var erro in erros)
            {
                AdicionarErroProcessamento(erro.ErrorMessage);
            }

            return CustomResponse();
        }

        protected ComandResult CustomResponse(ValidationResult validationResult)
        {
            foreach (var erro in validationResult.Errors)
            {
                AdicionarErroProcessamento(erro.ErrorMessage);
            }

            return CustomResponse();
        }
        protected ComandResult CustomResponse(ValidationResult validationResult, string mensagem = null)
        {
            foreach (var erro in validationResult.Errors)
            {
                AdicionarErroProcessamento(erro.ErrorMessage);
            }

            if (OperacaoValida())
            {
                return new ComandResult(true, mensagem, null);
            }
            else
            {
                return new ComandResult(false, "Erro:", new { Erros });
            }
            // return CustomResponse();
        }

        protected bool OperacaoValida()
        {
            return !Erros.Any();
        }

        protected void AdicionarErroProcessamento(string erro)
        {
            Erros.Add(erro);
        }

        protected void LimparErrosProcessamento()
        {
            Erros.Clear();
        }
        protected async Task<dynamic> SerializarObjeto(dynamic objeto)
        {
            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            };

            return JsonSerializer.Serialize(await objeto, options);
        }
    }
}
