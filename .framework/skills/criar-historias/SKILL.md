---
name: criar-historias
description: Quebra arquitetura em historias atomicas, classificando cada uma como capacidade (8 tipos: crud, business-flow, integration, report, automation, authorization, architecture, refactor). Triggers: "/historias", "criar historias", "criar stories".
---

# Skill: criar-historias

## Filosofia
Historia = **capacidade do sistema**, nao apenas CRUD. Classificar por tipo define o fluxo de implementacao:
- `crud` → vai direto para `/impl` (sem artefato)
- demais tipos → exigem mockup ou contrato aprovado antes de `/impl`

## Entrada
- `estado/arquitetura.yaml`
- `estado/prd.yaml`
- `estado/ux.yaml` (opcional)
- `documentacao/3-personas.md` (opcional, gerado por `/ideia`) — fonte das personas para preencher campo `persona` em cada historia
- `documentacao/4-casos-de-uso.md` (opcional) — fonte do `motivo` ("para que")

## Acao
1. Ler arquitetura, PRD, UX. Se existir `documentacao/3-personas.md` e `4-casos-de-uso.md`, ler tambem.

2. **HIST-001**: sempre `tipo: architecture` — "Inicializar projeto" via `novo_projeto.py`.

3. **Para cada agregado em PRD/arquitetura**, gerar **2 categorias de historia** (nao apenas CRUD!):

   **3a. HIST de cadastro (`tipo: crud`)** — apenas para os 4 verbos basicos: salvar, alterar, listar, deletar.
   - Cria HIST-NNN.yaml:
     - tipo: crud
     - persona, motivo, valor_de_negocio (do caso de uso correspondente)
     - acao.comando: `python .framework/scripts/csharp_scaffold.py {S} --plural {P} --tudo`
     - dependencias: HIST-001

   **3b. HIST de business-flow (`tipo: business-flow`)** — para cada **verbo de dominio nao-CRUD** identificado em:
   - `documentacao/4-casos-de-uso.md` (acoes que nao sao salvar/alterar/listar/deletar)
   - `documentacao/5-modelagem.md` (transicoes de estado: aprovar, cancelar, pagar, enviar, devolver, ativar, desativar, transferir, aplicar)
   - `documentacao/8-regras-negocio.md` (cada RN com gatilho que nao e "salvar/listar")

   Exemplos de verbos que **sempre** viram business-flow (nunca CRUD):
   - **Pedido**: aprovar, cancelar, pagar, enviar, entregar, devolver, recalcular-total
   - **Conta**: transferir, congelar, descongelar, fechar
   - **Reserva**: confirmar, cancelar, remarcar, no-show
   - **Estoque**: reservar, liberar, ajustar, transferir-entre-depositos
   - **Cliente**: promover-para-vip, suspender, reativar
   - **Usuario**: trocar-senha, esquecer-senha, bloquear, desbloquear

   Cada HIST de business-flow tem:
   - tipo: business-flow
   - persona, motivo, valor_de_negocio
   - **regras_negocio**: lista dos `RN-NNN` (de `documentacao/8-regras-negocio.md`) que essa historia implementa/valida. Ex: `[RN-001, RN-005]`
   - artefato.tipo_artefato: `contrato` (obrigatorio antes do `/impl`)
   - dependencias: HIST do cadastro do agregado + HISTs de outros agregados que ela usa

**Regra para Claude**: NAO basta criar HIST crud para o agregado e parar ai. Olhar `documentacao/4-casos-de-uso.md` e `5-modelagem.md` SEMPRE pra extrair os verbos de dominio. Sistemas reais tem MAIS business-flow do que CRUD.

4. **Para cada feature em PRD > features_frontend ou ux.yaml > telas**:
   - tipo: `crud` (se for so listar+formulario simples) OU `business-flow` (se tem regra)
   - acao.comando: `python .framework/scripts/frontend_scaffold.py {feat} --tudo`
   - dependencias: HIST do agregado backend correspondente

5. **Para cada integracao em PRD > integracoes**:
   - tipo: `integration`
   - **Sem comando direto**: artefato (contrato) deve existir antes de implementar
   - dependencias: agregados afetados

6. **Para autenticacao/RBAC**:
   - HIST-NNN tipo: `authorization`
   - Se PRD tem `rbac.ativo: true`: criar historia para configurar policies

7. **Para relatorios/dashboards**:
   - tipo: `report`
   - artefato: mockup obrigatorio

8. **Para jobs/automacoes**:
   - tipo: `automation`
   - artefato: contrato obrigatorio

9. Salvar todas em `estado/historias/HIST-NNN.yaml`. Atualizar `projeto.yaml`:
   - fase: `historias`
   - historias_total: N
   - tipos_distribuicao: `{ crud: 5, business-flow: 2, integration: 1, ... }`

## Saida
- N arquivos `estado/historias/HIST-NNN.yaml` com `tipo` setado
- Tabela ao usuario:
  ```
  HIST-001  architecture  Inicializar projeto
  HIST-002  crud           Cadastro de Cliente
  HIST-003  business-flow  Aprovar pedido (precisa contrato)
  HIST-004  integration    Webhook Stripe (precisa contrato)
  HIST-005  report         Dashboard vendas (precisa mockup)
  ```
- Sugestao:
  - Para historias `crud` ou `architecture`: `/impl HIST-NNN`
  - Para outras: `/artefato HIST-NNN` (gera mockup/contrato) → `/aprovar HIST-NNN` → `/impl HIST-NNN`

## Regra de preenchimento de `persona` e `motivo`

| tipo | persona | motivo | valor_de_negocio |
|---|---|---|---|
| crud | obrigatorio | obrigatorio | recomendado |
| business-flow | obrigatorio | obrigatorio | recomendado |
| report | obrigatorio | obrigatorio | recomendado |
| authorization | obrigatorio | obrigatorio | opcional |
| integration (B2C visivel) | obrigatorio | obrigatorio | opcional |
| integration (server-to-server) | opcional | opcional | opcional |
| automation (que afeta usuario) | obrigatorio | obrigatorio | opcional |
| automation (limpeza/manutencao interna) | vazio | "manter saude do sistema" | opcional |
| architecture | vazio | vazio | vazio |
| refactor | vazio | "preparar terreno para X" | opcional |

**Token economy**: cada campo e UMA LINHA. Detalhe vive em `documentacao/`.

## Restricoes
- 1 historia = 1 commit logico
- NAO usar tipo generico "agregado" ou "feature" — sempre um dos 8 tipos
- NAO criar historias para refatoracao especulativa
- NAO escrever paragrafos em `persona`/`motivo` — Claude le `documentacao/3-personas.md` se precisar de profundidade
- Ordem: architecture → cruds simples → business-flows → integrations → reports → automation → telas frontend
- Se duvida no tipo, perguntar ao usuario
