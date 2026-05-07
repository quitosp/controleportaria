using Serilog;
using Api.Configuration;
using Api.Identidade;

namespace Api;

public class Program
{
    public static async Task Main(string[] args)
    {
        // permite Npgsql aceitar qualquer Kind (Utc/Local/Unspecified) em timestamp without time zone
        AppContext.SetSwitch("Npgsql.EnableLegacyTimestampBehavior", true);

        Log.Logger = new Serilog.LoggerConfiguration()
            .Enrich.FromLogContext()
            .WriteTo.Console(new Serilog.Formatting.Compact.CompactJsonFormatter())
            .CreateLogger();

        try
        {
            Log.Information("Iniciando API");
            var host = CreateHostBuilder(args).Build();
        await SeedAdmin.Executar(host.Services, "admin@local", "Admin@123", new[] { "admin" });
        await host.RunAsync();
        }
        catch (Exception ex) { Log.Fatal(ex, "Falha ao iniciar"); throw; }
        finally { Log.CloseAndFlush(); }
    }

    public static IHostBuilder CreateHostBuilder(string[] args) =>
        Host.CreateDefaultBuilder(args)
            .UseSerilog((ctx, cfg) => cfg.ReadFrom.Configuration(ctx.Configuration).Enrich.FromLogContext().Enrich.WithMachineName().Enrich.WithEnvironmentName().WriteTo.Console(new Serilog.Formatting.Compact.CompactJsonFormatter()).WriteTo.File(new Serilog.Formatting.Compact.CompactJsonFormatter(), "logs/api-.json", rollingInterval: Serilog.RollingInterval.Day, retainedFileCountLimit: 14))
            .ConfigureWebHostDefaults(webBuilder => webBuilder.UseStartup<Startup>());
}
