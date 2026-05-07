# Templates EntityAuditable + Interceptor (C# Portaria)

Quando aplicar: agregados que precisam rastrear quem criou e quem alterou (LGPD, SOC2, debug em produção).

## Como ativar
1. Adicionar `EntityAuditable.cs` no Core (uma vez por projeto)
2. Adicionar `AuditoriaInterceptor.cs` no Repositorios (uma vez por projeto)
3. Registrar o interceptor no `ContextoDB.OnConfiguring`
4. Para agregados auditaveis: scaffold com `--auditavel` (entidade herda `EntityAuditable` em vez de `Entity`)

## EntityAuditable.cs (Core/ObjetoDominio/)
```csharp
namespace Core.ObjetoDominio;

public abstract class EntityAuditable : Entity
{
    public Guid? CriadoPor { get; set; }
    public DateTime? CriadoEm { get; set; }
    public Guid? AlteradoPor { get; set; }
    public DateTime? AlteradoEm { get; set; }
}
```

## AuditoriaInterceptor.cs (Repositorios/Contexto/)
```csharp
using Core.ObjetoDominio;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.ChangeTracking;
using Microsoft.EntityFrameworkCore.Diagnostics;
using WebApi.Core.Usuario;

namespace Repositorios.Contexto;

public class AuditoriaInterceptor : SaveChangesInterceptor
{
    private readonly IAspNetUser _user;

    public AuditoriaInterceptor(IAspNetUser user) => _user = user;

    public override InterceptionResult<int> SavingChanges(DbContextEventData eventData, InterceptionResult<int> result)
    {
        Aplicar(eventData.Context);
        return base.SavingChanges(eventData, result);
    }

    public override ValueTask<InterceptionResult<int>> SavingChangesAsync(DbContextEventData eventData, InterceptionResult<int> result, CancellationToken ct = default)
    {
        Aplicar(eventData.Context);
        return base.SavingChangesAsync(eventData, result, ct);
    }

    private void Aplicar(DbContext? ctx)
    {
        if (ctx is null) return;
        var userId = _user.EstaAutenticado() ? _user.ObterUserId() : (Guid?)null;
        var agora = DateTime.UtcNow;
        foreach (var entry in ctx.ChangeTracker.Entries<EntityAuditable>())
        {
            if (entry.State == EntityState.Added)
            {
                entry.Entity.CriadoPor = userId;
                entry.Entity.CriadoEm = agora;
            }
            if (entry.State == EntityState.Modified)
            {
                entry.Entity.AlteradoPor = userId;
                entry.Entity.AlteradoEm = agora;
            }
        }
    }
}
```

## Registrar no ContextoDB
```csharp
// ContextoDB.cs
private readonly AuditoriaInterceptor? _auditoriaInterceptor;

public ContextoDB(DbContextOptions<ContextoDB> options, IMediatorHandler mediator, AuditoriaInterceptor? auditoria = null) : base(options)
{
    _mediatorHandler = mediator;
    _auditoriaInterceptor = auditoria;
    // ...
}

protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
{
    if (_auditoriaInterceptor != null)
        optionsBuilder.AddInterceptors(_auditoriaInterceptor);
    base.OnConfiguring(optionsBuilder);
}
```

## DI (DependencyInjectionConfig.cs)
```csharp
services.AddScoped<AuditoriaInterceptor>();
```

## Maps de entidade auditavel
```csharp
public class EmpresaMaps : IEntityTypeConfiguration<Empresa>
{
    public void Configure(EntityTypeBuilder<Empresa> builder)
    {
        builder.HasKey(l => l.Id);
        builder.Property(l => l.Id).ValueGeneratedOnAdd().HasColumnName("EmpresaId");
        builder.Property(l => l.Nome).IsRequired().HasColumnType("varchar(200)");
        // colunas auditaveis ja sao mapeadas automaticamente por EF Core
    }
}
```

## Migration
Apos primeira aplicacao, gerar migration:
```bash
python .framework/scripts/migrate.py
```
A migration alterar todas as tabelas que herdam EntityAuditable adicionando 4 colunas.
