namespace Dominios.MovimentosPortaria.Entidades;

public enum CanalNotificacao { Whatsapp = 0, Email = 1, Socket = 2 }
public enum StatusNotificacao { Pendente = 0, Enviada = 1, Falhou = 2, Descartada = 3 }

public class NotificacaoPendente
{
    public Guid Id { get; set; }
    public Guid MovimentoPortariaId { get; set; }
    public CanalNotificacao Canal { get; set; }
    public string Destino { get; set; } = string.Empty;
    public string Payload { get; set; } = string.Empty;
    public StatusNotificacao Status { get; set; }
    public int Tentativas { get; set; }
    public DateTime? ProximaTentativa { get; set; }
    public string? UltimoErro { get; set; }
}
