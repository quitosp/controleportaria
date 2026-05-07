using Api.Configuration;
using Microsoft.AspNetCore.Mvc;
using WebAPI.Core.Identidade;
using Api.Middleware;
using Microsoft.AspNetCore.RateLimiting;

namespace Api;

public class Startup
{
    public IConfiguration Configuration { get; }

    public Startup(IHostEnvironment hostEnvironment)
    {
        var builder = new ConfigurationBuilder()
            .SetBasePath(hostEnvironment.ContentRootPath)
            .AddJsonFile("appsettings.json", true, true)
            .AddJsonFile($"appsettings.{hostEnvironment.EnvironmentName}.json", true, true)
            .AddEnvironmentVariables();

        if (hostEnvironment.IsDevelopment()) builder.AddUserSecrets<Startup>();
        Configuration = builder.Build();
    }

    public void ConfigureServices(IServiceCollection services)
    {
        services.AddIdentityConfiguration(Configuration);
        services.AddApiConfiguration(Configuration);
        services.AddJwtConfiguration(Configuration);
        services.AddAuthorizationConfiguration();
        services.AddSwaggerConfiguration();
        services.AddRateLimitConfiguration();
        services.AddHealthCheckConfiguration(Configuration);
        services.AddSignalRConfiguration();

        var handlers = AppDomain.CurrentDomain.Load("Dominios");
        services.AddMediatR(cfg => cfg.RegisterServicesFromAssemblies(handlers));

        services.RegisterServices();

        services.Configure<ApiBehaviorOptions>(options =>
        {
            options.SuppressModelStateInvalidFilter = true;
        });
    }

    public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
    {
        app.UseSwaggerConfiguration();
        app.UseApiConfiguration(env);
        app.UseStaticFiles();
        app.UseHealthCheckConfiguration();
        app.UseRequestLogging();
    }
}
