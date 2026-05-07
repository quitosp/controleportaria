---
name: criar-arquitetura
description: Gera arquitetura.yaml a partir de prd.yaml + blueprint da stack. Triggers: "/arq", "arquitetura", "criar arquitetura".
---

# Skill: criar-arquitetura

## Entrada
- `estado/prd.yaml` (deve existir e estar valido)
- `nucleo/{stack}.md` (blueprint correspondente)
- **Opcional mas recomendado**: `documentacao/5-modelagem.md` + `estado/analise.yaml` (se `/ideia` rodou) — traz modelagem OO rica com abstracoes, value-objects, heranca

## Acao
1. Ler `estado/prd.yaml`. Se nao existe, abortar e pedir `/prd`.
2. Carregar blueprint conforme `prd.yaml > projeto.stack`.
3. Carregar template `.framework/modelos/arquitetura.yaml`.
4. **Se existe `estado/analise.yaml`** (output do `/ideia`):
   - Para cada `abstracoes[]`: gerar bloco extra de classe-base/interface/value-object com arquivos no namespace correto (`Core/ObjetoDominio/` para value-objects compartilhados, `Dominios/<dominio>/Bases/` para classes-abstratas)
   - Para cada `agregados[]` com `extends`: o scaffold deve marcar `: <Base>` na declaracao da classe
   - Para cada `composto_por: [Endereco]`: incluir `Endereco Endereco { get; set; }` como propriedade do agregado e adicionar mapping owned-entity no `Maps`
5. Para cada agregado em `prd.yaml > agregados` (ou `analise.yaml > agregados` se mais rico):
   - Gerar bloco `agregados_mapeados[]` com `arquivos_gerados` e `arquivos_alterados` derivados do blueprint (substituindo `{nome}` e `{plural}`).
6. Definir `infraestrutura` com defaults: PostgreSQL (todas stacks), JWT auth, sem cache/fila. Sobrescrever a partir de `analise.yaml > requisitos_nao_funcionais` se presente (ex: cache se "10k req/s simultaneos", fila se "tem horario de pico").
7. Gerar ADRs:
   - 1-3 minimos sempre: stack, padrao CQRS-lite, idioma PT-BR
   - Se ha `documentacao/7-decisoes.md`, copiar como ADRs adicionais (linkando)
8. Salvar em `estado/arquitetura.yaml`. Atualizar `estado/projeto.yaml` com fase=arquitetura.

## Saida
- Arquivo `estado/arquitetura.yaml`
- Resposta ao usuario: numero de agregados mapeados + total de arquivos a gerar + sugestao "/historias"

## Restricoes
- NAO discutir trade-offs de stack — ja travada por blueprint
- NAO criar ADRs longos — uma linha por campo
- NAO incluir agregados nao listados no PRD
