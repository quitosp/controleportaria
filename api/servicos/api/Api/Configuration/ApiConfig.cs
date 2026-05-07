using Microsoft.EntityFrameworkCore;
using NetDevPack.Security.JwtSigningCredentials.AspNetCore;
using Repositorios.Contexto;
using System.Text.Json.Serialization;
using WebApi.Core.Middleware;
using WebAPI.Core.Identidade;
using Api.Middleware;

namespace Api.Configuration;

public static class ApiConfig
{
    public static void AddApiConfiguration(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddDbContext<ContextoDB>(options =>
            options.UseNpgsql(configuration.GetConnectionString("DefaultConnection")));

        services.AddControllers().AddJsonOptions(options =>
        {
            options.JsonSerializerOptions.ReferenceHandler = ReferenceHandler.IgnoreCycles;
            options.JsonSerializerOptions.WriteIndented = true;
        });

        // CORS: SetIsOriginAllowed + AllowCredentials e o que funciona com JWT em browser moderno.
        // Permitir todas as origens e incompativel com AllowCredentials Chrome bloqueia.
        // Em dev libera localhost:* (qualquer porta). Em prod, restrinja via appsettings > Cors:Origens.
        services.AddCors(options =>
        {
            options.AddPolicy("Total", builder => builder
                .SetIsOriginAllowed(origin =>
                {
                    if (string.IsNullOrEmpty(origin)) return false;
                    var configuradas = configuration.GetSection("Cors:Origens").Get<string[]>() ?? Array.Empty<string>();
                    if (configuradas.Contains(origin)) return true;
                    return origin.StartsWith("http://localhost:") || origin.StartsWith("https://localhost:");
                })
                .AllowAnyMethod()
                .AllowAnyHeader()
                .AllowCredentials());
        });
    }

    public static void UseApiConfiguration(this IApplicationBuilder app, IWebHostEnvironment env)
    {
        app.UseTratamentoErros();
        // HTTPS redirect SO em producao — em dev, redirect quebra preflight OPTIONS do CORS
        // (browser nao aceita 307 em preflight). Em dev voce roda na porta http normal.
        if (!env.IsDevelopment()) app.UseHttpsRedirection();
        app.UseSecurityHeaders();
        if (!env.IsDevelopment()) app.UseHsts();
        app.UseRouting();
        app.UseCors("Total");
        app.UseAuthConfiguration();
        app.UseRateLimiter();
        app.UseEndpoints(endpoints =>
        {
            endpoints.MapControllers();
            endpoints.MapHub<Api.Hubs.PainelChamadaHub>("/hubs/painel-chamada");
        });
        app.UseJwksDiscovery();
    }
}
