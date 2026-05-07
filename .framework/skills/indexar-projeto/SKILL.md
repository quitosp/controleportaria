---
name: indexar-projeto
description: Gera/atualiza indice de simbolos do projeto em estado/index.json. Triggers: "/idx", "indexar", "reindexar".
---

# Skill: indexar-projeto

## Entrada
Nenhuma (opera no cwd).

## Acao
Rodar: `python .framework/scripts/indexar.py .`

## Saida
- `estado/index.json` atualizado
- Resposta: 1 linha com estatisticas (total arquivos, simbolos, rotas, tokens estimados)

## Quando usar
- Apos cada `implementar-historia` (automatico)
- Apos edits manuais grandes
- Antes de pedir busca complexa

## Restricoes
- NAO indexar Portaria-master (referencia, nao codigo do projeto)
- NAO indexar bin/, obj/, node_modules/, .next/, .venv/
