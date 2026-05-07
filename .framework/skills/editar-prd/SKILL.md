---
name: editar-prd
description: Edita prd.yaml de forma controlada e propaga impacto para arquitetura/historias. Marca artefatos afetados como revisao_necessaria. Triggers: "/editar-prd", "alterar PRD", "adicionar agregado ao PRD", "remover feature do PRD".
---

# Skill: editar-prd

## Entrada
- `estado/prd.yaml` (deve existir)
- Mudanca solicitada em texto livre

## Acao
1. Carregar `prd.yaml`. Se nao existe, abortar e sugerir `/prd`.
2. Identificar tipo de mudanca:
   - **adicionar agregado**: adicionar entry em `agregados[]`
   - **remover agregado**: remover entry e marcar dependentes
   - **alterar campos de agregado**: editar `campos[]` do agregado
   - **adicionar feature**: editar `features_frontend[]`
   - **mudar restricao/escopo**: editar campos correspondentes
3. Aplicar mudanca no YAML (preservar campos nao tocados).
4. Identificar impacto e marcar:
   - Se `arquitetura.yaml` existe e mudanca afeta agregados:
     - Adicionar campo `revisao_necessaria: true` no(s) `agregados_mapeados[]` afetado(s)
   - Se `historias/HIST-NNN.yaml` referenciam agregado afetado:
     - Adicionar `revisao_necessaria: true` no historia.yaml
     - Se historia ja `concluida`, marcar tambem como `revisao_pos_concluida: true`
5. Atualizar `estado/projeto.yaml > ultima_edicao_prd: <ISO date>`
6. Reportar diff conciso: o que mudou + lista de artefatos afetados marcados.

## Saida
- prd.yaml atualizado
- Lista de arquivos marcados para revisao
- Sugestao: `/arq` se a arquitetura ainda nao foi gerada, ou apenas verificacao manual de cada artefato marcado

## Restricoes
- NAO regerar arquitetura/historias automaticamente — usuario decide
- NAO apagar campos sem confirmar
- NAO modificar projeto.yaml > fase (mudanca de PRD nao volta fase)
- Sempre preservar comentarios e ordem dos campos do YAML
