using System.Net;
using System.Text.Json;
using Core.Exeptions;
using Core.ObjetoDominio;
using FluentValidation;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

namespace WebApi.Core.Middleware;

public class ExceptionMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ExceptionMiddleware> _log;

    public ExceptionMiddleware(RequestDelegate next, ILogger<ExceptionMiddleware> log)
    {
        _next = next;
        _log = log;
    }

    public async Task Invoke(HttpContext ctx)
    {
        try
        {
            await _next(ctx);
        }
        catch (ValidationException ex)
        {
            await Escrever(ctx, HttpStatusCode.BadRequest, "Validacao falhou",
                ex.Errors.Select(e => e.ErrorMessage).ToList());
        }
        catch (ApiException ex)
        {
            await Escrever(ctx, ex.StatusCode, ex.Message, new List<string>());
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Erro nao tratado em {Path}", ctx.Request.Path);
            var detalhe = ctx.RequestServices.GetService<IHostEnvironment>()?.IsDevelopment() == true
                ? new List<string> { ex.Message }
                : new List<string>();
            await Escrever(ctx, HttpStatusCode.InternalServerError, "Erro interno", detalhe);
        }
    }

    private static async Task Escrever(HttpContext ctx, HttpStatusCode status, string mensagem, List<string> erros)
    {
        if (ctx.Response.HasStarted) return;
        ctx.Response.Clear();
        ctx.Response.StatusCode = (int)status;
        ctx.Response.ContentType = "application/json";
        var body = new ComandResult(false, mensagem, erros, (int)status);
        await ctx.Response.WriteAsync(JsonSerializer.Serialize(body, new JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.CamelCase }));
    }
}

public static class ExceptionMiddlewareExtensions
{
    public static IApplicationBuilder UseTratamentoErros(this IApplicationBuilder app)
        => app.UseMiddleware<ExceptionMiddleware>();
}
