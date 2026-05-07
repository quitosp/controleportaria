using Core.ObjetoDominio.Autorizacao;
using Dominios.Portarias.Entidades;
using Dominios.Unidades.Entidades;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using Repositorios.Contexto;
using WebApi.Core.Usuario;

namespace Api.Identidade;

public static class SeedAdmin
{
    public static async Task Executar(IServiceProvider sp, string email, string senha, string[] roles)
    {
        using var scope = sp.CreateScope();
        var userManager = scope.ServiceProvider.GetRequiredService<UserManager<Usuario>>();
        var roleManager = scope.ServiceProvider.GetRequiredService<RoleManager<IdentityRole>>();
        var ctx = scope.ServiceProvider.GetRequiredService<ContextoDB>();

        foreach (var role in roles)
            if (!await roleManager.RoleExistsAsync(role))
                await roleManager.CreateAsync(new IdentityRole(role));

        // Garante uma Unidade default
        var unidade = await ctx.Unidades.FirstOrDefaultAsync(u => u.Nome == "Frigoestrela");
        if (unidade is null)
        {
            unidade = new Unidade("Frigoestrela", null, null);
            ctx.Unidades.Add(unidade);
            await ctx.SaveChangesAsync();
        }

        // Garante uma Portaria default na unidade
        var portaria = await ctx.Portarias.FirstOrDefaultAsync(p => p.UnidadeId == unidade.Id);
        if (portaria is null)
        {
            portaria = new Portaria("Portaria 1", unidade.Id);
            ctx.Portarias.Add(portaria);
            await ctx.SaveChangesAsync();
        }

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
                Papel = PapelUsuario.Admin,
                UnidadeId = unidade.Id,
                PortariaPadraoId = portaria.Id
            };
            var result = await userManager.CreateAsync(user, senha);
            if (!result.Succeeded) return;
        }
        else
        {
            var atualizar = false;
            if (user.Papel != PapelUsuario.Admin) { user.DefinirPapel(PapelUsuario.Admin); atualizar = true; }
            if (user.UnidadeId != unidade.Id || user.PortariaPadraoId != portaria.Id)
            {
                user.DefinirUnidade(unidade.Id, portaria.Id);
                atualizar = true;
            }
            if (atualizar) await userManager.UpdateAsync(user);
        }

        foreach (var role in roles)
            if (!await userManager.IsInRoleAsync(user, role))
                await userManager.AddToRoleAsync(user, role);
    }
}
