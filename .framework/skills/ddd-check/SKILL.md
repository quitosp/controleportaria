---
name: ddd-check
description: Detecta agregados anemicos (so propriedades, zero comportamento). Sugere mover logica de Handler para metodos do agregado. Triggers: "/ddd-check", "ddd check", "agregados anemicos", "rich domain model".
---

# Skill: ddd-check

## Filosofia
Em DDD rico, o agregado (`Pedido`, `Conta`, `Cliente`) **encapsula comportamento**, nao so dados. Logica do tipo "validar transicao de estado", "calcular total", "aplicar desconto" pertence ao agregado, nao ao Handler.

Anti-pattern: agregado anemico
```csharp
public class Pedido {
    public Guid Id { get; set; }
    public string Status { get; set; }
    public decimal Total { get; set; }
    // 0 metodos
}

// Handler com toda logica:
public class AprovarPedidoHandler {
    public async Task Handle(...) {
        if (pedido.Status != "rascunho") throw new DominioException("...");
        pedido.Status = "aprovado";
        pedido.Total = pedido.Itens.Sum(x => x.Valor);
        ...
    }
}
```

Padrao saudavel: agregado rico
```csharp
public class Pedido {
    public Guid Id { get; private set; }
    public string Status { get; private set; }
    public decimal Total { get; private set; }
    private readonly List<ItemPedido> _itens = new();

    public void Aprovar() {
        if (Status != "rascunho") throw new DominioException("Pedido nao esta em rascunho");
        Status = "aprovado";
        Total = _itens.Sum(x => x.Valor);
    }
}

// Handler so orquestra:
public class AprovarPedidoHandler {
    public async Task Handle(...) {
        pedido.Aprovar();  // toda logica encapsulada
        await _repo.Alterar(pedido);
    }
}
```

## Acao

Rodar `python .framework/scripts/ddd_check.py --raiz <projeto>`. Esse script:

### 1. Detecta agregados anemicos
- Para cada classe em `Dominios/<X>/Entidades/<Y>.cs`:
  - Conta propriedades publicas (`public T X { get; set; }`)
  - Conta metodos publicos (excluindo Construtor)
  - Se metodos == 0 e propriedades > 3: marca como ANEMICO

### 2. Detecta logica que deveria estar no agregado
- Em handlers (`*Handler.cs`):
  - Encontra blocos que mutam multiplas propriedades de um agregado
  - Procura padroes: `entidade.X = ...; entidade.Y = ...; entidade.Z = ...`
  - Sugere extrair em metodo `entidade.MudarEstado()` ou similar

### 3. Detecta validacoes de regra que deveriam estar no agregado
- Validacoes em handler do tipo `if (entidade.Status != "X") throw ...` 
- Sugere mover para metodo `entidade.PodeAprovar()` retornando bool/exception

## Saida

```
ANEMICO  dominios/Dominios/Pedidos/Entidades/Pedido.cs:
         8 propriedades, 0 metodos. Considere extrair logica do AprovarPedidoHandler para Pedido.Aprovar().

LOGICA-NO-HANDLER  servicos/api/Api/Handlers/AprovarPedidoHandler.cs:42-48:
         Bloco muta 4 propriedades de Pedido. Considere encapsular em Pedido.Aprovar().

VALIDACAO-NO-HANDLER  servicos/api/Api/Handlers/CancelarPedidoHandler.cs:31:
         Validacao de estado externa ao agregado. Considere Pedido.PodeCancelar().
```

## Como interpretar
- `ANEMICO` em **agregados de cadastro simples** (ex: `Categoria`, `Tag`) e ACEITAVEL — esses sao realmente CRUD-only.
- `ANEMICO` em **agregados com regras de negocio** (mencionados em `documentacao/8-regras-negocio.md`) e **PROBLEMA** — refatorar.

## Restricoes
- NAO modifica codigo automaticamente (mudar agregado pode quebrar Maps, queries, scaffolds)
- Sugere refatoracao com exemplos
- Nao falha o gate por default (e diretiva, nao bloqueante)
