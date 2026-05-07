---
name: adicionar-capacidade
description: Adiciona uma nova capacidade (HIST) ao projeto sem refazer todo o /historias. Editar PRD + criar HIST + sugerir proximo passo. Triggers: "/capacidade", "adicionar capacidade", "nova capacidade", "preciso adicionar X", "adicionar feature/integracao/relatorio".
---

# Skill: adicionar-capacidade

## Filosofia
Atalho para o caso comum: "ja tenho /historias rodado, mas surgiu uma capacidade nova". Em vez de regenerar tudo, adiciona pontualmente.

## Quando usar
- PRD/historias ja existem
- Surgiu requisito novo (uma integracao, um relatorio, um job, um fluxo)
- Voce nao quer refazer toda a quebra em historias

## Quando NAO usar
- Voce ainda nao rodou `/historias` — use `/historias`
- A capacidade exige mudanca arquitetural grande — use `/editar-prd` + `/arq` + `/historias`

## Acao

### 1. Coletar info da capacidade
Pergunte ao usuario (em UMA mensagem so):
- Nome curto da capacidade
- Tipo: `crud | business-flow | integration | report | automation | authorization | architecture | refactor`
- Depende de quais historias existentes? (lista de IDs ou "nenhuma")
- Resumo em 1 frase
- Para `integration`: servico externo + tipo (webhook/rest/grpc/broker) + auth
- Para `report`: o que mostrar e fonte de dados
- Para `automation`: quando dispara (cron/intervalo) e idempotencia
- Para `authorization`: que escopo controla

### 2. Atualizar PRD
Carregar `estado/prd.yaml` e adicionar item ao bloco apropriado:
- `crud` -> novo agregado em `agregados[]`
- `business-flow`, `report`, `authorization` -> nada no PRD (so vira historia)
- `integration` -> adicionar em `integracoes[]`
- `automation` -> documentar em `escopo_mvp.inclui[]`
- `architecture`, `refactor` -> apenas em historias

### 3. Detectar proximo ID disponivel
Listar `estado/historias/HIST-*.yaml` e pegar maior numero + 1.

### 4. Criar nova historia
Gerar `estado/historias/HIST-NNN.yaml` baseado em `modelos/historia.yaml`:
- `id`, `titulo`, `tipo`, `prioridade`, `estado: pendente`
- `contexto.dependencias`: ids fornecidos
- `acao.comando`: `python .framework/scripts/csharp_scaffold.py X --campos "..." --tudo` (so se tipo=crud)
- `aceite`: 3 itens objetivos
- `artefato`:
  - tipo `crud` ou `architecture`: `aprovado: true` (sem bloqueio)
  - outros: `aprovado: false` + `tipo_artefato: ""` (vai ser definido no /artefato)

### 5. Atualizar projeto.yaml
- `historias_total += 1`

### 6. Reportar
Mensagem curta com:
- ID gerado
- Tipo
- Proximo passo:
  - `crud`/`architecture`: `/impl HIST-NNN`
  - outros: `/artefato HIST-NNN` -> `/aprovar HIST-NNN` -> `/impl HIST-NNN`

## Saida
- 1 arquivo `estado/historias/HIST-NNN.yaml` novo
- 1 entrada nova no PRD (se aplicavel)
- `projeto.yaml` incrementado
- Sugestao de proximo comando

## Restricoes
- NAO regenerar todas as historias — so adicionar uma
- NAO mexer em historias ja `concluida` salvo se afetadas pela dependencia
- NAO criar historia sem perguntar tipo se ambiguo
- Tipo OBRIGATORIO — sem tipo, abortar
- Para crud, sugerir usuario rodar `/agregado X` direto se for cadastro simples (atalho mais curto que via historia)
