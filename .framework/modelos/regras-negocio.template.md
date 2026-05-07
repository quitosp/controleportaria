# Regras de negocio

Regras invariaveis do dominio. Cada regra tem um ID (`RN-NNN`) que e citado nas historias, contratos e codigo (via comentario `// RN-NNN` no Handler/Service que a implementa).

## Formato

```
### RN-NNN — Nome curto da regra

- **Agregados envolvidos:** Pedido, Estoque
- **Gatilho:** ao [evento] (ex: ao aprovar Pedido)
- **Condicao:** [predicado verificavel] (ex: Pedido.itens.todos.estoque > 0)
- **Acao se violada:** [erro / ajuste / log] (ex: lanca DominioException("Item X sem estoque"))
- **Severidade:** critica | alta | media | baixa
- **Justificativa:** [opcional, motivo de negocio]
- **Implementada em:** [opcional, preenchido apos /impl] (ex: AprovarPedidoHandler:42)
```

## Exemplos por dominio

### Financeiro

#### RN-001 — Saldo nunca pode ficar negativo

- **Agregados envolvidos:** Conta, Movimento
- **Gatilho:** ao salvar Movimento do tipo "saida"
- **Condicao:** Conta.saldoAtual - Movimento.valor >= 0
- **Acao se violada:** lanca `DominioException("Saldo insuficiente")` (HTTP 400)
- **Severidade:** critica
- **Justificativa:** evita inconsistencia contabil; cliente nao pode gastar o que nao tem
- **Implementada em:** *(preenchido apos `/impl`)*

#### RN-002 — Transferencia entre contas e atomica

- **Agregados envolvidos:** Conta (origem), Conta (destino), Movimento
- **Gatilho:** ao iniciar transferencia
- **Condicao:** debito da origem E credito do destino acontecem na mesma transacao
- **Acao se violada:** rollback completo, nenhum movimento persistido
- **Severidade:** critica
- **Implementada em:** *(preenchido apos `/impl`)*

### E-commerce

#### RN-003 — Cliente VIP recebe desconto de 10% acima de R$ 500

- **Agregados envolvidos:** Pedido, Cliente
- **Gatilho:** ao calcular total do Pedido
- **Condicao:** Cliente.tipo == "VIP" E Pedido.subtotal >= 500
- **Acao:** aplica `desconto = subtotal * 0.10`
- **Severidade:** media
- **Justificativa:** politica de fidelidade definida pelo time comercial
- **Implementada em:** *(preenchido apos `/impl`)*

#### RN-004 — Pedido cancelado libera estoque reservado

- **Agregados envolvidos:** Pedido, Estoque
- **Gatilho:** ao mudar Pedido.status para "cancelado"
- **Condicao:** Pedido.status anterior in ["pago", "em_separacao"]
- **Acao:** incrementa `Estoque.disponivel` para cada ItemPedido
- **Severidade:** alta
- **Implementada em:** *(preenchido apos `/impl`)*

### Locacao / Reserva

#### RN-005 — Nao pode haver dupla reserva no mesmo horario

- **Agregados envolvidos:** Reserva, Recurso
- **Gatilho:** ao criar Reserva
- **Condicao:** nao existe outra Reserva ativa para o mesmo Recurso com horarios sobrepostos
- **Acao se violada:** lanca `ConflitoException("Horario ja reservado")` (HTTP 409)
- **Severidade:** critica
- **Implementada em:** *(preenchido apos `/impl`)*

---

## Como o framework usa este arquivo

1. **`/ideia`** te conduz pela rodada 3.5 (regras de negocio) e popula este arquivo a partir das suas respostas.
2. **`/historias`** ao gerar uma `HIST` de business-flow, lista os RN-NNN aplicaveis no campo `regras_negocio: [RN-001, RN-002]`.
3. **`/artefato`** inclui as regras no contrato (na secao "Validacoes") com os IDs.
4. **`/impl`** le os RN-NNN da historia, implementa cada validacao no Handler, e adiciona comentario `// RN-NNN` na linha que implementa.
5. **`/rev`** verifica que cada RN listada na historia tem comentario `// RN-NNN` no codigo. Se nao, falha gate.
6. **`/commit`** ao concluir, atualiza este arquivo preenchendo `Implementada em:` com o caminho real.
