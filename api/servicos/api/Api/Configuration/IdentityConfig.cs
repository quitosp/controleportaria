using Api.Identidade.Extensions;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Repositorios.Contexto;
using WebApi.Core.Usuario;

namespace Api.Configuration
{
    public static class IdentityConfig
    {
        public static IServiceCollection AddIdentityConfiguration(this IServiceCollection services,
            IConfiguration configuration)
        {
            var appSettingsSection = configuration.GetSection("AppTokenSettings");
            services.Configure<AppTokenSettings>(appSettingsSection);

            services.Configure<IdentityOptions>(options =>
            {
                // Default Password settings.
                options.Password.RequireDigit = true;
                options.Password.RequireLowercase = true;
                options.Password.RequireNonAlphanumeric = true;
                options.Password.RequireUppercase = true;
                options.Password.RequiredLength = 8;
                options.Password.RequiredUniqueChars = 0;
                options.User.AllowedUserNameCharacters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._@+/ ";
                options.Lockout.MaxFailedAccessAttempts = 5;
                options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(15);
                options.Lockout.AllowedForNewUsers = true;
            });

            services.AddJwksManager()
                .PersistKeysToDatabaseStore<ContextoDB>();

            services.AddDbContext<ContextoDB>(options =>
                options.UseNpgsql(configuration.GetConnectionString("DefaultConnection")));

            services.AddDefaultIdentity<Usuario>()
                .AddRoles<IdentityRole>()
                .AddErrorDescriber<IdentityMensagensPortugues>()
                .AddEntityFrameworkStores<ContextoDB>()
                .AddDefaultTokenProviders();

            return services;
        }
    }
}
