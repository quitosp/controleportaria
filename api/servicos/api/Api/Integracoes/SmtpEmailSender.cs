using System.Net;
using System.Net.Mail;
using Microsoft.Extensions.Configuration;

namespace Api.Integracoes;

// HIST-020 — Email via SMTP (default) ou SendGrid (futuro switch via config)
// Configuracao em appsettings: Email:Smtp:Host/Porta/Usuario/Senha/De/Provedor
public class SmtpEmailSender : IEmailSender
{
    private readonly IConfiguration _cfg;

    public SmtpEmailSender(IConfiguration cfg) => _cfg = cfg;

    public async Task Enviar(string para, string assunto, string corpo, CancellationToken ct)
    {
        var host = _cfg["Email:Smtp:Host"];
        if (string.IsNullOrWhiteSpace(host))
            throw new InvalidOperationException("Email SMTP nao configurado (Email:Smtp:Host vazio).");

        var porta = int.TryParse(_cfg["Email:Smtp:Porta"], out var p) ? p : 587;
        var usuario = _cfg["Email:Smtp:Usuario"] ?? "";
        var senha = _cfg["Email:Smtp:Senha"] ?? "";
        var de = _cfg["Email:Smtp:De"] ?? usuario;

        using var client = new SmtpClient(host, porta)
        {
            EnableSsl = true,
            Credentials = new NetworkCredential(usuario, senha)
        };
        using var msg = new MailMessage(de, para, assunto, corpo) { IsBodyHtml = false };
        await client.SendMailAsync(msg, ct);
    }
}
