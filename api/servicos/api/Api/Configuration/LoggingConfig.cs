using Serilog;
using Serilog.Events;
using Serilog.Formatting.Compact;

namespace Api.Configuration;

public static class LoggingConfig
{
    public static void ConfigurarSerilog(this WebApplicationBuilder builder)
    {
        builder.Host.UseSerilog((ctx, services, cfg) =>
        {
            cfg.ReadFrom.Configuration(ctx.Configuration)
               .ReadFrom.Services(services)
               .Enrich.FromLogContext()
               .Enrich.WithMachineName()
               .Enrich.WithEnvironmentName()
               .MinimumLevel.Information()
               .MinimumLevel.Override("Microsoft.AspNetCore", LogEventLevel.Warning)
               .MinimumLevel.Override("Microsoft.EntityFrameworkCore", LogEventLevel.Warning)
               .WriteTo.Console(new CompactJsonFormatter())
               .WriteTo.File(new CompactJsonFormatter(),
                             "logs/api-.json",
                             rollingInterval: RollingInterval.Day,
                             retainedFileCountLimit: 14);
        });
    }
}
