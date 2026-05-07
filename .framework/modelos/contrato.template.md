# Contrato: {TITULO_HISTORIA}

**HIST**: HIST-NNN
**Tipo**: integration | automation | business-flow (sem UI) | authorization
**Categoria**: API externa | Webhook | Job agendado | Evento de dominio | Fluxo interno

## Objetivo
{1 frase: o que este contrato define}

## Disparo / Trigger
Como esta capacidade e ativada:
- [ ] Endpoint HTTP — `{METODO} {/rota}`
- [ ] Webhook recebido de — `{servico}` em `{/rota}`
- [ ] Job agendado — cron `{expressao}` ou intervalo `{tempo}`
- [ ] Evento de dominio — `{NomeEvento}` publicado por `{agregado}`
- [ ] Comando interno — chamada de outro modulo

## Entrada
```json
{
  "campo1": "string",
  "campo2": 123,
  "campo3": { "nested": true }
}
```

Validacao:
- `campo1`: obrigatorio, max 200 chars
- `campo2`: > 0
- `campo3.nested`: opcional

## Saida (em sucesso)
```json
{
  "success": true,
  "data": { "id": "uuid", "status": "processado" },
  "code": 200
}
```

## Saida (em erro)
| Codigo HTTP | Cenario | Mensagem |
|-------------|---------|----------|
| 400 | validacao falhou | "Campo X obrigatorio" |
| 404 | recurso nao existe | "Y nao encontrado" |
| 409 | conflito | "Ja processado" |
| 502 | servico externo indisponivel | "Tente novamente em 30s" |

## Fluxo (passos)
1. Receber entrada e validar (FluentValidation)
2. Buscar entidades relacionadas via repositorio
3. Aplicar regra de negocio
4. Persistir mudanca via UnitOfWork.Commit
5. Disparar evento `XConcluido` (se outros modulos precisam saber)
6. Retornar saida

## Side effects
- Tabelas alteradas: `{tabela1}`, `{tabela2}`
- Eventos publicados: `{Evento1}`, `{Evento2}`
- Logs estruturados emitidos: `audit_X`, `slow_query` (se aplicavel)
- Notificacoes enviadas: email/SMS/push para `{quem}`

## Idempotencia
Como evitar processamento duplicado (importante para webhooks/jobs):
- [ ] Chave idempotente: `{nome_campo}` (hash de entrada)
- [ ] Verifica `IdempotencyKey` antes de processar
- [ ] Outro: ____________

## Retry / Timeout
- Timeout: `{N segundos}`
- Retry: `{N tentativas}` com backoff `{linear|exponencial}`
- Falha permanente: registrar em tabela `FalhasProcessamento`

## Servicos externos (se integration)
- Nome: `{servico}`
- Endpoint: `{url}`
- Auth: `{Bearer/HMAC/OAuth}`
- Sandbox: `{url}`
- Rate limit: `{N req/min}`

## Aprovacao

- [ ] Entrada e saida tipadas
- [ ] Erros mapeados (400/404/409/...)
- [ ] Fluxo descrito em passos numerados
- [ ] Side effects listados
- [ ] Idempotencia tratada (se webhook/job)
- [ ] Timeout e retry definidos (se integration externa)

Quando todos checados: marcar `artefato.aprovado: true` no historia.yaml e prosseguir com `/impl HIST-NNN`.
