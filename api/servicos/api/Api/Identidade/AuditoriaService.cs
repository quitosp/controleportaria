using Microsoft.EntityFrameworkCore;

namespace Api.Identidade;

public enum TipoEventoAuditoria
{
    LoginSucesso,
    LoginFalha,
    Logout,
    Registro,
    TrocaSenha,
    AdicaoRole,
    RemocaoRole,
    Exclusao,
}

public class AuditoriaService
{
    private readonly ILogger<AuditoriaService> _logger;

    public AuditoriaService(ILogger<AuditoriaService> logger) => _logger = logger;

    public void Registrar(TipoEventoAuditoria tipo, string usuarioEmail, string? ipAddress = null, string? detalhes = null)
    {
        // Log estruturado: ferramentas como Seq/Datadog/CloudWatch parseiam por nome de campo
        _logger.LogInformation("AUDIT {Tipo} usuario={Usuario} ip={Ip} detalhes={Detalhes}",
            tipo.ToString(), usuarioEmail, ipAddress ?? "?", detalhes ?? "");
    }
}
