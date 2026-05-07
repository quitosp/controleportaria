using System.Net.Http.Json;
using System.Text.Json;

namespace Api.Integracoes;

// HIST-019 — Evolution API real (POST {urlBase}/message/sendText/{instancia}, Header: apikey)
// RN-011/RN-017 — falha NAO bloqueia fluxo; worker captura excecao e marca NotificacaoPendente.Falhou
public class EvolutionApiClient : IEvolutionApiClient
{
    private readonly HttpClient _http;

    public EvolutionApiClient(HttpClient http)
    {
        _http = http;
        _http.Timeout = TimeSpan.FromSeconds(15);
    }

    public async Task EnviarMensagem(string urlBase, string token, string instancia, string telefone, string mensagem, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(urlBase) || string.IsNullOrWhiteSpace(token))
            throw new InvalidOperationException("Evolution API nao configurada para esta unidade.");

        var url = $"{urlBase.TrimEnd('/')}/message/sendText/{Uri.EscapeDataString(instancia)}";
        var payload = new { number = telefone, text = mensagem };

        using var req = new HttpRequestMessage(HttpMethod.Post, url)
        {
            Content = JsonContent.Create(payload)
        };
        req.Headers.Add("apikey", token);

        using var resp = await _http.SendAsync(req, ct);
        if (!resp.IsSuccessStatusCode)
        {
            var body = await resp.Content.ReadAsStringAsync(ct);
            throw new HttpRequestException($"Evolution API {(int)resp.StatusCode}: {body}");
        }
    }
}
