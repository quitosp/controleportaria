using Core.ObjetoDominio.Autorizacao;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.SignalR;

namespace Api.Hubs;

[Authorize(Policy = PoliticasAuth.PorteiroOuMaior)]
public class PainelChamadaHub : Hub
{
    public async Task EntrarGrupoUnidade(string unidadeId)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, $"unidade:{unidadeId}");
    }

    public async Task SairGrupoUnidade(string unidadeId)
    {
        await Groups.RemoveFromGroupAsync(Context.ConnectionId, $"unidade:{unidadeId}");
    }
}
