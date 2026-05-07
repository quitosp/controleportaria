# Templates avançados C# (use sob demanda)

Continuação de [csharp-extras.md](csharp-extras.md). Templates para situações que aparecem quando o projeto cresce.

## 1. Data seeds (popular dados iniciais)

Quando: precisa popular roles, lookups (categorias, status), dados demo.

### Interface
```csharp
// Core/Data/ISeedData.cs
public interface ISeedData
{
    int Ordem { get; }            // menor primeiro
    Task ExecutarAsync(IServiceProvider sp, CancellationToken ct);
}
```

### Implementacao por dominio
```csharp
// Dominios/Categorias/Seed/CategoriasSeed.cs
public class CategoriasSeed : ISeedData
{
    public int Ordem => 100;

    public async Task ExecutarAsync(IServiceProvider sp, CancellationToken ct)
    {
        using var scope = sp.CreateScope();
        var ctx = scope.ServiceProvider.GetRequiredService<ContextoDB>();
        if (await ctx.Categorias.AnyAsync(ct)) return; // idempotente

        ctx.Categorias.AddRange(
            new Categoria("Eletronicos"),
            new Categoria("Roupas"),
            new Categoria("Alimentos"));
        await ctx.SaveChangesAsync(ct);
    }
}
```

### Runner em Program.cs
```csharp
public class Program
{
    public static async Task Main(string[] args)
    {
        var host = CreateHostBuilder(args).Build();

        await SeedAdmin.Executar(host.Services, "admin@local", "Admin@123", new[] { "admin" });

        // Roda todos os ISeedData em ordem
        using (var scope = host.Services.CreateScope())
        {
            var seeds = scope.ServiceProvider.GetServices<ISeedData>().OrderBy(s => s.Ordem);
            foreach (var seed in seeds) await seed.ExecutarAsync(host.Services, default);
        }

        await host.RunAsync();
    }
    // ...
}
```

DI:
```csharp
services.AddScoped<ISeedData, CategoriasSeed>();
services.AddScoped<ISeedData, StatusPedidoSeed>();
```

## 2. Multi-tenancy (TenantId em toda entidade)

Quando: SaaS B2B onde cada empresa cliente tem dados isolados.

### EntityTenant.cs (Core)
```csharp
public abstract class EntityTenant : Entity
{
    public Guid TenantId { get; set; }
}
```

### TenantAtual (request-scoped)
```csharp
// WebApi.Core/Tenant/ITenantAtual.cs
public interface ITenantAtual
{
    Guid? Id { get; }
    void Definir(Guid tenantId);
}

public class TenantAtual : ITenantAtual
{
    public Guid? Id { get; private set; }
    public void Definir(Guid tenantId) => Id = tenantId;
}
```

### Middleware extrai tenant do JWT/subdominio
```csharp
public class TenantMiddleware
{
    private readonly RequestDelegate _next;
    public TenantMiddleware(RequestDelegate next) => _next = next;

    public async Task InvokeAsync(HttpContext ctx, ITenantAtual tenant)
    {
        var claim = ctx.User?.FindFirst("tenant_id")?.Value;
        if (Guid.TryParse(claim, out var tid)) tenant.Definir(tid);
        // Alternativa: extrair de subdominio (acme.app.com -> tenant "acme")
        await _next(ctx);
    }
}
```

### Global Query Filter no ContextoDB
```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    // ... config existente ...

    foreach (var entityType in modelBuilder.Model.GetEntityTypes())
    {
        if (typeof(EntityTenant).IsAssignableFrom(entityType.ClrType))
        {
            var method = typeof(ContextoDB).GetMethod(nameof(AplicarFiltroTenant),
                System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Static);
            method!.MakeGenericMethod(entityType.ClrType).Invoke(null, new object[] { modelBuilder, _tenant });
        }
    }
}

private static void AplicarFiltroTenant<T>(ModelBuilder mb, ITenantAtual tenant) where T : EntityTenant
{
    mb.Entity<T>().HasQueryFilter(e => e.TenantId == (tenant.Id ?? Guid.Empty));
}
```

### Interceptor seta TenantId em SaveChanges
```csharp
public class TenantInterceptor : SaveChangesInterceptor
{
    private readonly ITenantAtual _tenant;
    public TenantInterceptor(ITenantAtual t) => _tenant = t;

    public override InterceptionResult<int> SavingChanges(DbContextEventData ed, InterceptionResult<int> result)
    {
        if (_tenant.Id is not Guid tid) return base.SavingChanges(ed, result);
        foreach (var entry in ed.Context!.ChangeTracker.Entries<EntityTenant>())
            if (entry.State == EntityState.Added && entry.Entity.TenantId == Guid.Empty)
                entry.Entity.TenantId = tid;
        return base.SavingChanges(ed, result);
    }
}
```

### DI + middleware
```csharp
services.AddScoped<ITenantAtual, TenantAtual>();
services.AddScoped<TenantInterceptor>();

app.UseAuthentication();
app.UseMiddleware<TenantMiddleware>();
app.UseAuthorization();
```

### Trade-offs
| Estrategia | Quando usar | Complexidade |
|------------|-------------|--------------|
| Row-level (TenantId) | A maioria dos casos | Baixa |
| Schema-per-tenant | Dados muito sensíveis | Média |
| Database-per-tenant | Compliance estrito (HIPAA) | Alta |

Default recomendado: row-level + global query filter.

## 3. Modularizacao (quando o projeto cresce)

Quando: > 20 agregados, equipes diferentes, contextos delimitados claros.

### De monolito Portaria para modular
Estrutura inicial (1 dominio):
```
dominios/Dominios/
├── Empresas/
├── Pedidos/
├── Estoque/
└── Clientes/
```

Modularizado:
```
modulos/
├── Vendas/
│   ├── Vendas.Dominio/
│   ├── Vendas.Repositorios/
│   └── Vendas.Api/        (registra controllers + handlers proprios)
├── Estoque/
│   ├── Estoque.Dominio/
│   ├── Estoque.Repositorios/
│   └── Estoque.Api/
├── Clientes/
│   └── ...
└── Compartilhados/        (Core + WebApi.Core)
```

### Cada modulo registra suas dependencias
```csharp
// Vendas.Api/Configuration/VendasModule.cs
public static class VendasModule
{
    public static IServiceCollection AddVendas(this IServiceCollection services)
    {
        services.AddScoped<IPedidoRepositorio, PedidoRepositorio>();
        services.AddScoped<IRequestHandler<SalvarPedidoEntrada, ComandResult>, PedidoCommandHandler>();
        // ...
        return services;
    }
}
```

API host registra todos:
```csharp
// servicos/api/Api/Startup.cs
services.AddVendas();
services.AddEstoque();
services.AddClientes();
```

### Comunicacao entre modulos
- **MediatR INotification** dentro do mesmo processo (sincrono ou async)
- **MessageBus** (RabbitMQ/Redis Pub-Sub) se modulos viram services separados depois
- **NUNCA** referenciar repositorio de outro modulo direto — sempre via evento ou contract publico

### Migration por modulo
Cada modulo tem suas migrations (com prefixo `Vendas_v1`, `Estoque_v1`). DbContext fica unico ou um por modulo (decisao por equipe).

### Quando NAO modularizar
- Solo dev: monolito Portaria escala bem ate ~30 agregados
- < 20 agregados: complexidade nao compensa
- Equipe < 3 devs: comunicacao supera fronteira

## 4. E2E tests (Playwright para Next.js)

Quando: aplicacao em uso real, regressoes visuais matam negocio.

### Setup
```bash
cd <projeto-web>
npm install -D @playwright/test
npx playwright install --with-deps chromium
```

### Estrutura
```
e2e/
├── auth.spec.ts        # login + acesso a rota privada
├── clientes.spec.ts    # criar + listar + editar
└── playwright.config.ts
```

### playwright.config.ts
```ts
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  use: {
    baseURL: process.env.BASE_URL ?? "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
  },
});
```

### auth.spec.ts (exemplo)
```ts
import { test, expect } from "@playwright/test";

test("login com credenciais default redireciona para /clientes", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel(/email/i).fill("admin@local");
  await page.getByLabel(/senha/i).fill("Admin@123");
  await page.getByRole("button", { name: /entrar/i }).click();
  await expect(page).toHaveURL(/clientes/);
  await expect(page.getByRole("heading", { name: /clientes/i })).toBeVisible();
});

test("rota privada sem token redireciona para /login", async ({ page, context }) => {
  await context.clearCookies();
  await page.goto("/clientes");
  await expect(page).toHaveURL(/login/);
});
```

### Workflow CI
```yaml
# .github/workflows/e2e.yml
name: E2E
on: [pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env: { POSTGRES_USER: postgres, POSTGRES_PASSWORD: postgres, POSTGRES_DB: e2e }
        ports: ["5432:5432"]
        options: --health-cmd pg_isready
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: "9.0.x" }
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - name: Start API
        run: |
          dotnet ef database update --project repositorios/Repositorios --startup-project servicos/api/Api
          nohup dotnet run --project servicos/api/Api &
          sleep 10
      - name: Install + run Playwright
        working-directory: pet-shop-web
        run: |
          npm ci
          npx playwright install --with-deps chromium
          npx playwright test
```

### Boas praticas
- Cada teste deve ser independente (limpar dados antes/depois ou usar transactions)
- Usar `data-testid` para selectors estaveis (em vez de classes/IDs que mudam)
- Page Object Pattern em features grandes
- Screenshots automaticos em falhas (Playwright faz por default)
