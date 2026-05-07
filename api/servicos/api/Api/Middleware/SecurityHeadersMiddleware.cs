using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;

namespace Api.Middleware;

public static class SecurityHeadersMiddleware
{
    public static IApplicationBuilder UseSecurityHeaders(this IApplicationBuilder app)
    {
        return app.Use(async (ctx, next) =>
        {
            ctx.Response.Headers["X-Content-Type-Options"] = "nosniff";
            ctx.Response.Headers["X-Frame-Options"] = "DENY";
            ctx.Response.Headers["Referrer-Policy"] = "strict-origin-when-cross-origin";
            ctx.Response.Headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()";
            ctx.Response.Headers["X-Permitted-Cross-Domain-Policies"] = "none";
            await next();
        });
    }
}
