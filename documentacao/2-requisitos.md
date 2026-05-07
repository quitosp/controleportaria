# 2. Requisitos

## 2.1 Requisitos Funcionais (RF)

### Autenticacao e identificacao
- **RF-001** Sistema deve exigir login (usuario+senha) para qualquer operacao de chegada, chamada, entrada ou saida.
- **RF-002** Usuario logado, portaria atual e timestamp devem ser registrados automaticamente em cada acao critica (chegada, mudanca de estado, edicao, saida).
- **RF-003** Usuario deve ter um papel: `Porteiro`, `Lider`, `Supervisor`, `Admin`.
- **RF-004** Cada usuario tem uma portaria padrao vinculada; pode trocar de portaria ativa apos login.

### Cadastro de chegada
- **RF-010** Porteiro cadastra chegada com: placa de carreta (obrigatorio), placa de cavalo, placa de carreta secundaria, container, tipo de carga (obrigatorio), motivo (obrigatorio), nota fiscal (opcional), contrato, produto, setor, motorista (obrigatorio), transportadora (obrigatorio), patio destino (obrigatorio: Interno/Externo/Lavador), observacao.
- **RF-011** Ao digitar uma placa, sistema busca o ultimo `MovimentoPortaria` daquela placa e sugere `Transportadora` e `TipoCarga`. Porteiro pode aceitar ou sobrescrever.
- **RF-012** Se patio destino = Interno, campo "Autorizado por" (texto livre — nome de quem autorizou via radio/telefone) e obrigatorio.
- **RF-013** Se motorista esta `Bloqueado`, sistema exibe alerta vermelho com motivo e exige observacao obrigatoria; porteiro decide se prossegue. A decisao gera `EventoFluxo: AlertaBloqueio`.
- **RF-014** Sistema bloqueia cadastro de chegada se a placa de carreta ja tem movimento aberto (estado != `Saiu`/`Cancelado`/`Desistencia`) em qualquer portaria da unidade.
- **RF-015** Porteiro pode cadastrar novo motorista, transportadora ou veiculo durante a chegada, sem sair do fluxo.

### Painel de chamada (Lider)
- **RF-020** Lider/Supervisor visualizam, em tempo real, todos os veiculos com estado `NoPateoExterno` da unidade (independente de portaria de chegada).
- **RF-021** Painel exibe: placa de carreta, transportadora, motorista, motivo, produto, setor, hora de chegada, tempo de espera.
- **RF-022** Lider clica em "Autorizar entrada"; sistema muda estado para `ChamadoParaInterno`, registra `LiderQueAutorizouId` + timestamp, e dispara WhatsApp ao motorista, email ao motorista (se cadastrado) e notificacao SignalR para a portaria de chegada.
- **RF-023** Falha em qualquer canal de notificacao (WhatsApp, email, SignalR) nao bloqueia a mudanca de estado; gera `NotificacaoPendente` para retry assincrono.
- **RF-024** Estado `ChamadoParaInterno` tem TTL de 30 minutos (configuravel). Apos expirar, lider pode "recancelar chamada", retornando o veiculo para `NoPateoExterno` com `EventoFluxo: ChamadaExpirada`.

### Confirmacao de entrada
- **RF-030** Porteiro da portaria de chegada confirma a entrada do veiculo (estado vai de `ChamadoParaInterno` para `NoPateoInterno`). Acao registra porteiro + timestamp.

### Saida
- **RF-040** Porteiro localiza movimento aberto pela placa de carreta e registra saida.
- **RF-041** Saida com `MotivoEntrada=Descarga`: apenas timestamp + porteiro + observacao opcional.
- **RF-042** Saida com `MotivoEntrada=Carga`: campos obrigatorios `NumeroNF`, `Lacre`, `Destino`.
- **RF-043** Saida de container exportacao (heuristica: `MotivoEntrada=Carga` + `TipoCarga=Container`): adicionalmente `NumeroContainer` e `Contrato` obrigatorios.
- **RF-044** Estado vai para `Saiu`. Movimento finalizado.

### Cancelamento e desistencia
- **RF-050** Em qualquer estado != `Saiu`, usuario com papel `Porteiro+` pode marcar movimento como `Cancelado` (cancelamento operacional) ou `Desistencia` (motorista desistiu).
- **RF-051** Observacao obrigatoria no cancelamento/desistencia.

### Anexos
- **RF-060** Em cada estagio (chegada, entrada/confirmacao, saida), usuario pode anexar 0..N arquivos (foto ou PDF).
- **RF-061** Cada anexo registra estagio, usuario, timestamp.
- **RF-062** Tamanho maximo por arquivo: 10MB. Formatos aceitos: jpg, jpeg, png, pdf.

### Cadastros de apoio
- **RF-070** Admin gerencia: unidades, portarias, usuarios (com papeis), motoristas (com status: Ativo/Bloqueado/Pendente), transportadoras, veiculos.
- **RF-071** Bloqueio/desbloqueio de motorista exige motivo (texto livre obrigatorio).

### Auditoria e edicao
- **RF-080** Toda mudanca de estado de um movimento gera `EventoFluxo` imutavel.
- **RF-081** Toda edicao de campo de movimento ja registrado gera `EventoFluxo: EdicaoCampo` com diff (antes/depois).
- **RF-082** Edicao de campos criticos (placa carreta, motorista, motivo) apos estado `NoPateoInterno` exige usuario com papel `Lider+`.
- **RF-083** Lista de eventos do movimento e visivel em tela de detalhe.

### Multi-portaria e multi-tenant
- **RF-090** Toda consulta filtra por `UnidadeId` do usuario. Usuario nao ve dados de outras unidades.
- **RF-091** Painel de chamada agrega veiculos de todas as portarias da unidade do lider.

## 2.2 Requisitos Nao-Funcionais (RNF)

### Performance e volume
- **RNF-001** Volume esperado MVP: ~50 movimentos/dia por unidade, ate 3 portarias, 2-3 porteiros simultaneos, ate 10 lideres no painel. Sistema deve responder cadastro de chegada em <1s P95.
- **RNF-002** Painel de chamada atualiza em tempo real (latencia <2s entre evento e UI dos lideres).

### Seguranca
- **RNF-010** Senhas armazenadas com hash forte (Identity padrao C#).
- **RNF-011** JWT para API; refresh token; expiracao 8h (ajustavel por papel).
- **RNF-012** Rate limit no login (5 tentativas/min por IP).
- **RNF-013** Headers de seguranca aplicados (HSTS, CSP, X-Content-Type-Options).

### LGPD e auditoria
- **RNF-020** Log de auditoria imutavel (`EventoFluxo`) para todo movimento.
- **RNF-021** Dados pessoais armazenados: nome, CPF e WhatsApp do motorista; nome e email do usuario. Justificativa de tratamento documentada (interesse legitimo de seguranca patrimonial).
- **RNF-022** Retencao indefinida (decisao do cliente). Excluir/anonimizar so via solicitacao formal do titular.

### Disponibilidade
- **RNF-030** Aceitavel 5min downtime para deploys.
- **RNF-031** Backup diario do PostgreSQL.

### Integracoes
- **RNF-040** WhatsApp via Evolution API. Configurado por unidade (cada unidade tem sua instancia/token).
- **RNF-041** Email via SMTP (provedor a confirmar na fase de arquitetura — provavelmente SendGrid ou SES).
- **RNF-042** Notificacao em tempo real via SignalR no proprio backend C#.

### Plataformas
- **RNF-050** Web responsivo (Next.js 15 + Tailwind + shadcn/ui). Otimizado para desktop (porteiros e lideres) e tablet (lideres em chao de fabrica).
- **RNF-051** Mobile (Flutter) previsto para anexos de fotos e visualizacao do motorista — fora do MVP.

### Internacionalizacao
- **RNF-060** Idioma do dominio: PT-BR (nomes, mensagens, UI). Sem multi-idioma no MVP.

### Observabilidade
- **RNF-070** Serilog estruturado JSON.
- **RNF-071** Health checks `/health`, `/ready`, `/live`.
- **RNF-072** Metricas de fila de notificacoes pendentes (alarme se > 50 pendentes).
