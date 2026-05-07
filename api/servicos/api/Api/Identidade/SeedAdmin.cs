using Core.ObjetoDominio.Autorizacao;
using Microsoft.AspNetCore.Identity;
using WebApi.Core.Usuario;

namespace Api.Identidade;

public static class SeedAdmin
{
    public static async Task Executar(IServiceProvider sp, string email, string senha, string[] roles)
    {
        using var scope = sp.CreateScope();
        var userManager = scope.ServiceProvider.GetRequiredService<UserManager<Usuario>>();
        var roleManager = scope.ServiceProvider.GetRequiredService<RoleManager<IdentityRole>>();

        foreach (var role in roles)
            if (!await roleManager.RoleExistsAsync(role))
                await roleManager.CreateAsync(new IdentityRole(role));

        var user = await userManager.FindByEmailAsync(email);
        if (user is null)
        {
            user = new Usuario
            {
                UserName = email,
                Email = email,
                EmailConfirmed = true,
                Nome = "Admin",
                SobreNome = "Sistema",
                Papel = PapelUsuario.Admin
            };
            var result = await userManager.CreateAsync(user, senha);
            if (!result.Succeeded) return;
        }
        else if (user.Papel != PapelUsuario.Admin)
        {
            user.DefinirPapel(PapelUsuario.Admin);
            await userManager.UpdateAsync(user);
        }

        foreach (var role in roles)
            if (!await userManager.IsInRoleAsync(user, role))
                await userManager.AddToRoleAsync(user, role);
    }
}
