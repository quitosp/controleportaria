---
name: implementar-historia
description: Implementa uma historia respeitando o tipo de capacidade. Crud vai direto via scaffold; demais tipos exigem artefato aprovado + scaffold de capacidade + IMPLEMENTACAO COMPLETA da logica seguindo o contrato. Triggers: "/impl HIST-NNN", "implementar HIST-NNN", "/impl proxima".
---

# Skill: implementar-historia

## Filosofia: zero TODOs em commit
Capacidades nao-CRUD precisam de **logica funcional implementada** lendo o contrato/mockup aprovado. NUNCA commitar esqueleto com `// TODO`. Claude le o contrato, gera estrutura via scaffold, e completa a logica via Edit.

## Entrada
- ID da historia ou "proxima"
- `estado/historias/HIST-NNN.yaml` (com `tipo`, `persona`, `motivo`, `artefato`)
- `estado/artefatos/HIST-NNN.md` (mockup ou contrato APROVADO se tipo != crud/architecture)
- **Contexto narrativo** (campos `persona` + `motivo` da historia): Claude le PRIMEIRO antes de escrever qualquer codigo. Usa pra:
  - Decidir UX coerente (se `persona: Cliente final`, formularios sao simples e linguagem coloquial; se `persona: Admin`, mostra mais filtros e dados tecnicos)
  - Priorizar elementos no scaffold (campos mais usados pela persona ficam no topo do form)
  - Questionar regras incoerentes ("a persona 'cliente' nao deveria ver dados de outros clientes — vou aplicar filtro por usuario logado")
  - Se a persona estiver vazia (tipos internos como `architecture`/`refactor`), pular essa heuristica

## Gates pre-implementacao
1. **Dependencias concluidas?** Se nao, abortar.
2. **Artefato aprovado?** Se tipo != crud/architecture e `artefato.aprovado: false` → abortar com sugestao `/artefato HIST-NNN` + `/aprovar HIST-NNN`.
3. **Estado coerente?** `pendente` ok; outros perguntar.

## Processo por tipo

### tipo: crud
Scaffold direto cobre tudo:
```
python .framework/scripts/csharp_scaffold.py {Singular} --plural {Plural} --campos "..." --tudo
```
Ou `frontend_scaffold.py --tudo` se frontend.

### tipo: architecture
**IMPORTANTE — pastas separadas**: a API vai em `api/` e o frontend em `web/` (sub-pastas da raiz). NUNCA criar API e Web na mesma pasta — atrapalha solution C#, mistura node_modules com bin/obj, e quebra `/run`.

Comandos:
```
# Backend C#
python .framework/scripts/novo_projeto.py csharp-portaria <nome> --auth --destino api
python .framework/scripts/aplicar_observabilidade_csharp.py --raiz api
python .framework/scripts/aplicar_seguranca_csharp.py --prod-mode --raiz api

# Frontend Next.js (se PRD tem plataforma web)
mkdir web && cd web
npx create-next-app@latest . --typescript --tailwind --app --src-dir --use-npm
npm install axios @tanstack/react-query react-hook-form @hookform/resolvers zod sonner lucide-react jwt-decode
cd ..
python .framework/scripts/setup_ui.py --raiz web
python .framework/scripts/sincronizar_api_url.py --api api --front web
```

Apos o setup, voce tem:
```
meu-projeto/
├── .framework/
├── api/         # backend
└── web/         # frontend
```

### tipo: business-flow / integration / report / automation

**Processo de 3 passos** (executar SEMPRE nessa ordem):

#### Passo 1 — Scaffold de estrutura
```
python .framework/scripts/csharp_scaffold_capacidade.py --tipo <T> --nome <N> [--agregado <A>] --raiz <projeto>
```
Cria arquivos esqueleto + atualiza DI + adiciona endpoint no controller (business-flow).

#### Passo 2 — Ler artefato + regras de negocio
1. `Read` em `estado/artefatos/HIST-NNN.md`
2. **Ler `regras_negocio[]` da historia**. Para cada `RN-NNN`:
   - `Read` em `documentacao/8-regras-negocio.md` para extrair o bloco da regra
   - Anotar: gatilho, condicao, acao se violada, severidade
3. Identificar do artefato + regras:
   - Campos de entrada (com validacoes formais via FluentValidation)
   - **Validacoes de regra de negocio** (RN-NNN) — implementadas no Handler, NAO no Comand (porque dependem de estado de outras entidades)
   - Saida esperada (estrutura JSON)
   - Erros mapeados (codigos HTTP) — cada RN com `acao_se_violada: lanca DominioException` vira um possivel erro 400/409
   - Fluxo (passos numerados)
   - Side effects (tabelas, eventos)
   - Idempotencia (se webhook/job)
   - Servicos externos (se integration)
4. Mapear cada TODO no codigo gerado para um item do contrato OU uma RN.

#### Passo 3 — Implementar via Edit
Para cada arquivo gerado, **substituir TODOs por codigo real** seguindo o contrato:

**business-flow** (Entrada + Handler):
- Entrada: definir properties usando exatamente os campos do contrato. Adicionar `RuleFor` para cada validacao **formal** (campos obrigatorios, formatos, ranges fixos).
- Handler:
  - Injetar repositorios necessarios (mencionados em "Side effects" do contrato)
  - Implementar fluxo passo a passo: validar → buscar → verificar conflitos → criar entidades → persistir
  - **Para cada RN-NNN listada na historia**: implementar a checagem da regra com **comentario obrigatorio** identificando a regra. Exemplo:
    ```csharp
    // RN-001 — Saldo nunca pode ficar negativo
    var saldoApos = conta.SaldoAtual - entrada.Valor;
    if (saldoApos < 0)
        throw new DominioException("Saldo insuficiente");
    ```
    O comentario `// RN-NNN` e obrigatorio — o `revisar_codigo.py` valida que cada RN listada na historia tem comentario correspondente no codigo, e falha o gate se nao tem.
  - Mapear cada erro do contrato + cada RN com `acao: lanca DominioException` para um throw com mensagem clara
  - Retornar `data` com IDs/dados conforme contrato
- Se contrato/RN menciona regra que precisa de dados de outras tabelas: adicionar metodo no repositorio correspondente (ex: `CalcularSaldo`).

**integration** (Settings + Service + WebhookController):
- Settings: campos especificos do servico (api keys, base url, timeouts, etc) do contrato.
- Service.Processar: implementar parsing/transformacao + chamadas HTTP (Dio/HttpClient) + persistencia. Sempre considerar idempotencia (tabela auxiliar com chave do contrato).
- WebhookController: rota e validacao de assinatura ja vem prontos. Ajustar headers conforme contrato.
- Se precisa entidade auxiliar (idempotencia): criar manualmente em `Repositorios/Contexto/` + adicionar `DbSet` + migration.

**report** (Query + Saida + Controller partial):
- Saida: campos do mockup (KPIs, listas, breakdowns).
- Query: LINQ com `.Where`, `.GroupBy`, `.Sum`, `.Select`. Evitar carregar dados em memoria — agregar no banco quando possivel.
- Controller: parametros de filtro do mockup (data, periodo, categoria, etc).

**automation** (Worker):
- Definir intervalo conforme contrato (`TimeSpan.FromHours(N)`, `FromMinutes(N)`).
- Implementar logica de processamento dentro do `while`.
- Sempre tratar excecoes (job nao pode quebrar host).
- Persistir resultado se aplicavel (ex: notificar usuarios processados).

#### Passo 4 — Validacao + Review OBRIGATORIO

**Toda implementacao passa pelo gate de qualidade automaticamente, em CADA `/impl`. Nenhuma historia pode ser marcada como `concluida` se o review aponta CRITICO ou ALTO.**

1. Se mudou schema do banco (nova tabela/coluna): `python .framework/scripts/migrate.py`
2. `dotnet build` (ou `parse_dotnet_errors.py` se erro). Se erro: corrigir e repetir.
3. **Review obrigatorio** — rodar e validar:
   ```
   python .framework/scripts/pos_implementacao.py --raiz <projeto>
   ```
   Esse script encadeia:
   - `revisar_codigo.py` (estrutura contra blueprint)
   - `verificar_seguranca.py` (deps vulneraveis, secrets, headers)
   - `indexar.py` (reindex)

4. **Avaliar saida do review:**
   - **0 desvios CRITICO/ALTO** → segue.
   - **>=1 CRITICO ou ALTO** → STOP. Mostrar desvios ao usuario, perguntar:
     ```
     Review apontou X desvios criticos/altos. Posso corrigir agora antes de marcar
     a historia como concluida? [sim recomendado / nao quero pular]
     ```
     Se sim: corrigir cada desvio, voltar ao passo 2 (rebuild + re-review).
     Se nao: NAO marcar como concluida. Marcar `estado: pendente_review` e abortar.
   - **MEDIO/INFO** → reportar mas nao bloquear.

5. So apos review limpo: marcar `estado: concluida` na historia + incrementar `projeto.yaml > historias_concluidas`.

**Resumo da regra de ouro:** uma historia so e `concluida` se passou no review automatico. Sem excecoes.

## Saida
- Arquivos criados via scaffold
- Arquivos editados via Edit (sem TODOs)
- Build OK
- Pos-implementacao OK
- Historia marcada como concluida

## Restricoes (importantissimo)
- **NUNCA commitar `// TODO`** — implementar tudo lendo contrato
- **NUNCA pular leitura do contrato** — e a fonte de verdade
- **NUNCA inventar regras** que nao estao no contrato — se faltar info, pedir esclarecimento ao usuario
- **NUNCA marcar historia como `concluida` sem rodar review** (`pos_implementacao.py`) — gate obrigatorio
- **NUNCA passar pelo review com desvios CRITICO/ALTO** — corrigir primeiro
- NAO criar API e Web na mesma pasta — sempre `api/` e `web/` separadas
- NAO ler arquivo grande sem `token_check.py`
- NAO usar Glob/Grep se index existe — usar `buscar.py`
- NAO modificar historias ja `concluida` sem motivo claro

## Exemplo de fluxo completo (business-flow: TransferirEntreContas)

1. Usuario: `/impl HIST-005`
2. Claude le `historias/HIST-005.yaml` → tipo `business-flow`, artefato aprovado
3. Claude le `artefatos/HIST-005.md` → contrato com 4 campos de entrada, 3 erros, 5 passos
4. Claude roda: `python .framework/scripts/csharp_scaffold_capacidade.py --tipo business-flow --nome TransferirEntreContas --agregado Movimento`
5. Claude faz Edit em `TransferirEntreContasEntrada.cs`: 4 properties + 4 RuleFor
6. Claude faz Edit em `TransferirEntreContasHandler.cs`: injetar IContaRepositorio + IMovimentoRepositorio + implementar 5 passos
7. Claude adiciona `CalcularSaldo` em IMovimentoRepositorio + impl
8. Claude roda `dotnet build` → 0 erros
9. Claude roda `pos_implementacao.py` → tudo OK
10. Claude marca HIST-005 como `concluida`
11. Claude reporta: "HIST-005 concluida. /impl proxima ou /commit HIST-005"

Tudo automatico do ponto de vista do usuario. Logica REAL implementada, sem TODOs.
