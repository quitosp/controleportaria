# 4. Casos de Uso

## CDU-001 — Login

**Ator**: qualquer usuario.
**Pre**: usuario cadastrado e ativo.
**Fluxo principal**:
1. Usuario informa login e senha.
2. Sistema valida credenciais.
3. Sistema retorna JWT com claims (papel, `UnidadeId`, `PortariaPadraoId`).
4. UI carrega dashboard conforme papel.
**Fluxo alternativo**: senha invalida -> incrementa contador; apos 5 erros em 1 min, bloqueia IP por 15 min.
**Pos**: usuario autenticado, sessao ativa.

## CDU-002 — Cadastrar chegada

**Ator**: Porteiro.
**Pre**: porteiro logado, vinculado a uma portaria ativa.
**Fluxo principal**:
1. Porteiro digita placa da carreta.
2. Sistema busca ultimo `MovimentoPortaria` daquela placa e sugere `Transportadora` e `TipoCarga`.
3. Porteiro preenche/ajusta campos obrigatorios: motorista, motivo, patio destino.
4. Se patio destino = Interno: campo "Autorizado por" obrigatorio.
5. Se motorista esta `Bloqueado`: sistema exibe alerta vermelho com motivo. Porteiro decide prosseguir e preenche observacao.
6. Sistema valida que carreta nao tem movimento aberto na unidade.
7. Sistema cria `MovimentoPortaria` com estado inicial: `NoPateoExterno` se Externo; `NoPateoInterno` se Interno; `NoLavador` se Lavador.
8. Sistema gera `EventoFluxo: ChegadaRegistrada`.
9. Se motorista bloqueado: gera `EventoFluxo: AlertaBloqueio`.
10. Porteiro pode anexar foto(s) da chegada.

**Fluxo alternativo A** (placa nova): nenhum movimento anterior; porteiro preenche tudo manualmente.
**Fluxo alternativo B** (motorista nao cadastrado): porteiro abre dialog de cadastro rapido sem perder o fluxo de chegada.
**Fluxo alternativo C** (carreta com movimento aberto): sistema bloqueia com mensagem "Movimento HIST-XXX em estado YYY ainda aberto". Porteiro deve resolver o aberto antes.

**Pos**: movimento criado, evento de chegada gerado, anexos opcionalmente vinculados.

## CDU-003 — Visualizar painel de chamada

**Ator**: Lider, Supervisor, Admin.
**Pre**: usuario logado com papel `Lider+`.
**Fluxo principal**:
1. Usuario abre painel.
2. Sistema retorna lista paginada de movimentos `NoPateoExterno` da unidade.
3. UI atualiza em tempo real via SignalR (chegadas novas, mudancas de estado).
**Pos**: lider visualiza fila atual.

## CDU-004 — Chamar veiculo

**Ator**: Lider, Supervisor, Admin.
**Pre**: movimento em estado `NoPateoExterno`.
**Fluxo principal**:
1. Lider clica "Autorizar entrada" no painel.
2. Sistema valida estado atual (`NoPateoExterno`); se outro lider ja chamou (lock otimista), retorna erro "Movimento ja liberado por outro usuario".
3. Sistema muda estado para `ChamadoParaInterno`, registra `LiderQueAutorizouId` + timestamp.
4. Sistema gera `EventoFluxo: ChamadaAutorizada`.
5. Sistema enfileira: WhatsApp ao motorista (Evolution API), email ao motorista (se cadastrado), notificacao SignalR para a portaria de chegada.
6. UI do lider e da portaria atualizam.

**Fluxo alternativo** (canal de notificacao falha): sistema persiste `NotificacaoPendente` por canal; processa retry com backoff exponencial (1m, 5m, 15m, 1h, dropa apos 24h).
**Pos**: motorista convocado, portaria sabe quem vai entrar.

## CDU-005 — Recancelar chamada expirada

**Ator**: Lider, Supervisor, Admin.
**Pre**: movimento em estado `ChamadoParaInterno` ha mais de 30 minutos (TTL configuravel).
**Fluxo principal**:
1. Painel destaca movimentos com chamada expirada.
2. Lider clica "Recancelar".
3. Sistema retorna estado para `NoPateoExterno`.
4. Gera `EventoFluxo: ChamadaExpirada`.
**Pos**: motorista volta para a fila do patio externo; lider pode rechamar mais tarde.

## CDU-006 — Confirmar entrada no patio interno

**Ator**: Porteiro.
**Pre**: movimento em estado `ChamadoParaInterno`.
**Fluxo principal**:
1. Porteiro localiza movimento (auto-destaque por SignalR ou busca por placa).
2. Porteiro clica "Confirmar entrada".
3. Sistema muda estado para `NoPateoInterno`.
4. Gera `EventoFluxo: EntradaConfirmada`.
5. Porteiro pode anexar foto(s).

**Fluxo alternativo** (motorista nao apareceu): porteiro nao confirma; chamada expira pelo TTL.
**Pos**: veiculo registrado dentro do patio interno.

## CDU-007 — Registrar saida

**Ator**: Porteiro.
**Pre**: movimento em estado `NoPateoInterno`.
**Fluxo principal**:
1. Porteiro busca por placa.
2. Sistema apresenta tela de saida.
3. Campos exibidos conforme `MotivoEntrada`:
   - **Descarga**: nenhum campo extra alem de timestamp (auto) e observacao opcional.
   - **Carga**: `NumeroNF`, `Lacre`, `Destino` obrigatorios.
   - **Container exportacao** (Carga + TipoCarga=Container): adiciona `NumeroContainer` e `Contrato` obrigatorios.
4. Porteiro anexa foto(s) de saida (lacre, container, etc).
5. Sistema valida campos.
6. Sistema muda estado para `Saiu`.
7. Gera `EventoFluxo: SaidaRegistrada`.
**Pos**: movimento finalizado.

## CDU-008 — Cancelar movimento

**Ator**: Porteiro+.
**Pre**: estado != `Saiu`.
**Fluxo principal**:
1. Usuario abre detalhe do movimento.
2. Clica "Cancelar".
3. Informa observacao obrigatoria.
4. Sistema muda estado para `Cancelado`.
5. Gera `EventoFluxo: Cancelamento`.
**Pos**: movimento finalizado sem saida.

## CDU-009 — Registrar desistencia

**Ator**: Porteiro+.
**Pre**: estado != `Saiu`.
**Fluxo**: identico ao CDU-008, com estado final `Desistencia` e evento `Desistencia`.

## CDU-010 — Bloquear/desbloquear motorista

**Ator**: Supervisor, Admin.
**Fluxo principal**:
1. Admin abre cadastro do motorista.
2. Altera status: Ativo / Pendente / Bloqueado.
3. Informa motivo (texto livre obrigatorio).
4. Sistema persiste alteracao com auditoria.
**Pos**: motorista marcado; proxima chegada com ele aciona alerta.

## CDU-011 — Editar movimento

**Ator**: Porteiro+ (com restricoes por papel).
**Pre**: movimento existe; campos criticos exigem `Lider+` apos `NoPateoInterno`.
**Fluxo principal**:
1. Usuario abre detalhe e clica "Editar".
2. Altera campo permitido pelo papel.
3. Sistema persiste e gera `EventoFluxo: EdicaoCampo` com diff (antes/depois).
**Pos**: movimento atualizado, edicao auditada.

## CDU-012 — Visualizar auditoria de movimento

**Ator**: Supervisor, Admin.
**Fluxo principal**:
1. Usuario abre detalhe do movimento.
2. Sistema lista todos `EventoFluxo` em ordem cronologica.
3. Cada evento exibe: tipo, usuario, timestamp, dados (antes/depois quando edicao).
**Pos**: rastreabilidade completa.

## CDU-013 — Anexar arquivo

**Ator**: Porteiro+, em qualquer estagio.
**Pre**: movimento existe.
**Fluxo principal**:
1. Usuario seleciona arquivo (max 10MB; jpg/jpeg/png/pdf).
2. Sistema valida tamanho e formato.
3. Sistema persiste anexo com `Estagio` (Chegada / Entrada / Saida), usuario, timestamp.
**Fluxo alternativo**: arquivo invalido -> erro de validacao.
**Pos**: anexo vinculado ao movimento.

## CDU-014 — Cadastrar motorista no fluxo

**Ator**: Porteiro+.
**Pre**: durante cadastro de chegada, motorista nao encontrado.
**Fluxo principal**:
1. Porteiro clica "Novo motorista" no autocomplete.
2. Modal abre com campos: nome, CPF, WhatsApp, email (opcional), observacao.
3. Sistema valida CPF unico na unidade e cria com status `Ativo`.
4. Modal fecha; novo motorista ja selecionado no formulario de chegada.
**Pos**: motorista cadastrado e usado no movimento atual.

## CDU-015 — Cadastrar veiculo no fluxo

Identico ao CDU-014, para placa nova. Validacao de formato de placa (Mercosul ou tradicional).
