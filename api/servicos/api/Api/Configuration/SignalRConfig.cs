using Api.Hubs;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;

namespace Api.Configuration;

public static class SignalRConfig
{
    public static IServiceCollection AddSignalRConfiguration(this IServiceCollection services)
    {
        services.AddSignalR();
        return services;
    }

    public static IApplicationBuilder UseSignalRConfiguration(this IApplicationBuilder app)
    {
        return app.UseEndpoints(e => e.MapHub<PainelChamadaHub>("/hubs/painel-chamada"));
    }
}
