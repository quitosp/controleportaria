---
name: editar-ux
description: Edita ux.yaml e propaga impacto para historias de tela. Triggers: "/editar-ux", "alterar tela", "adicionar fluxo", "mudar componente da tela".
---

# Skill: editar-ux

## Entrada
- `estado/ux.yaml` (deve existir)
- Mudanca solicitada

## Acao
1. Carregar `ux.yaml`. Se nao existe, abortar e sugerir `/ux`.
2. Identificar tipo:
   - **adicionar tela**: novo entry em `telas[]` com id sequencial
   - **remover tela**: remover entry, marcar fluxos afetados
   - **alterar componentes/estados/acoes**: editar tela existente
   - **alterar design_tokens**: ajustar paleta/tipografia (afeta TODAS as telas implementadas)
   - **alterar navegacao**: editar `navegacao.itens[]`
3. Aplicar mudanca preservando outros campos.
4. Marcar impacto:
   - Historias com `tipo: tela` cujo `id_ux` mudou: `revisao_necessaria: true`
   - Se mudou `design_tokens`: marcar TODAS historias de tela ja `concluida` com `revisao_design: true`
5. Atualizar `projeto.yaml > ultima_edicao_ux`.
6. Reportar diff + impacto.

## Saida
- ux.yaml atualizado
- Lista de historias marcadas
- Sugestao: revisar telas marcadas via `/impl HIST-NNN` ou `/rev`

## Restricoes
- NAO regerar telas implementadas — usuario decide se reimplementa
- Manter os 4 estados (carregando/vazio/erro/sucesso) preenchidos sempre
- NAO mudar id de tela existente (quebra referencias). Se precisa renomear, criar nova com novo id e marcar antiga como deprecada
