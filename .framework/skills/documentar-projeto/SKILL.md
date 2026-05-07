---
name: documentar-projeto
description: Gera README.md compacto a partir de prd.yaml + arquitetura.yaml + index.json. Triggers: "/doc", "documentar projeto", "gerar README".
---

# Skill: documentar-projeto

## Entrada
- `estado/prd.yaml`
- `estado/arquitetura.yaml` (opcional)
- `estado/index.json` (opcional)
- `estado/ux.yaml` (opcional)

## Acao
1. Ler todos artefatos disponiveis.
2. Gerar `README.md` na raiz do projeto com secoes:
   - **Nome + 1 frase** (de prd.yaml > problema.dor)
   - **Stack** (de prd.yaml > stack)
   - **Como rodar**:
     - C#: `dotnet run --project servicos/api/Api`
     - Frontend: `npm run dev`
     - Python: `uvicorn servicos.api.main:app --reload`
   - **Configuracao** (variaveis de ambiente de arquitetura.yaml > config_chaves)
   - **Estrutura** (4 pastas raiz da stack — referenciar blueprint)
   - **Endpoints** (de index.json > rotas_api, agrupados por controller)
   - **Agregados** (lista de prd.yaml > agregados, com 1 linha cada)
   - **Telas** (se ux.yaml: tabela tela|rota|proposito)
   - **Decisoes-chave** (1 linha por ADR de arquitetura.yaml > decisoes)
3. Sobrescrever README.md (se existir, perguntar antes).

## Saida
- `README.md` na raiz do projeto, max 200 linhas

## Restricoes
- NAO copiar `.framework/` ou Portaria-master no README
- NAO inventar conteudo nao presente nos artefatos
- Tabelas markdown simples, sem screenshots
- Se algum artefato faltar, marcar secao como "(nao gerado ainda — rode /...)"
- PT-BR
