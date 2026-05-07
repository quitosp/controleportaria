---
name: commitar-historia
description: Cria commit git logico para uma historia concluida. Triggers: "/commit HIST-NNN", "/commit", "commitar historia".
---

# Skill: commitar-historia

## Entrada
- ID da historia (ou "atual" = ultima `concluida`)
- `estado/historias/HIST-NNN.yaml`

## Pre-requisito
- Diretorio precisa ser repositorio git (`.git/`)
- Se nao for, perguntar se deve rodar `git init`

## Acao
1. Carregar historia. Se `estado != concluida`, abortar (so commita o que terminou).
2. **GATE de qualidade**: rodar `python .framework/scripts/pos_implementacao.py --raiz <projeto> --stack <stack>`.
   - Se exit code != 0: abortar commit. Reportar desvios CRITICO/ALTO ao usuario com sugestao de fix.
   - Para forcar commit mesmo com desvios (uso raro): `--sem-bloqueio` no comando manual.
3. Verificar `git status --porcelain`. Se vazio, abortar com "nada a commitar".
4. Stage seletivo: adicionar APENAS os arquivos listados em `acao.arquivos_criar` + `acao.arquivos_editar`. NAO usar `git add .` ou `git add -A`.
5. Se houver arquivos modificados fora dessa lista, listar e pedir confirmacao (podem ser side-effects esperados como ContextoDB.cs ou index.json).
6. Construir mensagem padrao:
   ```
   {id}: {titulo}
   
   {tipo}: {agregado se aplicavel}
   Arquivos: {N} criados, {M} alterados
   ```
7. Rodar `git commit -m "<heredoc>"` SEM hooks bypass.
8. Atualizar `historia.yaml > commit_sha: <hash>` com saida de `git rev-parse HEAD`.

## Saida
- Commit criado
- SHA reportado
- Sugestao: `/impl proxima` ou `git push` se houver remote

## Restricoes
- NUNCA `--no-verify` salvo pedido explicito
- NUNCA `git add -A` ou `.` (poderia commitar `.framework/estado/index.json` ou outros gerados)
- NUNCA `--amend` (cada historia = commit novo)
- NAO push automatico
- Se pre-commit hook falhar, reportar erro completo e NAO tentar bypass
