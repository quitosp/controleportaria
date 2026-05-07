# Templates extras C# (use sob demanda)

Templates para situações que `csharp_scaffold.py` não gera por padrão. Copiar/adaptar.

## 1. Relacionamentos entre agregados (FK + navigation)

Quando: `Cliente` tem N `Veiculos`, ou `Pedido` tem 1 `Cliente`.

### 1:N (um cliente, varios veiculos)

**Veiculo.cs** (lado N):
```csharp
public class Veiculo : Entity
{
    public Veiculo(string nome, Guid clienteId) { Nome = nome; ClienteId = clienteId; }
    protected Veiculo() { }
    public string Nome { get; private set; } = "";
    public Guid ClienteId { get; private set; }
    public Cliente? Cliente { get; private set; } // navigation, opcional
}
```

**Cliente.cs** (lado 1):
```csharp
public class Cliente : Entity
{
    private readonly List<Veiculo> _veiculos = new();
    public IReadOnlyCollection<Veiculo> Veiculos => _veiculos.AsReadOnly();
    // ...
}
```

**VeiculoMaps.cs**:
```csharp
builder.HasOne(v => v.Cliente)
       .WithMany(c => c.Veiculos)
       .HasForeignKey(v => v.ClienteId)
       .OnDelete(DeleteBehavior.Restrict);
```

**VeiculoRepositorio.Listar com Include**:
```csharp
var query = _context.Veiculos.Include(v => v.Cliente).AsQueryable();
```

### N:N (Tag <-> Post)
Use entidade de junção explícita (`PostTag` com `PostId` + `TagId`) — preferível ao auto-gerado.

## 2. Filtros e sort dinâmicos (Specification pattern light)

Quando: lista precisa filtrar por múltiplos campos e ordenar por coluna.

### Filtro entrada
```csharp
public class FiltroVeiculo
{
    public string? Nome { get; set; }
    public Guid? ClienteId { get; set; }
    public DateTime? CriadoApos { get; set; }
    public string? OrdenarPor { get; set; } // nome | dataCadastro
    public bool Desc { get; set; } = false;
    public int PageIndex { get; set; } = 1;
    public int PageSize { get; set; } = 20;
}
```

### Repositorio.Listar dinâmico
```csharp
public async Task<PagedResult<VeiculoSaida>> Listar(FiltroVeiculo f)
{
    var q = _context.Veiculos.AsQueryable();

    if (!string.IsNullOrEmpty(f.Nome)) q = q.Where(v => v.Nome.Contains(f.Nome));
    if (f.ClienteId.HasValue) q = q.Where(v => v.ClienteId == f.ClienteId.Value);
    if (f.CriadoApos.HasValue) q = q.Where(v => v.DataCadastro >= f.CriadoApos.Value);

    q = f.OrdenarPor?.ToLower() switch
    {
        "nome" => f.Desc ? q.OrderByDescending(v => v.Nome) : q.OrderBy(v => v.Nome),
        "datacadastro" => f.Desc ? q.OrderByDescending(v => v.DataCadastro) : q.OrderBy(v => v.DataCadastro),
        _ => q.OrderByDescending(v => v.DataCadastro),
    };

    var total = await q.CountAsync();
    var lista = await q.Skip((f.PageIndex - 1) * f.PageSize).Take(f.PageSize)
        .Select(v => new VeiculoSaida { /*...*/ }).ToListAsync();
    return new PagedResult<VeiculoSaida> { List = lista, TotalResults = total, PageIndex = f.PageIndex, PageSize = f.PageSize };
}
```

### Controller
```csharp
[HttpGet("v1/listar")]
public async Task<PagedResult<VeiculoSaida>> Listar([FromQuery] FiltroVeiculo filtro)
    => await _repositorio.Listar(filtro);
```

## 3. Background job (IHostedService)

Quando: limpar dados antigos toda noite, processar fila, sincronizar com terceiro.

```csharp
// Api/Workers/LimpezaTokensWorker.cs
namespace Api.Workers;

public class LimpezaTokensWorker : BackgroundService
{
    private readonly IServiceProvider _sp;
    private readonly ILogger<LimpezaTokensWorker> _log;
    private readonly TimeSpan _intervalo = TimeSpan.FromHours(6);

    public LimpezaTokensWorker(IServiceProvider sp, ILogger<LimpezaTokensWorker> log)
    {
        _sp = sp; _log = log;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                using var scope = _sp.CreateScope();
                var ctx = scope.ServiceProvider.GetRequiredService<ContextoDB>();
                var expirados = ctx.RefreshTokens.Where(t => t.ExpirationDate < DateTime.UtcNow);
                ctx.RefreshTokens.RemoveRange(expirados);
                var n = await ctx.SaveChangesAsync(stoppingToken);
                _log.LogInformation("LimpezaTokens: {N} tokens removidos", n);
            }
            catch (Exception ex) { _log.LogError(ex, "Falha em LimpezaTokens"); }

            await Task.Delay(_intervalo, stoppingToken);
        }
    }
}
```

Registrar:
```csharp
// DependencyInjectionConfig.cs
services.AddHostedService<LimpezaTokensWorker>();
```

## 4. File upload helper

Quando: usuario envia foto/PDF/anexo.

### Controller
```csharp
[HttpPost("v1/upload")]
[RequestSizeLimit(10_000_000)] // 10 MB
public async Task<IComandResult> Upload(IFormFile arquivo)
{
    if (arquivo == null || arquivo.Length == 0)
        return new ComandResult(false, "Arquivo invalido", new List<string>(), 400);

    var permitidos = new[] { ".jpg", ".jpeg", ".png", ".pdf" };
    var ext = Path.GetExtension(arquivo.FileName).ToLowerInvariant();
    if (!permitidos.Contains(ext))
        return new ComandResult(false, "Extensao nao permitida", new List<string>(), 415);

    var nomeUnico = $"{Guid.NewGuid():N}{ext}";
    var dir = Path.Combine(_env.WebRootPath ?? "wwwroot", "uploads");
    Directory.CreateDirectory(dir);
    var caminho = Path.Combine(dir, nomeUnico);

    using (var stream = System.IO.File.Create(caminho))
        await arquivo.CopyToAsync(stream);

    return new ComandResult(true, "Upload OK", new { url = $"/uploads/{nomeUnico}" }, 200);
}
```

Para produção: usar S3/Azure Blob com `IFileStorage` interface.

## 5. Email service (template)

Quando: enviar boas-vindas, reset senha, notificacoes.

### Interface
```csharp
// Core/Services/IEmailService.cs
public interface IEmailService
{
    Task EnviarAsync(string para, string assunto, string corpoHtml);
}
```

### Implementacao SMTP simples
```csharp
public class EmailService : IEmailService
{
    private readonly EmailSettings _cfg;
    public EmailService(IOptions<EmailSettings> cfg) => _cfg = cfg.Value;

    public async Task EnviarAsync(string para, string assunto, string corpoHtml)
    {
        using var client = new System.Net.Mail.SmtpClient(_cfg.Host, _cfg.Port)
        {
            Credentials = new System.Net.NetworkCredential(_cfg.User, _cfg.Senha),
            EnableSsl = true,
        };
        var msg = new System.Net.Mail.MailMessage(_cfg.De, para, assunto, corpoHtml) { IsBodyHtml = true };
        await client.SendMailAsync(msg);
    }
}

public class EmailSettings { public string Host{get;set;}=""; public int Port{get;set;}=587; public string User{get;set;}=""; public string Senha{get;set;}=""; public string De{get;set;}=""; }
```

DI + appsettings:
```csharp
services.Configure<EmailSettings>(configuration.GetSection("Email"));
services.AddScoped<IEmailService, EmailService>();
```
```json
"Email": { "Host": "smtp.example.com", "Port": 587, "User": "...", "Senha": "...", "De": "noreply@app.com" }
```

Producao recomendada: SendGrid / Resend / AWS SES via SDK.

## 6. Cache wrapper (IMemoryCache)

Quando: lista frequente, dados que mudam pouco.

```csharp
// Core/Services/ICacheService.cs
public interface ICacheService
{
    Task<T> ObterOuCriar<T>(string chave, Func<Task<T>> factory, TimeSpan? expiracao = null);
    void Remover(string chave);
}
```

```csharp
public class CacheService : ICacheService
{
    private readonly IMemoryCache _cache;
    public CacheService(IMemoryCache cache) => _cache = cache;

    public async Task<T> ObterOuCriar<T>(string chave, Func<Task<T>> factory, TimeSpan? expiracao = null)
    {
        if (_cache.TryGetValue(chave, out T? cached) && cached != null) return cached;
        var valor = await factory();
        _cache.Set(chave, valor, expiracao ?? TimeSpan.FromMinutes(5));
        return valor;
    }

    public void Remover(string chave) => _cache.Remove(chave);
}
```

DI:
```csharp
services.AddMemoryCache();
services.AddScoped<ICacheService, CacheService>();
```

Uso:
```csharp
var lista = await _cache.ObterOuCriar(
    $"empresas:p{pageIndex}:s{pageSize}",
    () => _repo.Listar(pageIndex, pageSize),
    TimeSpan.FromMinutes(2));
```

Producao multi-instancia: trocar `IMemoryCache` por `IDistributedCache` (Redis).

## 7. Webhook receiver com HMAC

Quando: receber callbacks de Stripe, GitHub, Twilio.

```csharp
[HttpPost("v1/webhook/stripe")]
[AllowAnonymous]
public async Task<IActionResult> WebhookStripe()
{
    Request.EnableBuffering();
    var body = await new StreamReader(Request.Body).ReadToEndAsync();
    Request.Body.Position = 0;

    var assinatura = Request.Headers["Stripe-Signature"].ToString();
    var segredo = _config["Stripe:WebhookSecret"];
    if (!ValidarHmac(body, assinatura, segredo))
        return Unauthorized();

    var evento = JsonSerializer.Deserialize<JsonElement>(body);
    // processar evento
    return Ok();
}

private bool ValidarHmac(string payload, string assinaturaHeader, string segredo)
{
    using var hmac = new System.Security.Cryptography.HMACSHA256(Encoding.UTF8.GetBytes(segredo));
    var hash = Convert.ToHexString(hmac.ComputeHash(Encoding.UTF8.GetBytes(payload))).ToLowerInvariant();
    return assinaturaHeader.Contains(hash, StringComparison.OrdinalIgnoreCase);
}
```

## 8. i18n (.NET resources)

`Resources/Mensagens.pt-BR.resx`, `Mensagens.en-US.resx`. Em controllers:
```csharp
[Route("api/[controller]")]
public class XController : MainController
{
    private readonly IStringLocalizer<Mensagens> _t;
    public XController(IStringLocalizer<Mensagens> t) => _t = t;

    [HttpGet("v1/saudacao")]
    public string Hello() => _t["BemVindo"];
}
```

Configurar:
```csharp
services.AddLocalization(options => options.ResourcesPath = "Resources");
services.Configure<RequestLocalizationOptions>(o =>
{
    var supported = new[] { new CultureInfo("pt-BR"), new CultureInfo("en-US") };
    o.DefaultRequestCulture = new RequestCulture("pt-BR");
    o.SupportedCultures = supported; o.SupportedUICultures = supported;
});

app.UseRequestLocalization();
```
