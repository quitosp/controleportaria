---
name: criar-prd
description: Cria PRD estruturado em YAML a partir de uma ideia do usuario. Output em estado/prd.yaml. Triggers: "/prd", "criar PRD", "novo projeto".
---

# Skill: criar-prd

## Entrada
Ideia em texto livre do usuario, ou (preferencial) `.framework/estado/analise.yaml` ja gerado pelo `/ideia`.

## Acao
0. **Verificar se existe `.framework/estado/analise.yaml`** (saida de `/ideia`):
   - Se SIM: ler, gerar PRD direto sem perguntar nada (a analise ja tem tudo). Saltar para passo 4.
   - Se NAO: avisar **"Recomendo rodar `/ideia` antes — o engenheiro de software conduz uma analise conversacional e produz documentacao + modelagem OO. Se preferir o caminho rapido (sem documentacao), responda 'rapido' que sigo com perguntas curtas."**
   - Se usuario confirmar caminho rapido, segue passos 1-3 abaixo.

1. Carregar template `.framework/modelos/prd.yaml`.

2. Fazer ate 6 perguntas, todas em UMA mensagem so:
   - **Q1**: Nome do projeto + 1 frase do problema
   - **Q2**: Quem usa (1-3 perfis)
   - **Q3**: Lista bruta de entidades de dominio (vira agregados)
   - **Q4 — Autenticacao**:
     - Tem autenticacao? (default: sim, JWT + Identity)
     - Tem RBAC com roles? Quais? (default: nao)
     - Registro aberto ao publico? (default: nao, so admin cria)
   - **Q5 — Plataformas**:
     - Vai ter frontend web? (sim/nao)
     - Se sim: apenas-desktop, responsivo, ou PWA instalavel?
     - Vai ter app mobile? (nao / so-pwa / flutter-nativo)
   - **Q6 — Stack** (so pergunta se ambiguo): API em C# Portaria ou Python FastAPI?

3. Inferir o resto:
   - data: hoje
   - versao: 0.1.0
   - escopo MVP: derivado dos agregados + frontend
   - restricoes default: paginacao 20, JWT se auth ativa
   - admin seed default: admin@local / Admin@123 (so se auth.ativa)

4. Para cada entidade citada, criar bloco `agregados[]`:
   - operacoes default: [salvar, alterar, listar]
   - campo Nome string obrigatorio
   - se usuario citou outros campos, incluir
   - se usuario disse que campo X "e unico" / "nao pode repetir", marcar `unico: true`

5. Validar: todos campos obrigatorios preenchidos? Se nao, perguntar APENAS os faltantes em mensagem curta.

6. Salvar em `estado/prd.yaml`. Atualizar `estado/projeto.yaml` com:
   - fase=prd
   - stack escolhida
   - plataformas: lista de stacks ativas (api/web/mobile)

## Saida
- Arquivo `estado/prd.yaml` valido
- Resposta ao usuario: 1-2 linhas com:
  - numero de agregados
  - plataformas ativas (api / web / mobile)
  - se auth ativa
  - sugestao da proxima fase:
    - tem frontend web ou mobile? sugerir `/ux`
    - so API pura? sugerir `/arq`

## Restricoes
- NAO escrever PRD em markdown narrativo
- NAO inventar requisitos nao mencionados
- NAO fazer "discovery profundo" estilo entrevista
- Se usuario der instrucao curta e completa (ex: "API portaria com empresas e veiculos, com auth"), gerar tudo sem perguntar mais
- Para projetos B2B/admin internos: default RBAC desligado, single role
- Para SaaS multi-tenant: sugerir RBAC ativo com [admin, usuario]
- Se usuario menciona "app", "celular", "mobile", perguntar tipo do mobile
- Se usuario menciona "desktop", "sistema interno": default web responsivo, sem mobile
