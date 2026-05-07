# 3. Personas e Atores

## 3.1 Porteiro

**Quem**: Funcionario da Frigoestrela alocado fisicamente em uma das portarias.
**Frequencia de uso**: Diaria, jornada de 8h. E o usuario mais intensivo do sistema.
**Objetivos**:
- Cadastrar chegada de veiculo de forma rapida e precisa.
- Confirmar entrada de veiculos ja chamados pelos lideres.
- Registrar saida de veiculo com os campos certos (carga vs descarga vs exportacao).
- Tirar duvida sobre situacao de motorista (bloqueado? pendente?).

**Dores hoje**:
- Digita os mesmos dados de placa/transportadora repetidas vezes (sem auto-fill).
- Recebe ligacoes constantes de lideres pedindo liberacao do patio externo.
- Nao tem clareza de quem autorizou cada entrada quando questionado depois.
- Erra na saida quando motivo era container exportacao mas registra como carga normal.

**Permissoes**:
- Cadastrar chegada, entrada, saida, anexos.
- Cadastrar motorista, transportadora, veiculo "no fluxo" (durante chegada).
- Cancelar/desistir movimento ate `NoPateoInterno`.
- Editar campos nao-criticos do movimento.

## 3.2 Lider

**Quem**: Lider de equipe da industria (carga, descarga, expedicao). Trabalha dentro do galpao, acessa o sistema de tablet/desktop.
**Frequencia de uso**: Varias vezes ao dia, em momentos pontuais.
**Objetivos**:
- Ver quais veiculos estao no patio externo aguardando liberacao.
- Liberar a entrada de um veiculo direto pelo sistema, sem precisar ligar para a portaria.
- Receber notificacao quando seu setor tem veiculo esperando.

**Dores hoje**:
- Para liberar um veiculo, liga para a portaria, espera porteiro atender, da o numero da placa, espera a confirmacao.
- Nao tem nenhuma visibilidade do que esta no patio externo se nao ligar.
- Quando trocou de turno, nao sabe quais veiculos estavam la.

**Permissoes**:
- Tudo do porteiro.
- Painel de chamada: visualizar todos veiculos `NoPateoExterno` da unidade.
- Acionar "Autorizar entrada" (chamar veiculo).
- Recancelar chamada apos TTL expirado.
- Editar campos criticos de movimento ja em estado `NoPateoInterno`+.

## 3.3 Supervisor

**Quem**: Supervisor de operacao. Responsavel por mais de uma equipe de lideres.
**Frequencia de uso**: Esporadica, em casos de excecao ou para revisao.
**Objetivos**:
- Investigar movimentos com problema (cancelamentos, desistencias, alertas de bloqueio de motorista).
- Acompanhar SLA do dia (futuro).
- Liberar excecoes (motorista bloqueado, edicao retroativa).

**Dores hoje**:
- Sem auditoria, depende de relato verbal do porteiro/lider.
- Nao consegue cruzar facilmente "qual transportadora trouxe X veiculos no mes".

**Permissoes**:
- Tudo do lider.
- Visualizar `EventoFluxo` completo (auditoria) de qualquer movimento.
- Editar dados retroativamente com auditoria.

## 3.4 Administrador

**Quem**: TI/gerencia. Responsavel pela configuracao do sistema.
**Frequencia de uso**: Semanal ou em mudancas estruturais.
**Objetivos**:
- Cadastrar e gerenciar usuarios, papeis, portarias, unidades.
- Bloquear/desbloquear motoristas com base em decisoes administrativas.
- Configurar integracoes (WhatsApp Evolution API por unidade, SMTP).
- Configurar parametros (TTL de chamada, tamanho max de anexo).

**Permissoes**:
- Tudo do supervisor.
- Cadastros de apoio: unidades, portarias, usuarios (com papeis), motoristas (status).
- Configuracoes de sistema.

## 3.5 Motorista (ator externo)

**Quem**: Motorista de caminhao que chega na portaria. Nao tem login no sistema MVP.
**Como interage**:
- Recebe WhatsApp e/ou email quando lider o "chama" do patio externo.
- Apresenta documento ao porteiro na chegada e na saida.

**Futuro (fora MVP)**:
- App mobile para receber notificacoes oficiais e enviar fotos.

## 3.6 Mapa de papeis x permissoes

| Funcionalidade | Porteiro | Lider | Supervisor | Admin |
|----------------|----------|-------|------------|-------|
| Login                                   | ok | ok | ok | ok |
| Cadastrar chegada                       | ok | ok | ok | ok |
| Confirmar entrada                       | ok | ok | ok | ok |
| Registrar saida                         | ok | ok | ok | ok |
| Cancelar/Desistencia                    | ok | ok | ok | ok |
| Painel de chamada (ver patio externo)   | -  | ok | ok | ok |
| Chamar veiculo                          | -  | ok | ok | ok |
| Recancelar chamada expirada             | -  | ok | ok | ok |
| Cadastrar motorista/transportadora/veic | ok | ok | ok | ok |
| Bloquear/desbloquear motorista          | -  | -  | ok | ok |
| Editar campos criticos pos-entrada      | -  | ok | ok | ok |
| Ver auditoria completa (EventoFluxo)    | -  | -  | ok | ok |
| Cadastrar usuarios                      | -  | -  | -  | ok |
| Cadastrar portarias/unidades            | -  | -  | -  | ok |
| Configurar integracoes                  | -  | -  | -  | ok |
