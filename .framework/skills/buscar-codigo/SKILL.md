---
name: buscar-codigo
description: Busca simbolos/rotas/agregados sem ler arquivos. Substitui Glob/Grep para perguntas tipo "onde esta X?". Triggers: "/buscar X", "onde fica X", "encontrar X".
---

# Skill: buscar-codigo

## Entrada
Termo de busca ou filtro especifico.

## Acao — escolher modo conforme intencao
1. Simbolo por nome: `python .framework/scripts/buscar.py <termo>`
2. Rota HTTP: `python .framework/scripts/buscar.py --rota /api/empresa`
3. Tipo de simbolo: `python .framework/scripts/buscar.py <termo> --tipo class`
4. Tipo de arquivo: `python .framework/scripts/buscar.py --tipo handler`
5. Agregado completo: `python .framework/scripts/buscar.py --agregado Empresa`

## Saida
Lista compacta `<tipo> <nome> <arquivo>:<linha>`.

## Quando usar isso vs Glob/Grep
| Pergunta | Usar |
|----------|------|
| "onde esta a classe X?" | buscar-codigo |
| "lista todos handlers" | buscar-codigo --tipo handler |
| "qual rota chama Y" | buscar-codigo --rota |
| "padrao no codigo todo, ex: TODO" | Grep |
| "arquivo por nome glob" | Glob |
| "ler arquivo conhecido" | Read direto |

## Restricoes
- Se index.json nao existe, rodar `indexar-projeto` primeiro
- NAO usar Read em sequencia para "explorar" — use buscar
