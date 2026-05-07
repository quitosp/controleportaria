---
name: criar-artefato
description: Gera mockup (visual) ou contrato (api/fluxo/evento) para uma historia tipo != crud, ANTES da implementacao. Triggers: "/artefato HIST-NNN", "criar mockup", "criar contrato", "wireframe da historia".
---

# Skill: criar-artefato

## Filosofia (kitocode)
Capacidades nao-CRUD (business-flow, integration, report, automation, authorization) precisam ser **visualizadas/contratualizadas antes de codar**. Reduz retrabalho — token mais caro de todos.

## Quando aplicar
- Historia com `tipo` != `crud` esta `pendente`
- Antes de `/impl HIST-NNN` ser executado
- Skill `criar-historias` ja sinalizou que precisa de artefato

## Decidir mockup vs contrato

| Tipo da historia | Artefato gerado |
|------------------|-----------------|
| `business-flow` com UI | mockup (wireframe ASCII) |
| `business-flow` sem UI | contrato (passos do fluxo) |
| `integration` | contrato (API externa, webhook) |
| `report` | mockup (layout + dados de exemplo) |
| `automation` | contrato (trigger, idempotencia, retry) |
| `authorization` | contrato (matriz de permissoes) |
| `architecture` | contrato (decisao + diagrama ASCII) |
| `refactor` | contrato (antes/depois + plano de migracao) |

## Acao
1. Ler `estado/historias/HIST-NNN.yaml` — extrair `persona`, `motivo`, `valor_de_negocio`, `tipo`, `aceite`, **`regras_negocio[]`**
2. Ler `prd.yaml` para contexto. Se existir `documentacao/3-personas.md`, ler o bloco da persona desta historia. Se existir `documentacao/8-regras-negocio.md`, ler os blocos das RNs listadas.
3. Carregar template apropriado:
   - mockup: `.framework/modelos/mockup.template.md`
   - contrato: `.framework/modelos/contrato.template.md`
4. Preencher placeholders com dados da historia + PRD. **Usar persona/motivo para decidir:**
   - **mockup**: campos mais relevantes pra persona ficam no topo, linguagem coerente com o perfil (ex: "Cliente final" usa termos simples, "Admin" pode ter colunas tecnicas como ID, status interno)
   - **contrato (business-flow/integration)**: validacoes priorizam o cenario da persona (ex: persona=Cliente significa validar dados pessoais + pagamento; persona=Backoffice significa validar permissoes + auditoria)
   - **contrato (report)**: KPIs e filtros refletem o que a persona quer responder ("para que" do motivo)
   - **contrato (authorization)**: matriz tem coluna pra cada persona definida em `documentacao/3-personas.md`
5. No topo do artefato, escrever bloco de contexto + regras aplicaveis:
   ```
   ## Contexto
   **Persona:** Cliente final
   **Motivo:** acompanhar entrega do pedido para saber quando vai chegar

   ## Regras de negocio aplicaveis
   - **RN-004** — Pedido cancelado libera estoque reservado (ler doc completa em documentacao/8-regras-negocio.md)
   - **RN-007** — Status so pode regredir se admin autorizar
   ```
   Cada RN aparece com ID + nome curto. O `/impl` depois implementa cada uma com `// RN-NNN` no codigo.
6. Salvar em `estado/artefatos/HIST-NNN.md`
6. Atualizar `historia.yaml`:
   ```yaml
   estado: aguardando_aprovacao
   artefato:
     tipo_artefato: mockup | contrato
     caminho: .framework/estado/artefatos/HIST-NNN.md
     aprovado: false
   ```
7. Apresentar artefato para o usuario revisar

## Saida
- Arquivo `.framework/estado/artefatos/HIST-NNN.md` (mockup ou contrato)
- Historia em `aguardando_aprovacao`
- Mensagem ao usuario:
  ```
  Artefato gerado: estado/artefatos/HIST-NNN.md
  Revise e aprove via /aprovar HIST-NNN
  Depois: /impl HIST-NNN
  ```

## Restricoes
- NAO gerar artefato para `tipo: crud` (CRUD usa csharp_scaffold direto)
- NAO inventar fluxo/regras nao mencionados no PRD — perguntar ao usuario se faltar contexto
- NAO codar antes do artefato estar aprovado
- Mockup ASCII deve caber em ~80 colunas (legivel em terminal)
- Contrato deve ser auto-suficiente: pessoa nova lendo entende o que codar
