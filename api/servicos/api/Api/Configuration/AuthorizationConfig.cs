using Core.ObjetoDominio.Autorizacao;
using Microsoft.AspNetCore.Authorization;

namespace Api.Configuration;

public static class AuthorizationConfig
{
    // RN-001 — toda operacao exige usuario autenticado (atributo [Authorize] herdado pelas policies abaixo)
    // RN-014 — multi-tenant: claim unidadeId consumida pelo IUnidadeContext
    // RN-021 — edicao critica pos-NoPateoInterno exige LiderOuMaior (validado no Handler do MovimentoPortaria)
    public static IServiceCollection AddAuthorizationConfiguration(this IServiceCollection services)
    {
        services.AddAuthorization(options =>
        {
            options.AddPolicy(PoliticasAuth.PorteiroOuMaior, p =>
                p.RequireAuthenticatedUser()
                 .RequireAssertion(c => PossuiPapel(c.User, PapelUsuario.Porteiro)));

            options.AddPolicy(PoliticasAuth.LiderOuMaior, p =>
                p.RequireAuthenticatedUser()
                 .RequireAssertion(c => PossuiPapel(c.User, PapelUsuario.Lider)));

            options.AddPolicy(PoliticasAuth.SupervisorOuMaior, p =>
                p.RequireAuthenticatedUser()
                 .RequireAssertion(c => PossuiPapel(c.User, PapelUsuario.Supervisor)));

            options.AddPolicy(PoliticasAuth.SomenteAdmin, p =>
                p.RequireAuthenticatedUser()
                 .RequireAssertion(c => PossuiPapel(c.User, PapelUsuario.Admin)));
        });

        return services;
    }

    private static bool PossuiPapel(System.Security.Claims.ClaimsPrincipal user, PapelUsuario minimo)
    {
        var claim = user.FindFirst(PoliticasAuth.ClaimPapel)?.Value;
        if (string.IsNullOrEmpty(claim)) return false;
        if (!Enum.TryParse<PapelUsuario>(claim, ignoreCase: true, out var papelDoUsuario)) return false;
        return papelDoUsuario >= minimo;
    }
}
