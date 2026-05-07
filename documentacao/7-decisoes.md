# 7. Decisoes Arquiteturais (ADRs)

Cada decisao registra: **contexto**, **decisao**, **consequencias**.

## ADR-001 — Stack backend: C# .NET 9 (csharp-portaria)

**Contexto**: Volume baixo-medio (~50 movimentos/dia), domínio com regras estavel (maquina de estados, auditoria, multi-tenant). A organizacao ja tem afinidade com C# (Portaria-master como referencia).

**Decisao**: usar **C# .NET 9** com Clean Arch + CQRS-lite + MediatR + EF Core 9 + Npgsql. Padrao Portaria-master ja documentado em `.framework/nucleo/csharp-portaria.md`.

**Consequencias**:
- Reuso direto do template Core/WebApi.Core.
- Familiaridade da equipe.
- BackgroundService nativo para worker de notificacoes.
- SignalR no mesmo backend, sem servico separado.

## ADR-002 — Stack frontend: Next.js 15 + Tailwind + shadcn/ui

**Contexto**: UI para porteiros (desktop), lideres (desktop e tablet), admins (desktop). Sem mobile no MVP. Padrao da casa (`.framework/nucleo/frontend-react.md`).

**Decisao**: Next.js 15 (App Router) + TypeScript + Tailwind + shadcn/ui + TanStack Query + Zod, feature-based.

**Consequencias**:
- Componentes prontos do shadcn/ui aceleram telas de cadastro.
- TanStack Query suporta cache + invalidacao em tempo real.
- Zod valida formularios espelhando contratos do backend.

## ADR-003 — Banco: PostgreSQL

**Contexto**: convencao do framework. Boa para multi-tenant via `UnidadeId`, suporta `timestamptz`, `uuid`, `jsonb` (anexos meta), texto sem limite.

**Decisao**: PostgreSQL 16+, provider Npgsql.

**Consequencias**: tudo que esta no nucleo do framework ja se aplica.

## ADR-004 — Multi-tenant via coluna `UnidadeId`

**Contexto**: MVP comeca com uma unidade Frigoestrela; futuro pode atender outras. Schema-per-tenant e overkill agora.

**Decisao**: cada agregado tem `UnidadeId`. Toda query filtra automaticamente via `IUnidadeContext` (extraido do JWT).

**Consequencias**:
- Solucao simples e suficiente para MVP.
- Revisar caso volume cresca a ponto de exigir isolation fisica.
- Risco mitigado por filtro global no DbContext (`HasQueryFilter`).

## ADR-005 — Integracao WhatsApp via Evolution API

**Contexto**: Cliente decidiu por Evolution API (custo zero, instancias proprias). Cada unidade tera sua instancia.

**Decisao**: cliente HTTP simples no backend, configuracao por Unidade (URL + token armazenados em `Unidade.ConfiguracaoEvolutionApi`). Falha nao bloqueia fluxo.

**Consequencias**:
- Sem dependencia de provedor pago.
- Cada unidade pode ter sua propria instancia/numero.
- Robustez via `NotificacaoPendente` + worker de retry.

## ADR-006 — Email via SMTP / SendGrid (a confirmar)

**Contexto**: Email e canal redundante a WhatsApp para chamada de veiculo.

**Decisao**: provedor a definir na arquitetura (provavelmente SendGrid ou AWS SES). MVP pode comecar com SMTP simples.

**Consequencias**: configuracao por unidade ou global, decidir na arquitetura.

## ADR-007 — Notificacao em tempo real via SignalR

**Contexto**: Painel de lideres precisa atualizar em tempo real; porteiros precisam saber quando um veiculo foi chamado.

**Decisao**: SignalR no proprio backend C#. Sem servico externo (Pusher etc) no MVP.

**Consequencias**:
- Stack uniforme.
- Suficiente para o volume previsto.
- Necessita de configuracao de sticky session se for escalar horizontalmente.

## ADR-008 — Auditoria via EventoFluxo (event log leve)

**Contexto**: LGPD exige rastreio de acoes; auditoria e questao de seguranca patrimonial.

**Decisao**: cada mudanca de estado e edicao gera `EventoFluxo` imutavel (insert-only). Estado canonico do `MovimentoPortaria` e mantido por consulta direta a tabela; historico e reconstruido pelo log de eventos.

**Consequencias**:
- Auditoria automatica sem custo adicional.
- Tabela `eventos_fluxo` cresce; particionar por mes se necessario.
- Edicao de campos criticos auditada com diff.

## ADR-009 — Lock otimista em MovimentoPortaria

**Contexto**: Dois lideres podem clicar "Chamar Veiculo" no mesmo movimento simultaneamente.

**Decisao**: usar `[Timestamp]` em `MovimentoPortaria` via EF Core. Conflito retorna erro de dominio `MovimentoJaLiberado`. UI trata mostrando "Outro lider chamou primeiro".

**Consequencias**: solucao gratuita do EF; nao requer Redis ou lock distribuido.

## ADR-010 — Anexos em filesystem ou S3

**Contexto**: Anexos podem ser fotos pesadas (~3-5MB). Salvar bytes no Postgres e ruim.

**Decisao**: armazenar em filesystem do servidor para MVP, com path em `Anexo.Url`. Migracao para S3-compativel (MinIO local ou AWS) prevista pos-MVP. Estrutura `/anexos/{UnidadeId}/{MovimentoId}/{guid}-{nome}.{ext}`.

**Consequencias**:
- Simples para MVP single-server.
- Backup precisa cobrir filesystem.
- Migrar para object storage quando rodar em multi-replica.

## ADR-011 — Worker de notificacoes via BackgroundService

**Contexto**: Notificacoes (WA, email) sao assincronas e idempotentes.

**Decisao**: `IHostedService` que polla `NotificacaoPendente` com `Status=Pendente` ou `Falhou` e `ProximaTentativa <= now`. Backoff exponencial (1m, 5m, 15m, 1h). Descarta apos 24h.

**Consequencias**:
- Sem dependencia de fila externa (RabbitMQ, Redis) no MVP.
- Pode ser substituido por fila real depois sem mudar o dominio.

## ADR-012 — Idioma do dominio: PT-BR

**Contexto**: Convencao do framework e clareza para a equipe da Frigoestrela.

**Decisao**: nomes de classes, propriedades, comandos, eventos, mensagens em **PT-BR**. So termos universais (Repository, Handler, etc) ficam em ingles.

**Consequencias**: codigo le como o negocio fala. Sem custo de traducao.

## ADR-013 — Sem heranca em Pessoa (Motorista vs Usuario)

**Contexto**: tentacao de extrair classe `Pessoa` para reuso.

**Decisao**: `Motorista` (externo) e `Usuario` (interno) sao agregados separados sem heranca. Reuso de campos via value-object `DadosContato` apenas se aparecer redundancia real depois.

**Consequencias**: codigo mais simples, sem hierarquia desnecessaria.

## ADR-014 — Retencao de dados indefinida

**Contexto**: Cliente nao quer politica automatica de expurgo.

**Decisao**: nenhum job automatico de retencao no MVP. Anonimizacao apenas mediante solicitacao formal do titular (LGPD).

**Consequencias**: revisitar quando volume tornar custo de armazenamento relevante.

## ADR-015 — Web responsivo, mobile fora do MVP

**Contexto**: Lideres podem usar tablet no chao de fabrica; motorista vai ter app no futuro.

**Decisao**: MVP e web responsivo apenas. Mobile (Flutter, conforme `.framework/nucleo/`) entra em fase posterior.

**Consequencias**: API ja deve expor endpoints suficientes para o app futuro consumir; preparar contratos REST estaveis.
