---
name: criar-ux
description: Cria especificacao de UX em YAML estruturado a partir de prd.yaml. Define telas, fluxos, estados, ux-writing e wireframes ASCII. So para projetos com frontend. Triggers: "/ux", "criar UX", "design de telas", "wireframe".
---

# Skill: criar-ux

## Entrada
- `estado/prd.yaml` (precisa ter `features_frontend` ou `agregados` com operacoes)
- `nucleo/frontend-react.md` (blueprint)

## Pre-requisito
Stack do projeto deve incluir frontend (`frontend-react` ou `hibrido`). Se PRD diz so `csharp-portaria` puro (API sem UI), abortar e perguntar se usuario quer adicionar frontend ao escopo.

## Acao
1. Ler `prd.yaml`. Carregar template `.framework/modelos/ux.yaml`.

2. **Gerar design system fundamentado** via skill `ui-ux-pro-max`:
   ```bash
   python .framework/scripts/uiux.py "<tipo_produto> <industria> <palavras-chave>" --design-system -p "<nome_projeto>"
   ```
   - tipo_produto: extrair de `prd.yaml > agregados` ou contexto (ex: petshop, fintech, saas, ecommerce)
   - industria/palavras: do `prd.yaml > problema.contexto` + estilo desejado
   - Persistir com `--persist` em `design-system/MASTER.md` se projeto for serio
   - Usar a saida (estilo + paleta hex + fonte + checklist) para popular `design_tokens` no ux.yaml

   Se nao houver palavras-chave de estilo no PRD, default seguro: `"<tipo> minimal modern professional"`.
3. Para cada feature em `features_frontend` (ou cada agregado se nao houver features explicitas):
   - Gerar 2-4 telas tipicas: Lista, Formulario novo, Detalhe, (opcional) Dashboard
   - Atribuir id sequencial (T-001, T-002, ...)
   - Mapear cada tela para endpoints do agregado correspondente
4. Para cada tela, preencher OBRIGATORIAMENTE os 4 estados (carregando, vazio, erro, sucesso). Sem placeholder vazio.
5. Definir fluxos principais: cadastro, edicao, visualizacao, exclusao.
6. Definir navegacao: sidebar para >5 itens, topbar para <=5.
7. Gerar ux_writing PT-BR amigavel: titulos, botoes, mensagens vazias e de erro.
8. Salvar em `estado/ux.yaml`. Atualizar `projeto.yaml` adicionando flag `ux_definido: true`.
9. Opcional: se usuario pediu wireframe, gerar inline na resposta em ASCII por tela (ver formato abaixo).

## Wireframe ASCII (formato compacto)

```
T-001 /empresas — Lista de Empresas
+------------------------------------------+
| [Logo]  Empresas    [buscar___] [+ Nova] |
+------------------------------------------+
| Nome           | CNPJ        | Acoes     |
|----------------|-------------|-----------|
| ACME Ltda      | 12.345.678  | [Editar]  |
| Beta SA        | 98.765.432  | [Editar]  |
+------------------------------------------+
| < 1 2 3 ... >        Total: 47           |
+------------------------------------------+
Estados: vazio="Nenhuma empresa", erro=toast, loading=skeleton
```

## Saida
- Arquivo `estado/ux.yaml`
- Resposta ao usuario: tabela com `T-NNN | rota | proposito` + sugestao "/historias" para incluir telas como historias de implementacao

## UI components base
Todos projetos frontend usam o mesmo conjunto base instalado via `setup_ui.py`:
- Button, Input, Label, Card, Table, Skeleton, Badge, Dialog (estilo shadcn/ui)
- Tema claro/escuro automatico via `next-themes` (componente `<AlternarTema />`)
- Tokens HSL com CSS variables — paleta default azul, modo escuro automatico
- `cn()` utility (tailwind-merge + clsx)

`frontend_scaffold.py` ja gera paginas/forms usando esses componentes.

## Restricoes
- NAO criar telas alem das features do PRD
- NAO escolher cores/fontes "criativas" — paleta neutra default, usuario customiza CSS variables em `globals.css`
- SEMPRE preencher os 4 estados explicitamente (Skeleton para carregando, mensagem para vazio, toast para erro)
- SEMPRE em PT-BR no ux_writing
- SEMPRE incluir AlternarTema no layout privado
- NAO entregar wireframe se nao foi pedido — yaml estruturado basta para Claude implementar
- Se PRD nao tiver agregados nem features, abortar e pedir /prd primeiro

## Integracao com outras skills
- `criar-historias` deve, apos esta skill rodar, gerar uma historia por tela (`HIST-NNN: Implementar tela {nome}`)
- `implementar-historia` para tipo=tela: ler `ux.yaml` da tela, gerar componentes/pagina seguindo `nucleo/frontend-react.md`
