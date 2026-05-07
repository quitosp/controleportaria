# Templates C# adicionais — usar quando agregado puro nao basta

Para gerar agregado completo, use `csharp_scaffold.py`. Os templates abaixo cobrem casos especificos.

## Value Object

Quando: tipo imutavel sem identidade (Endereco, Cnpj, Dinheiro). Vai dentro de uma Entity.

```csharp
// Core/ObjetoDominio/ValueObjects/Cnpj.cs
namespace Core.ObjetoDominio.ValueObjects;

public sealed record Cnpj
{
    public string Valor { get; }

    public Cnpj(string valor)
    {
        valor = (valor ?? "").Replace(".","").Replace("/","").Replace("-","");
        if (valor.Length != 14 || !valor.All(char.IsDigit))
            throw new ArgumentException("CNPJ invalido");
        Valor = valor;
    }

    public override string ToString() => Convert.ToUInt64(Valor).ToString(@"00\.000\.000\/0000\-00");

    public static implicit operator string(Cnpj c) => c.Valor;
    public static explicit operator Cnpj(string s) => new(s);
}
```

Mapeamento EF (no Maps do agregado dono):
```csharp
builder.OwnsOne(e => e.Cnpj, cnpj => {
    cnpj.Property(c => c.Valor).HasColumnName("Cnpj").HasColumnType("varchar(14)");
});
```

## Enum

Quando: conjunto fechado e estavel de valores (StatusPedido, FormaPagamento).

```csharp
// Core/Enuns/EStatusPedido.cs
namespace Core.Enuns;

public enum EStatusPedido
{
    Pendente = 1,
    Pago = 2,
    Cancelado = 3,
    Concluido = 4,
}
```

Convencao:
- `E` prefixo
- Valores explicitos (nao deixar default)
- Em entidade: `public EStatusPedido Status { get; private set; }`
- Em mapping: nao precisa configurar (EF mapeia int automaticamente)
- Para Postgres com nome do enum em vez de int:
  ```csharp
  builder.Property(p => p.Status).HasConversion<string>().HasColumnType("varchar(20)");
  ```

## Integration Event

Quando: comunicar entre agregados ou entre microsservicos.

```csharp
// Dominios/Pedidos/Eventos/PedidoConfirmadoEvent.cs
using Core.Mensagens;

namespace Dominios.Pedidos.Eventos;

public class PedidoConfirmadoEvent : Event
{
    public Guid PedidoId { get; }
    public Guid ClienteId { get; }
    public decimal Valor { get; }

    public PedidoConfirmadoEvent(Guid pedidoId, Guid clienteId, decimal valor)
    {
        AggregateId = pedidoId;
        PedidoId = pedidoId;
        ClienteId = clienteId;
        Valor = valor;
    }
}
```

Disparo na entidade:
```csharp
public void Confirmar()
{
    Status = EStatusPedido.Pago;
    AdicionarEvento(new PedidoConfirmadoEvent(Id, ClienteId, Total));
}
```

Handler:
```csharp
// Dominios/Pedidos/Eventos/PedidoConfirmadoHandler.cs
public class PedidoConfirmadoHandler : INotificationHandler<PedidoConfirmadoEvent>
{
    private readonly IClienteRepositorio _clienteRepo;

    public PedidoConfirmadoHandler(IClienteRepositorio clienteRepo) => _clienteRepo = clienteRepo;

    public async Task Handle(PedidoConfirmadoEvent ev, CancellationToken ct)
    {
        // efeito colateral em outro agregado
    }
}
```

DI (em DependencyInjectionConfig):
```csharp
services.AddScoped<INotificationHandler<PedidoConfirmadoEvent>, PedidoConfirmadoHandler>();
```

## Background Worker

Quando: processamento periodico (limpeza, retry de webhook, sync).

```csharp
// Api/Workers/LimpezaTokensWorker.cs
public class LimpezaTokensWorker : BackgroundService
{
    private readonly IServiceProvider _sp;
    private readonly ILogger<LimpezaTokensWorker> _log;

    public LimpezaTokensWorker(IServiceProvider sp, ILogger<LimpezaTokensWorker> log)
    {
        _sp = sp; _log = log;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            using var scope = _sp.CreateScope();
            var ctx = scope.ServiceProvider.GetRequiredService<ContextoDB>();
            // operacao
            await Task.Delay(TimeSpan.FromHours(1), stoppingToken);
        }
    }
}
```

DI:
```csharp
services.AddHostedService<LimpezaTokensWorker>();
```

## Migration manual (sem entidade)

Quando: precisa criar funcao SQL, view, indice composto.

```bash
dotnet ef migrations add NomeDescritivo --project repositorios/Repositorios --startup-project servicos/api/Api
```

Depois editar o `.cs` da migration para adicionar SQL bruto:
```csharp
migrationBuilder.Sql(@"CREATE INDEX idx_pedidos_status_data ON ""Pedidos"" (""Status"", ""DataCadastro"");");
```
