---
name: evoluir-arquitetura
description: Modulariza projeto Portaria quando cresce demais (>20 agregados). Divide em modulos verticais (Vendas, Estoque, Clientes) sem virar microservico. Triggers: "/evoluir", "modularizar", "muitos agregados", "como dividir o projeto".
---

# Skill: evoluir-arquitetura

## Quando aplicar
- > 20 agregados em `dominios/Dominios/`
- Equipes diferentes mexendo em pastas diferentes
- Arquivos crescendo: ContextoDB > 200 linhas, DI > 300 linhas
- Build lento (> 30s)
- Contextos delimitados claros (Vendas, Estoque, Clientes nao se cruzam muito)

## Quando NAO aplicar
- Solo dev — monolito Portaria escala ate ~30 agregados sem dor
- < 15 agregados
- Time < 3 devs
- Sem fronteiras claras entre dominios

## Acao

### 1. Identificar bounded contexts
Listar agregados e agrupar por contexto:
```
Vendas: Pedido, ItemPedido, Pagamento, Cupom
Estoque: Produto, Categoria, Movimento, Inventario
Clientes: Cliente, Endereco, Contato
Compartilhado: Usuario, Auditoria
```

### 2. Estrutura modular
```
modulos/
├── Vendas/
│   ├── Vendas.Dominio/         (csproj)
│   ├── Vendas.Repositorios/    (csproj, ContextoVendas opcional)
│   └── Vendas.Api/             (csproj)
├── Estoque/
│   ├── Estoque.Dominio/
│   ├── Estoque.Repositorios/
│   └── Estoque.Api/
├── Clientes/
│   └── ...
└── Compartilhados/             (Core + WebApi.Core)

servicos/api/Api/                 (host: importa modulos como referencia)
```

### 3. Cada modulo tem seu Module Registration
```csharp
public static class VendasModule
{
    public static IServiceCollection AddVendas(this IServiceCollection services)
    {
        services.AddScoped<IPedidoRepositorio, PedidoRepositorio>();
        // ... handlers + repos do Vendas
        return services;
    }
}
```

API host:
```csharp
services.AddVendas();
services.AddEstoque();
services.AddClientes();
```

### 4. Comunicacao entre modulos
- **Mesmo processo**: MediatR `INotificationHandler<T>` em outro modulo escuta evento de domain
- **Distribuido (futuro)**: trocar para MessageBus (RabbitMQ, Redis Pub/Sub)
- **NUNCA** referenciar repositorio de outro modulo direto

Exemplo:
```csharp
// Vendas/Domain: dispara evento ao confirmar pedido
public class PedidoConfirmadoEvent : INotification
{
    public Guid PedidoId { get; }
    public Guid ClienteId { get; }
}

// Estoque/Application: ouve e baixa estoque
public class BaixarEstoqueAoConfirmarPedido : INotificationHandler<PedidoConfirmadoEvent>
{
    public async Task Handle(PedidoConfirmadoEvent ev, CancellationToken ct) { /* ... */ }
}
```

### 5. DbContext: unico ou multiplos?
- **Unico ContextoDB compartilhado**: simples, ainda funciona com global query filter por modulo (TenantId / ModuloId), migration unica
- **Um por modulo**: isolamento real, mas precisa coordenar transactions e migrations. So vale com >50 agregados.

Default recomendado: unico DbContext + filtros por modulo se necessario.

### 6. Migration plan
1. Criar pasta `modulos/Vendas/`
2. Mover pasta `dominios/Dominios/Pedidos/` para `modulos/Vendas/Vendas.Dominio/Pedidos/`
3. Atualizar namespaces (`Vendas.Dominio.Pedidos.Entidades`)
4. Mover Maps + Repositorios correspondentes
5. Criar `VendasModule.cs` com registros DI
6. Substituir registros em `DependencyInjectionConfig.cs` por `services.AddVendas()`
7. `dotnet build` — corrigir imports

Repetir por modulo. **NAO fazer tudo num PR so** — um modulo de cada vez.

## Saida
- Estrutura modular criada
- API host com `services.AddVendas()` etc.
- Build passa
- Histórias futuras citam qual modulo

## Restricoes
- NAO modularizar prematuramente — solo dev quase nunca precisa
- NAO transformar em microservicos sem necessidade real (multi-team, deploy independente)
- Migracao deve ser incremental, modulo por modulo
- Manter ContextoDB unico ate dor real aparecer
- Sempre documentar bounded contexts no README

## Quando virar microservico
Quando todos verdadeiros:
- Equipes geograficamente separadas
- Deploy precisa ser independente
- Escala diferente por modulo
- > 100k req/min em algum modulo

Senao: monolito modular e o sweet spot. Veja [csharp-extras-avancado.md §3](../../modelos/csharp-extras-avancado.md).
