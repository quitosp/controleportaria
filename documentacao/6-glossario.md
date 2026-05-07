# 6. Glossario (Linguagem Ubiqua)

Termos e definicoes que devem aparecer literalmente no codigo, no banco e na UI.

| Termo | Definicao |
|-------|-----------|
| **Unidade** | Instalacao da Frigoestrela. E o tenant. No futuro pode haver mais de uma. |
| **Portaria** | Acesso fisico controlado de uma Unidade. Uma Unidade pode ter N portarias. |
| **MovimentoPortaria** | Ciclo de vida de um veiculo na unidade — da chegada ate a saida (ou cancelamento/desistencia). E o agregado raiz do dominio. |
| **Chegada** | Momento em que o porteiro registra um veiculo entrando no perimetro da unidade (patio externo, interno ou lavador). |
| **Saida** | Momento em que o veiculo deixa a unidade. Os campos exigidos variam pelo motivo da entrada. |
| **Carga** | Motivo de entrada: o veiculo vem buscar produto. Saida exige NF, lacre, destino. |
| **Descarga** | Motivo de entrada: o veiculo vem entregar produto. Saida exige apenas timestamp. |
| **Devolucao** | Motivo de entrada: produto sendo retornado. Tratada como Descarga simplificada. |
| **Container Exportacao** | Subcategoria de Carga onde TipoCarga=Container. Saida exige adicionalmente numero de container e contrato. |
| **Patio Interno** | Area dentro do galpao da industria onde o veiculo estaciona para carga/descarga. |
| **Patio Externo** | Area fora do galpao onde o veiculo aguarda autorizacao para entrar no patio interno. |
| **Lavador** | Area dedicada a higienizacao do veiculo, exigida para certas operacoes. |
| **Chamar Veiculo** | Acao do lider que autoriza o veiculo a sair do patio externo e entrar no patio interno. Dispara WhatsApp ao motorista, email ao motorista e notificacao SignalR a portaria de origem. |
| **Chamada Expirada** | Quando o lider chamou o veiculo mas o motorista nao se apresentou em 30 minutos (TTL configuravel). Lider pode recancelar ou rechamar. |
| **Cancelamento** | Encerramento operacional do movimento (ex: motorista saiu sem completar a operacao por motivo administrativo). Estado terminal. |
| **Desistencia** | Encerramento iniciado pelo motorista (motorista desistiu antes de completar). Estado terminal. |
| **Motorista Bloqueado** | Status que sinaliza pendencia administrativa (documentacao, restricao). Nao impede a chegada — apenas alerta o porteiro, que decide e registra a decisao. |
| **Autorizado por (chegada)** | Texto livre informado pelo porteiro quando o destino e patio interno: nome de quem autorizou via radio/telefone (substituido por sistema quando o lider usa o painel). |
| **Lider** | Usuario interno da industria responsavel por chamar veiculos para o patio interno. Trabalha no galpao. |
| **Porteiro** | Usuario fisicamente lotado na portaria, responsavel por registrar chegadas, entradas e saidas. |
| **EventoFluxo** | Registro imutavel de uma mudanca de estado ou edicao em um movimento. Base da auditoria. |
| **Anexo** | Arquivo (foto ou PDF) vinculado a um estagio (chegada, entrada, saida) de um movimento. |
| **NotificacaoPendente** | Side-effect a ser entregue (WhatsApp, email, SignalR) que pode ser retentado em caso de falha sem bloquear o fluxo. |
| **TTL de Chamada** | Tempo maximo (default 30min) que um movimento permanece em `ChamadoParaInterno` sem confirmacao de entrada. |
| **Auto-fill por placa** | Funcionalidade que sugere transportadora e tipo de carga com base no ultimo movimento daquela placa de carreta. |
| **Carreta** | Veiculo de tipo `Carreta` (placa principal — obrigatoria no movimento). |
| **Cavalo** | Veiculo de tipo `Cavalo` (placa do cavalo mecanico — opcional). |
| **Carreta Segunda** | Veiculo de tipo `CarretaSegunda` (segunda carreta para bitrem/rodotrem — opcional). |
| **Setor** | Departamento de destino interno (ex: armazem, frigorifico, expedicao). |
| **Lacre** | Numero do lacre aplicado a carga na saida — obrigatorio em saida de Carga. |
| **Evolution API** | Provedor de WhatsApp escolhido para integracao. Configurado por Unidade. |
| **SignalR** | Tecnologia de notificacao em tempo real (websocket) usada para atualizar o painel de chamada e a portaria de origem instantaneamente. |
