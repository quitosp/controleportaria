# 8. Regras de negocio

Regras invariaveis do dominio Controle de Portaria. Cada regra tem um ID `RN-NNN` que sera citado em historias, contratos e codigo (via comentario `// RN-NNN`).

---

### RN-001 — Toda operacao exige usuario autenticado

- **Agregados envolvidos:** Usuario, MovimentoPortaria
- **Gatilho:** qualquer endpoint de chegada, chamada, entrada, saida, edicao
- **Condicao:** request tem JWT valido com `UnidadeId` e `Papel` validos
- **Acao se violada:** retorna HTTP 401 (Unauthorized)
- **Severidade:** critica
- **Justificativa:** rastreabilidade legal e patrimonial. Substitui a selecao manual de "Funcionario" do sistema antigo.
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-002 — Acoes registram automaticamente Usuario + Timestamp + Portaria

- **Agregados envolvidos:** MovimentoPortaria, EventoFluxo
- **Gatilho:** qualquer mudanca de estado ou edicao
- **Condicao:** novo `EventoFluxo` deve conter `UsuarioId`, `Quando`, e a portaria do contexto deve estar associada ao movimento
- **Acao se violada:** comando rejeitado (`DominioException`), mudanca nao persiste
- **Severidade:** critica
- **Justificativa:** auditoria LGPD; substitui escolha manual de funcionario.
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-003 — Destino Patio Interno na chegada exige "Autorizado por"

- **Agregados envolvidos:** MovimentoPortaria
- **Gatilho:** ao registrar chegada com `Destino = Interno`
- **Condicao:** campo `AutorizadoPorChegada` (texto) preenchido (nao vazio)
- **Acao se violada:** `DominioException("AutorizadoPor obrigatorio quando destino e Interno")` (HTTP 400)
- **Severidade:** critica
- **Justificativa:** se o lider autorizou via radio/telefone, isso precisa ficar registrado. No futuro, este campo sera substituido pela acao "Chamar Veiculo" do painel.
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-004 — Motorista Bloqueado dispara alerta + observacao + auditoria

- **Agregados envolvidos:** Motorista, MovimentoPortaria, EventoFluxo
- **Gatilho:** ao registrar chegada com motorista de status `Bloqueado`
- **Condicao:** porteiro recebe alerta visual; campo `Observacao` obrigatorio para prosseguir
- **Acao se violada (sem observacao):** `DominioException("Motorista bloqueado: observacao obrigatoria")`
- **Acao apos prosseguir:** persistir movimento + gerar `EventoFluxo: AlertaBloqueio` com motivo do bloqueio do motorista e a decisao do porteiro
- **Severidade:** alta
- **Justificativa:** porteiro decide, mas a decisao fica auditada para investigacao posterior.
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-005 — Saida com motivo Descarga: apenas timestamp + porteiro

- **Agregados envolvidos:** MovimentoPortaria
- **Gatilho:** ao registrar saida com `MotivoEntrada = Descarga`
- **Condicao:** nenhum campo extra obrigatorio alem dos automaticos
- **Acao:** muda estado para `Saiu`, registra `DataSaida` e `PorteiroSaidaId`
- **Severidade:** critica
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-006 — Saida com motivo Carga: NF + Lacre + Destino obrigatorios

- **Agregados envolvidos:** MovimentoPortaria
- **Gatilho:** ao registrar saida com `MotivoEntrada = Carga`
- **Condicao:** `DadosCargaSaida.NumeroNF`, `Lacre`, `Destino` preenchidos
- **Acao se violada:** `DominioException` listando o(s) campo(s) faltante(s)
- **Severidade:** critica
- **Justificativa:** rastreabilidade comercial e fiscal da carga que sai da unidade.
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-007 — Saida de Container Exportacao: + Container + Contrato

- **Agregados envolvidos:** MovimentoPortaria
- **Gatilho:** ao registrar saida com `MotivoEntrada = Carga` e `TipoCarga = Container`
- **Condicao:** alem dos campos de RN-006, `DadosCargaSaida.NumeroContainer` e `Contrato` preenchidos
- **Acao se violada:** `DominioException` listando faltas
- **Severidade:** critica
- **Justificativa:** exigencia aduaneira/exportacao; futuro upload de fotos via mobile.
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-008 — Maquina de estados sem pulos

- **Agregados envolvidos:** MovimentoPortaria
- **Gatilho:** ao tentar mudar `Estado`
- **Condicao:** transicao deve ser valida segundo a maquina:
  - `NoPateoExterno -> ChamadoParaInterno` ou `NoPateoExterno -> NoPateoExterno` (recancelamento)
  - `ChamadoParaInterno -> NoPateoInterno` ou `ChamadoParaInterno -> NoPateoExterno` (expirada)
  - `NoPateoInterno -> Saiu`
  - `NoLavador -> NoPateoInterno`
  - Qualquer estado nao-terminal `-> Cancelado` ou `-> Desistencia`
- **Acao se violada:** `DominioException("Transicao invalida {de} -> {para}")`
- **Severidade:** critica
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-009 — Cancelar/Desistir exige observacao

- **Agregados envolvidos:** MovimentoPortaria, EventoFluxo
- **Gatilho:** ao mudar estado para `Cancelado` ou `Desistencia`
- **Condicao:** campo `Observacao` no comando preenchido
- **Acao se violada:** `DominioException("Observacao obrigatoria")`
- **Severidade:** alta
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-010 — Auto-fill por placa sugere ultimo movimento

- **Agregados envolvidos:** Veiculo, MovimentoPortaria
- **Gatilho:** consulta de auto-fill no formulario de chegada (porteiro digitando placa)
- **Condicao:** existe ao menos um `MovimentoPortaria` em estado terminal (`Saiu`/`Cancelado`/`Desistencia`) com aquela placa
- **Acao:** retorna `Transportadora` e `TipoCarga` do mais recente. Porteiro pode aceitar ou sobrescrever.
- **Severidade:** media
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-011 — Chamar Veiculo dispara WhatsApp + Email + SignalR

- **Agregados envolvidos:** MovimentoPortaria, NotificacaoPendente
- **Gatilho:** ao mudar estado de `NoPateoExterno` para `ChamadoParaInterno`
- **Condicao:** registra `LiderQueAutorizouId`, `DataChamada`. Enfileira `NotificacaoPendente` para Whatsapp (motorista), Email (motorista, se cadastrado), Socket (portaria de chegada).
- **Acao se violada (transicao invalida):** RN-008 cobre.
- **Severidade:** alta
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-012 — Carreta com movimento aberto bloqueia nova chegada

- **Agregados envolvidos:** Veiculo, MovimentoPortaria
- **Gatilho:** ao tentar registrar chegada
- **Condicao:** nao pode existir outro `MovimentoPortaria` da mesma `CarretaId` em estado nao-terminal na unidade
- **Acao se violada:** `DominioException("Carreta {placa} tem movimento aberto HIST-XXX em estado YYY")`
- **Severidade:** critica
- **Justificativa:** evita duplicidade. Se houver erro, deve ser resolvido cancelando o aberto antes.
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-013 — Lock otimista em "Chamar Veiculo"

- **Agregados envolvidos:** MovimentoPortaria
- **Gatilho:** dois lideres clicam "Chamar" simultaneamente
- **Condicao:** EF Core checa `[Timestamp]` no commit
- **Acao se violada:** `DbUpdateConcurrencyException` -> traduzir para `ConflitoException("MovimentoJaLiberado")` (HTTP 409). UI do segundo lider mostra "Outro lider chamou primeiro".
- **Severidade:** alta
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-014 — Multi-tenant: usuario so ve dados da sua unidade

- **Agregados envolvidos:** Todos os agregados com `UnidadeId`
- **Gatilho:** qualquer query
- **Condicao:** filtro global no DbContext (`HasQueryFilter` por `UnidadeId == _unidadeContext.UnidadeId`)
- **Acao se violada:** dados de outra unidade vazariam — incidente critico
- **Severidade:** critica
- **Justificativa:** isolamento de tenants. Crucial mesmo com uma unidade hoje, para nao precisar refatorar depois.
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-015 — Auditoria imutavel via EventoFluxo

- **Agregados envolvidos:** EventoFluxo, MovimentoPortaria
- **Gatilho:** qualquer mudanca de estado ou edicao de `MovimentoPortaria`
- **Condicao:** `EventoFluxo` correspondente persistido na mesma transacao
- **Acao se violada:** rollback (mudanca nao persiste sem evento)
- **Severidade:** alta
- **Justificativa:** LGPD + seguranca patrimonial.
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-016 — Anexos: 10MB max, formatos restritos

- **Agregados envolvidos:** Anexo
- **Gatilho:** ao fazer upload
- **Condicao:** tamanho <= 10MB; ContentType in {image/jpeg, image/png, application/pdf}
- **Acao se violada:** HTTP 400 com mensagem clara
- **Severidade:** media
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-017 — Notificacoes assincronas nao bloqueiam fluxo

- **Agregados envolvidos:** NotificacaoPendente, MovimentoPortaria
- **Gatilho:** ao gerar uma notificacao (RN-011)
- **Condicao:** persistencia da `NotificacaoPendente` ocorre na mesma transacao da mudanca de estado; envio externo e assincrono
- **Acao em falha de envio:** retry com backoff exponencial (1m, 5m, 15m, 1h); descartar apos 24h com `Status = Descartada` e `UltimoErro` preenchido
- **Severidade:** alta
- **Justificativa:** WhatsApp/Email instavel nao pode bloquear lider de chamar veiculo.
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-018 — NF opcional na chegada, obrigatoria na saida de Carga

- **Agregados envolvidos:** MovimentoPortaria
- **Gatilho:** validacao de chegada x saida
- **Condicao:** chegada nao exige `NumeroNF`. Saida com motivo Carga exige (RN-006).
- **Severidade:** alta
- **Justificativa:** caminhao chega sem NF impressa em alguns casos; NF chega depois.
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-019 — Validacao de "movimento aberto" e por carreta, nao por motorista

- **Agregados envolvidos:** Motorista, Veiculo, MovimentoPortaria
- **Gatilho:** validacao na chegada
- **Condicao:** mesmo motorista pode ter mais de um movimento ativo se for em carretas distintas
- **Severidade:** media
- **Justificativa:** porteiro pode operar entrada de motorista que ja tem outro caminhao na unidade.
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-020 — TTL da chamada e 30 minutos

- **Agregados envolvidos:** MovimentoPortaria
- **Gatilho:** worker de housekeeping (BackgroundService) a cada minuto
- **Condicao:** movimento em `ChamadoParaInterno` ha mais de 30min sem confirmacao
- **Acao:** marcado como "expirado" (sinalizacao no painel; nao muda estado automaticamente, espera lider recancelar). Alternativa futura: auto-recancelamento.
- **Severidade:** media
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-021 — Edicao de campos criticos pos-entrada exige Lider+

- **Agregados envolvidos:** MovimentoPortaria, EventoFluxo, Usuario
- **Gatilho:** ao editar campos `CarretaId`, `MotoristaId`, `Motivo` em movimento ja em estado >= `NoPateoInterno`
- **Condicao:** `Usuario.Papel` in {Lider, Supervisor, Admin}
- **Acao se violada:** HTTP 403 (Forbidden)
- **Severidade:** alta
- **Justificativa:** evita porteiro corrigir em silencio dado critico ja registrado oficialmente.
- **Implementada em:** *(preenchido apos `/impl`)*

### RN-022 — Retencao indefinida (sem expurgo automatico)

- **Agregados envolvidos:** todos
- **Gatilho:** N/A
- **Condicao:** sistema nao executa job de retencao
- **Acao:** anonimizacao apenas via solicitacao formal LGPD (processo manual)
- **Severidade:** baixa
- **Justificativa:** decisao explicita do cliente.
- **Implementada em:** N/A
