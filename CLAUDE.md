# Framework — instrucoes para Claude Code

## Sobre
Framework de criacao de projetos otimizado para uso solo + Claude Code. Idioma: PT-BR. Token-economy first.

## Filosofia: capacidade > CRUD
Cada historia e uma **capacidade do sistema**, nao apenas um cadastro. 8 tipos:
- `crud` — cadastro simples → `csharp_scaffold` direto
- `business-flow` — processo com regras/estados → exige mockup ou contrato
- `integration` — webhook/API externa → exige contrato
- `report` — dashboard/relatorio → exige mockup
- `automation` — job/fila/evento → exige contrato
- `authorization` — permissoes/roles → exige contrato
- `architecture` — base tecnica → exige descricao
- `refactor` — ajuste estrutural → exige plano antes/depois

**Regra**: tipo != `crud` requer artefato aprovado antes de `/impl`.

## Stacks suportadas (blueprint travado)
- **csharp-portaria** (PRINCIPAL) — C# .NET 9, Clean Arch + CQRS-lite + MediatR + EF Core 9 + Npgsql, padrao Portaria-master
- **frontend-react** — Next.js 15 + TypeScript + Tailwind + shadcn/ui + TanStack Query + Zod, feature-based
- **python-fastapi** — FastAPI + SQLAlchemy 2 + Pydantic 2 + asyncpg, espelha camadas Portaria

Banco: PostgreSQL para todas stacks.

## Fluxo padrao
```
/prd  →  [/ux]  →  /arq  →  /historias  →  [/artefato + /aprovar se tipo != crud]  →  /impl HIST-NNN  →  /commit HIST-NNN  (loop)
```
- `/ux` so para projetos com frontend.
- `/artefato` + `/aprovar` so para historias tipo != `crud` e != `architecture`.

## Comandos rapidos
| Comando | O que faz |
|---------|-----------|
| `/ideia` | **engenheiro de software conversacional**: levanta requisitos em rodadas, modela OO (heranca, value-objects, abstracoes), gera `documentacao/` com 7 .md estilo TCC + `estado/analise.yaml`. Pre-requisito recomendado do `/prd` (skill: criar-ideia) |
| `/prd` | criar PRD em YAML — usa `analise.yaml` automaticamente se `/ideia` rodou (skill: criar-prd) |
| `/ux` | criar UX (telas, fluxos, estados) — so frontend (skill: criar-ux) |
| `/arq` | gerar arquitetura.yaml a partir do PRD/UX (skill: criar-arquitetura) |
| `/historias` | quebrar arquitetura em historias (skill: criar-historias) |
| `/impl HIST-NNN` | implementar uma historia (skill: implementar-historia) |
| `/impl proxima` | implementar proxima pendente |
| `/agregado Nome` | atalho: scaffold direto agregado C# (skill: csharp-novo-agregado) |
| `/editar-prd` | editar PRD e propagar revisao_necessaria (skill: editar-prd) |
| `/editar-ux` | editar UX e propagar (skill: editar-ux) |
| `/commit HIST-NNN` | commitar historia concluida (skill: commitar-historia) |
| `/uiux <query>` | design system (estilo+paleta+fonte) via ui-ux-pro-max (skill: ui-ux-pro-max) |
| `/atualizar-uiux` | resincroniza `repo-original/` da skill ui-ux-pro-max do upstream (script: atualizar_uiux.py) |
| `/seguranca` | auditoria + aplicacao de seguranca backend/frontend (skill: seguranca) |
| `/pos` | pos-implementacao: review + seguranca + reindex (script: pos_implementacao.py) |
| `/idx` | reindexar projeto (skill: indexar-projeto) |
| `/buscar X` | buscar simbolo/rota/agregado (skill: buscar-codigo) |
| `/rev` | revisar codigo contra blueprint (script: revisar_codigo.py + skill: revisar-codigo) |
| `/doc` | gerar README do projeto (skill: documentar-projeto) |
| `/run` | rodar projeto em background. Antes de subir API C#, sincroniza `NEXT_PUBLIC_API_URL` no `.env.local` do frontend par (skill: rodar-projeto) |
| `/sync-api` | sincroniza URL da API no frontend lendo `launchSettings.json` (script: sincronizar_api_url.py) |
| `/testar X` | criar testes para agregado/feature (skill: criar-testes) |
| `/instalar` | setup de projeto existente clonado (skill: instalar-projeto) |
| `/desfazer` | reverter ultima historia implementada (skill: desfazer-ultima-historia) |
| `/observabilidade` | aplicar Serilog + health checks (script: aplicar_observabilidade_csharp.py) |
| `/ci` | aplicar GitHub Actions CI + CodeQL + Dependabot (script: aplicar_ci.py) |
| `/cliente-api` | gerar tipos TS a partir do swagger.json (script: gerar_cliente_api.py) |
| `/validar-prd` | valida estado/prd.yaml antes de /arq (script: validar_prd.py) |
| `/metricas` | telemetria de uso do framework (script: metricas.py) |
| `/proximo` | **oraculo**: analisa estado e diz o proximo passo (skill: oraculo). Nao usar `/help` — esta reservado pelo Claude Code. |
| `/profiling` | aplica EF interceptor para slow queries + N+1 detector (script: aplicar_profiling_csharp.py) |
| `/e2e` | configura Playwright + testes basicos (script: aplicar_e2e.py) |
| `/evoluir` | modulariza projeto quando cresce demais (skill: evoluir-arquitetura) |
| `/artefato HIST-NNN` | gera mockup ou contrato pre-implementacao (skill: criar-artefato) |
| `/aprovar HIST-NNN` | marca artefato aprovado, libera /impl (skill: aprovar-artefato) |
| `/otimizar` | gera cache .optimized/ compactado para economia de tokens (script: otimizar_tokens.py) |
| `/capacidade` | adicionar nova capacidade sem refazer /historias (skill: adicionar-capacidade) |
| `/migrar-tipos` | converte tipos legados (infra/agregado/...) para os 8 novos (script: migrar_tipos.py) |

## Regras inegociaveis para Claude (token economy)

### Antes de ler arquivos
1. **Existe `.framework/estado/.optimized/`?** Prefira ler dali (versao compactada). Fallback no original. Regenerar com `python .framework/scripts/otimizar_tokens.py` se mudou.
2. **Existe `.framework/estado/index.json`?** Use `python .framework/scripts/buscar.py` em vez de Glob/Grep.
   - `--simbolo X` → onde esta X
   - `--rota /api/X` → endpoints
   - `--agregado X` → todos arquivos do agregado
   - `--tipo handler` → todos handlers
   - `--conteudo "regex"` → grep nos arquivos indexados
3. **Index pode estar stale?** Rode `python .framework/scripts/check_drift.py` para confirmar.
4. **Arquivo > 300 linhas?** Rode `python .framework/scripts/token_check.py <arquivo>` antes de Read.
5. **Erro de build C#?** Use `python .framework/scripts/parse_dotnet_errors.py --rodar` em vez de ler stdout cru.

### Ao escrever codigo
1. **Zero comentarios** em codigo de dominio. Nomes claros bastam.
2. **Sempre** seguir blueprint da stack atual: `.framework/nucleo/{stack}.md`.
3. **Sempre PT-BR** em nomes de dominio (entidades, comandos, mensagens).
4. **Para agregados C#**: nunca escrever os 9 arquivos a mao — chamar `python .framework/scripts/csharp_scaffold.py {Nome} [--campos "..."] --tudo` (`--tudo` faz scaffold + migration + database update + **review estrutural + auditoria seguranca** + reindex). Se banco nao existe: `python .framework/scripts/criar_banco.py` antes.
5. **Para features frontend**: chamar `python .framework/scripts/frontend_scaffold.py {feature} [--campos "..."] --tudo` (gera + **review + seguranca** + reindex). Antes da primeira feature, rodar `python .framework/scripts/setup_ui.py --raiz {projeto}`.
6. **Para projetos novos**: chamar `python .framework/scripts/novo_projeto.py <stack> <nome>` (copia Core base de Portaria-master automaticamente).
7. **Migration manual** (sem mudanca de agregado): `python .framework/scripts/migrate.py`.
8. **Apos editar manualmente**: rodar `python .framework/scripts/pos_implementacao.py --raiz <projeto>` para revalidar (review + seguranca + reindex).
9. **Antes de cada commit**: `commitar-historia` skill ja executa `pos_implementacao.py` como gate. Se houver CRITICO/ALTO, abortar commit e corrigir.
10. **Em duvida arquitetural** consulte `Portaria-master/` se existir na raiz, OU `.framework/templates/csharp-core/` (template embutido). O framework e autonomo: nao precisa de Portaria-master ao lado.
11. **Atualizar template C# Core** (apos editar Portaria-master): `python .framework/scripts/atualizar_csharp_core.py --portaria <path>` propaga mudancas para o template interno.

### Ao responder usuario
1. **Tersas, sem narrativa.** Update por etapa em tarefa longa.
2. **Sem "vou fazer X"** — fazer e reportar.
3. **Sem resumo final redundante** quando o diff ja fala.
4. **Sem emojis** salvo pedido explicito.

## Estrutura
```
.framework/
├── nucleo/                         # blueprints e convencoes (referencia obrigatoria)
│   ├── csharp-portaria.md          # padrao C# completo
│   ├── frontend-react.md           # padrao Next.js
│   ├── python-fastapi.md           # padrao FastAPI
│   ├── testes.md                   # blueprint de testes
│   ├── convencoes.md               # mapeamento entre stacks
│   └── fluxo.md                    # PRD → UX → ARQ → HISTORIAS → IMPL
├── modelos/                        # templates YAML + extras
│   ├── prd.yaml
│   ├── ux.yaml
│   ├── arquitetura.yaml
│   ├── historia.yaml
│   ├── csharp-templates.md         # value objects, enums, integration events, workers
│   ├── gitignore.template          # gerado por novo_projeto.py
│   └── index.json.schema.json
├── skills/                         # 15 skills
│   ├── criar-prd/, editar-prd/
│   ├── criar-ux/, editar-ux/
│   ├── criar-arquitetura/
│   ├── criar-historias/
│   ├── implementar-historia/
│   ├── csharp-novo-agregado/
│   ├── commitar-historia/
│   ├── indexar-projeto/
│   ├── buscar-codigo/
│   ├── revisar-codigo/
│   ├── documentar-projeto/
│   ├── rodar-projeto/
│   └── criar-testes/
├── templates/
│   └── csharp-core/                # 47 arquivos do Core/WebApi.Core embutidos (autonomia)
├── scripts/                        # 30 scripts Python
│   ├── novo_projeto.py             # init csharp/frontend/flutter/python (chama copiar_core_base)
│   ├── copiar_core_base.py         # copia Core/WebApi.Core de Portaria-master, gera ContextoDB limpo Postgres
│   ├── csharp_scaffold.py          # 9 arquivos do agregado, --campos, --unico, --migrate, --tudo, --forcar
│   ├── auth_scaffold.py            # AuthController + SeedAdmin Identity+JWT (use --auth no novo_projeto)
│   ├── frontend_scaffold.py        # 5 arquivos da feature usando shadcn UI
│   ├── flutter_scaffold.py         # 5 arquivos da feature Flutter (Riverpod + Dio + freezed)
│   ├── setup_ui.py                 # aplica shadcn UI + tema claro/escuro em projeto Next.js
│   ├── migrate.py                  # dotnet ef migrations add v{N} + database update (auto-versao)
│   ├── criar_banco.py              # CREATE DATABASE Postgres (le appsettings, auto-detecta psql)
│   ├── indexar.py                  # gera estado/index.json
│   ├── buscar.py                   # consulta indice (simbolo, rota, agregado, conteudo)
│   ├── check_drift.py              # detecta indice stale
│   ├── parse_dotnet_errors.py      # extrai erros compactos do dotnet build
│   ├── token_check.py              # estima tokens antes de Read
│   ├── uiux.py                     # wrapper para skill ui-ux-pro-max
│   ├── verificar_seguranca.py      # auditoria backend+frontend+flutter (deps, headers, secrets)
│   ├── aplicar_seguranca_csharp.py # rate limit, HSTS, security headers, audit log no .NET
│   ├── aplicar_seguranca_next.py   # CSP, HSTS, headers, url validator no Next.js
│   ├── revisar_codigo.py           # lint estrutural contra blueprints (auto)
│   ├── pos_implementacao.py        # orquestrador: reindex + review + seguranca (gate de qualidade)
│   ├── aplicar_observabilidade_csharp.py  # Serilog (JSON estruturado) + health checks /health /ready /live
│   ├── aplicar_ci.py               # GitHub Actions (build/test/security) + CodeQL + Dependabot
│   ├── gerar_cliente_api.py        # gera tipos TS do swagger.json (sync front/back)
│   ├── validar_prd.py              # valida estado/prd.yaml antes de /arq
│   ├── metricas.py                 # telemetria local de uso do framework
│   ├── aplicar_profiling_csharp.py # EF Core interceptor: slow queries + N+1 detector
│   ├── aplicar_e2e.py              # Playwright config + testes basicos + workflow CI
│   └── oraculo.py                  # analisa estado do projeto e sugere proximo passo
└── estado/                         # estado vivo do projeto
    ├── projeto.yaml                # fase, stack, progresso
    ├── prd.yaml
    ├── ux.yaml
    ├── arquitetura.yaml
    ├── historias/HIST-NNN.yaml
    └── index.json                  # gerado, NAO editar (gitignored)

Portaria-master/                    # referencia C# original (intocavel) — Claude deve consultar em duvida
```

## Quando o projeto comeca do zero
1. Usuario fala a ideia.
2. Claude executa `/prd`.
3. Se frontend: `/ux`. Senao: `/arq`.
4. `/historias` → `/impl HIST-001`.
5. `HIST-001` tipicamente roda `python .framework/scripts/novo_projeto.py csharp-portaria <nome>` (que copia Core base do Portaria automaticamente).
6. `HIST-002+` cria agregados via `csharp_scaffold.py`.
7. Apos cada historia: `/commit HIST-NNN`.
8. Ao final: `/doc` para README, `/run` para subir local.

## Para projeto C# existente
1. Rodar `python .framework/scripts/indexar.py` na raiz do projeto.
2. Usar `/agregado Nome` direto, sem PRD/arquitetura.
3. Ou criar PRD retroativo se for refatorar.

## Compatibilidade de plataforma
Comandos usam `py` (launcher Windows). Em Linux/Mac trocar por `python3`.

## Decisoes ja tomadas (nao questionar)
- Idioma: PT-BR para dominio
- Validacao: FluentValidation embutida no Comand
- Erro padrao: ComandResult / PagedResult
- Auth: JWT default (NetDevPack)
- DB: PostgreSQL para todas stacks (provider Npgsql para C#)
- Sem cascade delete (`ClientSetNull`)
- NoTracking global em queries
- Zero comentarios em codigo de dominio
- Strings: `varchar(200)` default
- IDs: `Guid` / `uuid`
- DateTime: `timestamptz` (Brasilia explicito via DataBrasilia.HorarioBrasilia)
