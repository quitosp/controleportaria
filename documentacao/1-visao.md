# 1. Visao do Sistema

## 1.1 Contexto

A Frigoestrela opera um frigorifico com fluxo intenso de veiculos diariamente (~50 caminhoes/dia, 2-3 porteiros simultaneos, mais de uma portaria fisica). O sistema atual de "Cadastro de Chegada" e essencialmente um formulario de coleta de dados: nao identifica o porteiro logado, nao distingue portarias, nao bloqueia motoristas com pendencia, nao gerencia fila do patio externo, e a chamada de veiculos do patio externo para o interno ocorre por radio/telefone — informalmente, sem rastro.

## 1.2 Problema

O processo atual gera tres dores principais:

1. **Falta de rastreabilidade**: o campo "Funcionario" e selecionado manualmente; qualquer um pode escolher qualquer nome, e nao ha distincao entre portarias.
2. **Falta de controle de fluxo**: lideres da industria precisam ligar para a portaria para liberar veiculos do patio externo. Nao ha visao em tempo real de quem esta esperando, nem registro formal de quem autorizou cada entrada.
3. **Saida nao padronizada**: hoje o porteiro registra saida com os mesmos campos para qualquer motivo. Carga de exportacao (container) e descarga simples sao tratadas iguais — perdem-se dados criticos como lacre, contrato, destino.

## 1.3 Proposta de valor

Um sistema de **gerenciamento de fluxo logistico de portaria** que:

- Identifica cada acao por usuario autenticado, portaria fisica e timestamp.
- Diferencia o fluxo conforme o destino (patio interno, externo, lavador) e o motivo (carga, descarga, exportacao).
- Permite que lideres da industria, de qualquer terminal, autorizem entrada de veiculos via painel em tempo real, com notificacao automatica ao motorista (WhatsApp + Email) e a portaria (websocket).
- Bloqueia ou alerta sobre motoristas com pendencia, registrando a decisao do porteiro.
- Suporta anexos de fotos em todos os estagios (chegada, entrada, saida) para auditoria.
- Cumpre auditoria LGPD: toda mudanca de estado e edicao gera evento imutavel, retencao indefinida.

## 1.4 Escopo do MVP

**Inclui**:
- Login de usuario com papeis (porteiro, lider, supervisor, admin).
- Multi-portaria (uma instalacao Frigoestrela com N portarias).
- Cadastro de chegada com auto-fill por placa.
- Cadastro centralizado de motoristas, transportadoras, veiculos.
- Bloqueio/alerta de motorista com decisao registrada.
- Painel de veiculos no patio externo para lideres.
- "Chamar veiculo" com WhatsApp, Email, SignalR.
- Saida condicional por motivo (descarga / carga / container exportacao).
- Anexos de fotos em chegada, entrada, saida.
- Cancelamento e desistencia em qualquer estado pre-saida.
- Auditoria completa via EventoFluxo.

**Fora do MVP** (planejado para fases seguintes):
- Aplicativo mobile do motorista para upload direto de fotos.
- Multi-tenant real (varias unidades Frigoestrela ou outros frigorificos) — modelo ja preparado, ativacao posterior.
- Agendamento previo de chegadas.
- Integracao com sistemas internos de logistica/ERP.
- Painel de SLA / metricas operacionais.

## 1.5 Restricoes e premissas

- Stack: C# .NET 9 (API) + Next.js 15 (web) + PostgreSQL. Mobile futuro em Flutter.
- WhatsApp via Evolution API.
- Email via SMTP/SendGrid (a confirmar na arquitetura).
- Notificacao em tempo real via SignalR (mesmo stack).
- Idioma do dominio: PT-BR.
- Auditoria/LGPD: retencao indefinida, log imutavel.
