using Serilog;
using Serilog.Context;

namespace Api.Middleware;

public static class RequestLoggingMiddleware
{
    public static IApplicationBuilder UseRequestLogging(this IApplicationBuilder app)
    {
        return app.UseSerilogRequestLogging(options =>
        {
            options.MessageTemplate = "HTTP {RequestMethod} {RequestPath} -> {StatusCode} em {Elapsed:0}ms";
            options.GetLevel = (ctx, _, ex) =>
                ex != null ? Serilog.Events.LogEventLevel.Error :
                ctx.Response.StatusCode >= 500 ? Serilog.Events.LogEventLevel.Error :
                ctx.Response.StatusCode >= 400 ? Serilog.Events.LogEventLevel.Warning :
                Serilog.Events.LogEventLevel.Information;
            options.EnrichDiagnosticContext = (diag, ctx) =>
            {
                diag.Set("UserId", ctx.User?.FindFirst("sub")?.Value ?? "anon");
                diag.Set("RemoteIp", ctx.Connection.RemoteIpAddress?.ToString() ?? "?");
            };
        });
    }
}
