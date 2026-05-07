# Mockup: {TITULO_HISTORIA}

**HIST**: HIST-NNN
**Tipo**: business-flow | report | crud (com UI customizada)
**Tela/Fluxo**: {nome_tela_ou_fluxo}

## Objetivo
{1 frase: o que esta tela faz}

## Wireframe ASCII

```
+----------------------------------------------------------+
| Cabecalho             [acoes]   [usuario]               |
+----------------------------------------------------------+
| Titulo da pagina                          [+ Novo X]    |
|                                                          |
| [filtro: ____________] [outro: ___] [Buscar]            |
|                                                          |
| +------+----------+----------+----------+--------+      |
| | Col1 | Col2     | Col3     | Col4     | Acoes  |      |
| +------+----------+----------+----------+--------+      |
| | dado | exemplo  | exemplo  | exemplo  | edit X |      |
| | dado | exemplo  | exemplo  | exemplo  | edit X |      |
| +------+----------+----------+----------+--------+      |
|                                                          |
| [< 1 2 3 ... >]                  Total: 47              |
+----------------------------------------------------------+
```

## Estados (4 obrigatorios)
- **Carregando**: skeleton de 5 linhas
- **Vazio**: "{mensagem amigavel}" + botao acao primaria
- **Erro**: toast vermelho com retry
- **Sucesso**: tabela populada, paginacao no rodape

## Acoes do usuario
| Gatilho | O que acontece |
|---------|----------------|
| Clique em [+ Novo X] | abre modal com formulario |
| Clique em [Editar] na linha | navega para /x/{id}/editar |
| Submit do form | POST /api/x/v1/salvar → toast sucesso → invalida lista |
| Erro de validacao | mostra erro abaixo do campo |

## Dados de exemplo (para mock)
```json
[
  { "id": "uuid-1", "campo1": "exemplo", "campo2": 100 },
  { "id": "uuid-2", "campo1": "outro",   "campo2": 250 }
]
```

## Endpoints consumidos
- `GET /api/x/v1/listar/{pageIndex}/{pageSize}?filter={busca}`
- `POST /api/x/v1/salvar`
- `PUT /api/x/v1/alterar`

## Aprovacao

- [ ] Layout aprovado pelo usuario
- [ ] Estados (carregando/vazio/erro/sucesso) cobertos
- [ ] Acoes mapeadas para endpoints existentes
- [ ] Responsivo (mobile descrito acima ou separado)

Quando todos checados: marcar `artefato.aprovado: true` no historia.yaml e prosseguir com `/impl HIST-NNN`.
