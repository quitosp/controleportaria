# Tutorial — kitocode

Guia completo de uso do framework. Acompanhe do zero ate ter API + frontend rodando localmente, com testes e CI.

---

## Indice

1. [Pre-requisitos](#1-pre-requisitos)
2. [Instalacao](#2-instalacao)
3. [Conceitos antes de comecar](#3-conceitos-antes-de-comecar)
4. [Tutorial pratico — projeto "Tarefas"](#4-tutorial-pratico--projeto-tarefas)
5. [Os 8 tipos de capacidade](#5-os-8-tipos-de-capacidade)
6. [Referencia de slash commands](#6-referencia-de-slash-commands)
7. [Cenarios comuns](#7-cenarios-comuns)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Pre-requisitos

| O que | Versao minima | Verificar |
|---|---|---|
| **Node.js** | 20 | `node --version` |
| **Python** | 3.10 | `py --version` (Win) ou `python3 --version` |
| **Claude Code** (CLI) | 2.0 | `claude --version` |
| **PostgreSQL** | 14 | `psql --version` (so para projetos C#) |
| **.NET SDK** | 9 | `dotnet --version` (so para projetos C#) |
| **Git** | qualquer | `git --version` |

**Plataforma:** os scripts assumem `py` (launcher Windows). Em macOS/Linux, faca `alias py=python3` no seu shell rc.

**Postgres rapido com Docker:**
```bash
docker run -d --name pg -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16
```

---

## 2. Instalacao e estrutura

### Estrutura recomendada (api/ e web/ separadas)

A pasta-raiz onde voce roda `npx kitocode` hospeda APENAS o framework. **API e frontend devem ficar em sub-pastas separadas** (`api/` e `web/`) — evita misturar `dotnet` com `npm`, mantem `node_modules` longe da solution C#, e facilita CI/Docker:

```
meu-projeto/                       # pasta raiz, onde mora o framework
├── CLAUDE.md
├── TUTORIAL.md
├── .claude/commands/              # 26 slash commands gerados pelo CLI
├── .framework/                    # source do framework
│   ├── nucleo/                    # blueprints e convencoes
│   ├── modelos/                   # templates YAML
│   ├── skills/                    # 26 skills
│   ├── scripts/                   # 30+ scripts Python
│   ├── templates/csharp-core/     # Core/WebApi.Core embutidos
│   └── estado/                    # estado vivo (gerado durante uso)
├── documentacao/                  # gerada por /ideia (7 .md estilo TCC)
├── api/                           # backend C# (criado pelo HIST-001 architecture)
│   ├── ControleX.sln
│   ├── compartilhados/
│   ├── dominios/
│   ├── repositorios/
│   └── servicos/api/Api/
└── web/                           # frontend Next.js (criado pelo HIST-001 architecture)
    ├── src/
    ├── package.json
    └── tsconfig.json
```

### Comando

```bash
# cria a pasta raiz e instala o framework
npx kitocode@latest meu-projeto
cd meu-projeto
claude
```

Ou no diretorio atual (vazio ou ja existente):

```bash
mkdir meu-projeto && cd meu-projeto
npx kitocode@latest
```

Pre-requisitos: Node >= 20, Python >= 3.10. O CLI verifica e avisa.

Quando voce rodar `/impl HIST-001` (architecture), o framework cria `api/` e `web/` como sub-pastas — voce nao precisa cria-las a mao.

Abra a pasta no Claude Code:

```bash
claude
```

---

## 3. Conceitos antes de comecar

### 3.1 Filosofia: capacidade > CRUD

Cada historia e uma **capacidade do sistema**, nao apenas um cadastro. Antes de implementar algo nao-trivial, voce gera um **artefato** (mockup ou contrato) e aprova. So ai a implementacao roda. Resultado: zero TODO no commit, logica vem do contrato.

### 3.2 Token economy

Tudo que o framework faz e otimizado para gastar o **minimo de tokens** do Claude:

- Scripts Python fazem o trabalho pesado (scaffold, indexar, parsear erros). Claude so chama o script.
- `index.json` evita que Claude releia o codebase inteiro.
- `.optimized/` cacheia versoes compactas de YAMLs grandes.
- Skills detalhadas vivem em arquivos — Claude le on-demand, nao carrega tudo.

### 3.3 Fluxo padrao

```
/prd  →  [/ux]  →  /arq  →  /historias  →  [/artefato + /aprovar]  →  /impl HIST-NNN  →  /commit HIST-NNN
                                                                          ↑                            ↓
                                                                          └────────── proxima historia ┘
```

`/ux` so para projetos com frontend. `/artefato` + `/aprovar` so para historias tipo nao-`crud`.

### 3.4 Stacks

| Stack | Quando usar |
|---|---|
| `csharp-portaria` | Backend principal. Clean Arch + CQRS-lite + MediatR + EF Core 9 + Postgres. |
| `frontend-react` | Web. Next.js 15 + Tailwind + shadcn/ui + TanStack Query + Zod. |
| `python-fastapi` | Backend leve / scripts. FastAPI + SQLAlchemy 2 + asyncpg. |

A stack e definida no PRD e replicada para o resto do fluxo.

---

## 4. Tutorial pratico — projeto "Tarefas"

Vou guiar passo a passo a construcao de um app de gestao de tarefas com API C# + frontend Next.js.

### Passo 1 — Criar o projeto

```bash
npx kitocode@latest tarefas
cd tarefas
claude
```

### Passo 2 — `/proximo`

No Claude Code, digite:

```
/proximo
```

O oraculo analisa o estado e responde:

```
=== Estado do projeto ===
Sem PRD, sem arquitetura, sem historias.

=== Proximo passo recomendado ===
PRD nao existe. Comece criando o PRD do projeto.

Comandos relevantes:
  /prd
```

### Passo 3 — `/ideia` (recomendado antes do `/prd`)

Voce pode pular direto pro `/prd` (mais rapido), mas se quer **documentacao completa estilo trabalho de faculdade**, comece por:

```
/ideia
```

O engenheiro de software conversacional vai te conduzir em **6 rodadas**:

| Rodada | Foco | Saida |
|---|---|---|
| 1 | Visao (problema, contexto, escopo MVP) | `documentacao/1-visao.md` |
| 2 | Personas e atores (com objetivos e dores) | `documentacao/3-personas.md` |
| 3 | Modelagem OO — agregados, value-objects, heranca, diagrama Mermaid | `documentacao/5-modelagem.md` |
| 4 | Casos de uso (CDU-NNN com pre/pos condicoes) | `documentacao/4-casos-de-uso.md` |
| 5 | Requisitos nao-funcionais + decisoes (ADRs) | `documentacao/2-requisitos.md` + `7-decisoes.md` |
| 6 | Glossario (linguagem ubiqua) + resumo | `documentacao/6-glossario.md` |

**Diferenca pratica:** o `/ideia` faz perguntas socraticas ("e se 2 usuarios tentarem isso ao mesmo tempo?", "esse cliente pode ter mais de um endereco?", "como diferenciar PessoaFisica e PessoaJuridica — heranca ou enum?"), **identifica abstracoes que voce nao pensou** (ex: extrair `Endereco` como value-object porque `Cliente` e `Pedido` usam) e **desenha diagrama de classes** Mermaid antes de partir pro codigo.

No final, gera `.framework/estado/analise.yaml` que o `/prd` consome direto.

> **Quando pular?** Se voce ja tem dominio do problema e quer ir direto pro codigo (ex: "API com 3 cadastros simples"), o `/prd` rapido resolve. Se e um sistema com regras de negocio nao-triviais ou voce quer entregar com documentacao para faculdade/cliente, use `/ideia`.

### Passo 4 — `/prd`

Digite:

```
/prd
```

Se `/ideia` rodou, este comando le `analise.yaml` e gera o PRD direto sem perguntar mais nada. Se nao, Claude vai te perguntar:

- **Nome do projeto**: `Tarefas`
- **Proposito em uma frase**: "Gerenciar tarefas pessoais com prazos, prioridades e categorias"
- **Persona principal**: "Pessoa solo com 10-50 tarefas ativas"
- **Plataformas**: `api, web` (cria backend C# + frontend Next.js)
- **Funcionalidades core**: "criar tarefa, marcar concluida, filtrar por categoria, dashboard de produtividade"
- **Integracoes externas**: nenhuma (ou ex.: webhook do Telegram pra notificar)

Resultado: `.framework/estado/prd.yaml` preenchido com a stack travada como `csharp-portaria` + `frontend-react`.

**Sempre revise o PRD gerado.** Se algo estiver errado:

```
/editar-prd
```

### Passo 5 — `/ux` (so com frontend)

```
/ux
```

Como temos `web`, esse comando cria `.framework/estado/ux.yaml` com:

- Lista de telas (login, dashboard, lista-tarefas, detalhe-tarefa)
- Fluxos de navegacao
- Estados (loading, vazio, erro, sucesso)

E ja chama o `/uiux` para escolher design system. Voce pode rodar manualmente para ver opcoes:

```
/uiux "produtividade pessoal minimalista"
```

Retorna: estilo (ex.: Minimalismo), paleta (5 cores), font pairing (ex.: Inter + JetBrains Mono), efeitos.

### Passo 6 — `/arq`

```
/arq
```

Gera `.framework/estado/arquitetura.yaml`:

- Agregados (Tarefa, Categoria, Usuario)
- Capacidades (login, criar-tarefa, marcar-concluida, dashboard, filtrar)
- Stack confirmada
- Tabelas Postgres planejadas
- Endpoints REST esperados

Revise. Edite manualmente se faltar algo importante.

### Passo 7 — `/historias`

```
/historias
```

Quebra a arquitetura em historias `HIST-NNN.yaml` em `.framework/estado/historias/`. Cada uma tem:

- `id`: HIST-001, HIST-002, ...
- `tipo`: um dos 8 (crud, business-flow, integration, report, automation, authorization, architecture, refactor)
- `persona`: nome curto da persona principal (de `documentacao/3-personas.md`). Vazio para tipos internos como `architecture`.
- `motivo`: 1 linha do "para que" (extraido dos casos de uso). Da contexto a Claude na hora de implementar.
- `valor_de_negocio`: 1 linha opcional ("reduz tickets de suporte", "habilita upsell").
- `prioridade`: alta/media/baixa
- `dependencias`: outras HISTs que precisam estar prontas
- `aceite`: criterios objetivos
- `acao`: comando que o `/impl` vai executar

Exemplo:
```yaml
id: HIST-007
titulo: "Cliente acompanha pedido em andamento"
tipo: report
persona: "Cliente final"
motivo: "saber quando o pedido vai chegar sem precisar ligar no SAC"
valor_de_negocio: "reduz tickets de status em ~40%"
```

Esses 3 campos custam ~3 linhas de YAML mas direcionam decisoes do `/impl` (ex: linguagem amigavel para cliente, datas em PT-BR, sem campos tecnicos como UUID na tela). O detalhe da persona (objetivos, dores, frequencia de uso) vive em `documentacao/3-personas.md` — Claude le se precisar de profundidade.

Tipico: HIST-001 = `architecture` (sem persona). HIST-002+ = capacidades visiveis (com persona).

### Passo 8 — `/impl HIST-001` (architecture)

```
/impl HIST-001
```

A skill `implementar-historia` le o YAML, identifica que e `architecture`, e roda:

```bash
python .framework/scripts/novo_projeto.py csharp-portaria tarefas --auth
```

Isso cria a estrutura completa em `tarefas/`:

```
tarefas/
├── ControleFinanceiro.sln
├── compartilhados/core/Core/
├── compartilhados/webApi.core/WebApi.Core/
├── dominios/Dominios/
├── repositorios/Repositorios/
└── servicos/api/Api/
```

Com Postgres ja conectado, Identity + JWT seedado (`admin@local` / `Admin@123`), Swagger, CORS, ExceptionMiddleware.

Tambem cria o frontend Next.js em `tarefas-web/` com setup completo (Tailwind, shadcn/ui, axios, TanStack Query, Zod, tema claro/escuro, login).

### Passo 9 — `/commit HIST-001`

```
/commit HIST-001
```

Roda o gate de qualidade (`pos_implementacao.py`):

1. Reindex (`indexar_projeto`)
2. Review estrutural (`revisar_codigo`) — barra se houver desvio CRITICO/ALTO
3. Auditoria de seguranca (`verificar_seguranca`) — barra se houver vulnerabilidade

Se passar, cria commit com mensagem padrao e marca a historia como `concluida`.

### Passo 10 — `/impl HIST-002` (CRUD: Tarefa)

```
/impl HIST-002
```

Tipo `crud`, entao a skill executa:

```bash
python .framework/scripts/csharp_scaffold.py Tarefa --campos "titulo:string descricao:string prazo:datetime concluida:bool prioridade:int" --tudo
```

Em segundos, voce tem:

- Entidade `Tarefa` em `dominios/Dominios/Tarefas/Entidades/Tarefa.cs`
- Comandos `SalvarTarefaEntrada`, `AlterarTarefaEntrada` com FluentValidation
- Saidas `TarefaSaida`
- Handler `TarefaCommandHandler`
- Repositorio `ITarefaRepositorio` + `TarefaRepositorio` (Npgsql, NoTracking)
- Maps `TarefaMaps.cs` (varchar(200), timestamp without time zone)
- Controller `TarefaController` com `/v1/salvar`, `/v1/alterar`, `/v1/listar/{p}/{s}`
- DI registrado em `DependencyInjectionConfig`
- DbSet em `ContextoDB`
- Migration `v2` aplicada no banco

E feature Next.js correspondente em `tarefas-web/src/funcionalidades/tarefas/`:

- `tipos.ts` (Zod schema espelhando o C#)
- `api.ts` (chamadas axios)
- `ganchos.ts` (hooks TanStack Query)
- `componentes/FormularioTarefa.tsx` (form com RHF + Zod)
- `pagina.tsx` (lista glass + dialog de criar)
- `app/(privado)/tarefas/page.tsx`

```
/commit HIST-002
```

### Passo 11 — `/impl HIST-003` (business-flow: marcar concluida)

Tipo `business-flow` exige **artefato** antes:

```
/artefato HIST-003
```

Claude le o YAML da historia e gera `.framework/estado/artefatos/HIST-003.md` com o **contrato**:

```markdown
# HIST-003 — Marcar tarefa como concluida

## Endpoint
PATCH /api/tarefa/v1/{id}/concluir

## Pre-condicoes
- Tarefa existe
- Tarefa.concluida == false

## Pos-condicoes
- Tarefa.concluida = true
- Tarefa.concluidaEm = DataBrasilia.HorarioBrasilia()
- Evento TarefaConcluida disparado

## Validacoes
- 404 se tarefa nao existe → NaoEncontradoException
- 409 se ja concluida → ConflitoException

## Logica passo a passo
1. Carregar Tarefa por id (FirstOrDefaultAsync)
2. Validar pre-condicoes
3. Tarefa.MarcarConcluida()
4. Repositorio.Alterar(tarefa)
5. Salvar contexto (Commit)
```

Revise o contrato. Se estiver bom:

```
/aprovar HIST-003
```

Marca o artefato como aprovado. **So agora** o `/impl` aceita rodar:

```
/impl HIST-003
```

A skill scaffolda o handler vazio com o contrato como referencia, **le o contrato**, e implementa cada passo via Edit. Zero TODO no commit final.

```
/commit HIST-003
```

### Passo 12 — `/run`

```
/run
```

Sobe API + frontend em background:

- API em `https://localhost:7XXX` (porta detectada do `launchSettings.json`)
- Frontend em `http://localhost:3000`
- **Sincroniza automaticamente** a URL da API no `.env.local` do frontend par

Acesse `http://localhost:3000`, faz login (`admin@local` / `Admin@123`), ve as tarefas.

### Passo 13 — Iterar

Loop simples ate o MVP estar pronto:

```
/proximo            # ve qual a proxima historia
/impl HIST-NNN      # implementa
/commit HIST-NNN    # commita
```

A cada 5-6 historias, considere rodar:

```
/seguranca          # auditoria + hardening
/observabilidade    # Serilog + health checks
/ci                 # GitHub Actions
```

E ao final:

```
/doc                # gera README do projeto
```

---

## 5. Os 8 tipos de capacidade

| Tipo | Quando | Exige artefato? | Exemplo |
|---|---|:---:|---|
| `crud` | Cadastro simples (CRUD direto) | nao | Tarefa, Categoria, Cliente |
| `business-flow` | Processo com regras/estados | sim (contrato) | Marcar concluida, transferir entre contas |
| `integration` | Webhook/API externa | sim (contrato) | Importar OFX, sincronizar com Stripe |
| `report` | Dashboard/relatorio | sim (mockup) | Saldo mensal, top 10 produtos |
| `automation` | Job/fila/evento | sim (contrato) | Worker de notificacoes, cron de limpeza |
| `authorization` | Permissoes/roles | sim (contrato) | RBAC de admin/editor/viewer |
| `architecture` | Base tecnica | nao | Setup inicial, modularizacao |
| `refactor` | Ajuste estrutural | sim (plano antes/depois) | Migrar CommandResult para ProblemDetails |

**Regra:** tipo nao-`crud` e nao-`architecture` exige `/artefato HIST-NNN` + `/aprovar HIST-NNN` antes do `/impl`.

---

## 6. Referencia de slash commands

### Fluxo principal

| Comando | O que faz |
|---|---|
| `/proximo` | Oraculo: analisa estado e diz o proximo passo |
| `/prd` | Cria PRD em YAML |
| `/editar-prd` | Edita PRD e propaga `revisao_necessaria` |
| `/ux` | Cria UX (telas, fluxos, estados) — so frontend |
| `/editar-ux` | Edita UX |
| `/arq` | Gera arquitetura.yaml |
| `/historias` | Quebra arquitetura em historias |
| `/artefato HIST-NNN` | Gera mockup ou contrato |
| `/aprovar HIST-NNN` | Marca artefato aprovado, libera /impl |
| `/impl HIST-NNN` | Implementa historia |
| `/impl proxima` | Implementa proxima historia pendente |
| `/commit HIST-NNN` | Gate de qualidade + commit |

### Atalhos

| Comando | O que faz |
|---|---|
| `/agregado Nome` | Scaffold direto agregado C# (sem PRD/historia) |
| `/uiux <query>` | Design system via ui-ux-pro-max |
| `/rbac` | RBAC: papeis e permissoes |
| `/capacidade` | Adiciona nova capacidade sem refazer /historias |

### Qualidade

| Comando | O que faz |
|---|---|
| `/rev` | Revisa codigo contra blueprint |
| `/seguranca` | Auditoria + aplicacao de seguranca |
| `/observabilidade` | Serilog + health checks |
| `/ci` | GitHub Actions + CodeQL + Dependabot |
| `/testar X` | Cria testes para agregado/feature |

### Operacao

| Comando | O que faz |
|---|---|
| `/run` | Sobe API + frontend em background |
| `/idx` | Reindexar projeto |
| `/buscar X` | Busca simbolo/rota/agregado |
| `/doc` | Gera README do projeto |
| `/desfazer` | Reverte ultima historia |
| `/instalar` | Setup de projeto existente |
| `/evoluir` | Modulariza projeto quando cresce |

---

## 7. Cenarios comuns

### 7.1 Adicionar uma nova feature ao projeto existente

Voce ja tem PRD/arquitetura/historias mas quer **acrescentar** algo:

```
/capacidade
```

Claude pergunta o que voce quer adicionar, gera uma nova historia `HIST-NNN.yaml` no estado correto, e voce segue o fluxo `/artefato + /aprovar + /impl + /commit`.

### 7.2 Pegar projeto existente que ja foi feito a mao

```
cd projeto-existente
npx kitocode@latest .   # adiciona .framework/, CLAUDE.md, .claude/commands/
/instalar               # detecta a stack, indexa, gera projeto.yaml retroativo
/agregado Cliente       # ja pode usar atalhos
```

### 7.3 So quero scaffolds, sem PRD/arquitetura

```
/agregado Pedido --campos "valor:decimal status:string clienteId:guid"
```

Cria o agregado completo direto, sem precisar de PRD. Use quando ja sabe o que quer.

### 7.4 Mudei o PRD apos comecar a implementar

```
/editar-prd
```

A skill atualiza o PRD e marca como `revisao_necessaria` toda historia ainda pendente que mexe nas areas alteradas. Ao rodar `/impl HIST-NNN`, Claude alerta e te pede confirmacao.

### 7.5 A historia que rodei deu errado, quero voltar

```
/desfazer
```

Reverte o ultimo `/commit` (apaga arquivos criados, reverte migration, marca historia como `pendente` de novo).

### 7.6 Projeto cresceu, quero modularizar

```
/evoluir
```

Sugere modularizacao baseada nos agregados (ex: `Modulos/Vendas/`, `Modulos/Estoque/`) sem quebrar referencias.

### 7.7 Frontend em outro repo

A skill `/run` detecta o frontend par pelo nome (`<projeto>-web`). Se o seu frontend tem nome diferente, edite `.framework/estado/projeto.yaml > frontend_path` ou rode manualmente:

```bash
python .framework/scripts/sincronizar_api_url.py --front /caminho/do/frontend
```

---

## 8. Troubleshooting

### "Python nao detectado"

O CLI checa `py` (Win), `python3`, `python`. Instale Python 3.10+:

- Windows: `winget install Python.Python.3.12`
- macOS: `brew install python3`
- Linux: `sudo apt install python3`

Em macOS/Linux, depois disso adicione `alias py=python3` no `~/.bashrc` ou `~/.zshrc`.

### Slash commands nao aparecem no Claude Code

Confirme que `.claude/commands/` existe e tem arquivos `.md`:

```bash
ls .claude/commands/
```

Se vazio, reinstala:

```bash
rm -rf .claude .framework CLAUDE.md
npx kitocode@latest .
```

### `/help` nao chama o oraculo

`/help` e **reservado** pelo Claude Code (mostra o help builtin). Use `/proximo`.

### Erro de build C# apos `/impl`

Use o parser compacto:

```bash
python .framework/scripts/parse_dotnet_errors.py --rodar
```

Ele compila e mostra so os erros, agrupados por arquivo.

### Banco nao existe

```bash
python .framework/scripts/criar_banco.py
```

Le `appsettings.json`, cria o database via `psql`.

### Migration desincronizada

```bash
python .framework/scripts/migrate.py
```

Detecta proxima versao livre, roda `dotnet ef migrations add` + `database update`.

### Index esta stale

```bash
python .framework/scripts/check_drift.py
```

Detecta. Se positivo:

```bash
/idx
```

### Quero ver o que mudou desde a ultima sessao

```bash
python .framework/scripts/metricas.py
```

Mostra historias concluidas, tokens economizados, drift do index.

### CLAUDE.md ficou enorme e quero compactar

```bash
python .framework/scripts/otimizar_tokens.py
```

Gera `.framework/.optimized/` com versoes compactas dos YAMLs grandes. Skills ja preferem ler dali.

---

## Atribuicao

A skill `ui-ux-pro-max` e copia direta de [github.com/nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (NextLevelBuilder, MIT). Para atualizar do upstream:

```bash
python .framework/scripts/atualizar_uiux.py
```

---

## Recursos

- npm: https://www.npmjs.com/package/kitocode
- GitHub: https://github.com/quitosp/kitocode
- Issues: https://github.com/quitosp/kitocode/issues

Licenca: MIT
