---
name: desfazer-ultima-historia
description: Reverte ultima historia implementada (arquivos, migration, estado). NAO desfaz commit ja pushed. Triggers: "/desfazer", "rollback ultima", "desfazer ultima historia".
---

# Skill: desfazer-ultima-historia

## Pre-requisito
- Repositorio git
- Ultima acao foi `/impl HIST-NNN` (verificar `estado/projeto.yaml > historia_atual`)

## Acao

### 1. Identificar o que desfazer
- Carregar `estado/historias/HIST-NNN.yaml` mais recente com `estado: concluida`
- Se ja foi commitada (`commit_sha` existe no yaml): perguntar se faz `git revert <sha>` (cria commit novo) ou `git reset --soft HEAD~1` (mantem mudancas no working dir)
- Se NAO commitada: deletar arquivos listados em `acao.arquivos_criar`

### 2. Reverter migration (se for agregado C#)
```bash
dotnet ef migrations remove --project repositorios/Repositorios --startup-project servicos/api/Api
```
**ATENCAO**: se a migration ja foi aplicada no banco (database update), preciso primeiro fazer downgrade:
```bash
dotnet ef database update <migration-anterior> --project repositorios/Repositorios --startup-project servicos/api/Api
dotnet ef migrations remove --project repositorios/Repositorios --startup-project servicos/api/Api
```

### 3. Reverter patches em ContextoDB e DI
- Remover `DbSet<{Singular}>` e `ApplyConfiguration` do ContextoDB
- Remover registros de Repositorio + Handler do DependencyInjectionConfig
- Remover usings agora sem uso

### 4. Atualizar estado
- Marcar historia como `pendente` (ou `cancelada` se nao for re-implementada)
- Atualizar `projeto.yaml > historias_concluidas--`
- Reindexar: `python .framework/scripts/indexar.py`

### 5. Reportar
Lista do que foi revertido + sugestao de proximo passo.

## Saida
- Arquivos deletados / commit revertido
- Migration removida
- Banco voltado para estado anterior (se aplicado)
- index.json atualizado
- historia.yaml com `estado: pendente`

## Restricoes
- NUNCA `git push --force` automaticamente
- NUNCA tocar commits ja em branch remota sem confirmar
- NUNCA descartar mudancas sem confirmar (sempre perguntar antes de deletar arquivos uncommitted)
- NUNCA fazer drop de tabela direto — sempre via `dotnet ef database update`
- Se o estado do banco divergir do esperado (migration aplicada mas arquivos jah removidos), parar e pedir intervencao manual

## Avisos
Esta skill e para uso local. Em time, prefira:
- Criar PR de revert
- Marcar historia como `revisao_necessaria` em vez de desfazer
