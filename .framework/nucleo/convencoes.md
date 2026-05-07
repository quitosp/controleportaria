# Convenções globais

## Idioma
- **Domínio sempre PT-BR**: nomes de classes, pastas, métodos de negócio, mensagens
- **Keywords técnicas em inglês**: `async`, `await`, `class`, `interface`, `using`, `import`
- **Mensagens de erro/sucesso PT-BR amigáveis**: "Empresa salva com sucesso!"

## Mapeamento por stack

| Conceito Portaria C# | Frontend TS | Python FastAPI |
|---|---|---|
| `Empresa` (entity) | `Empresa` (interface/zod) | `Empresa` (class) |
| `SalvarEmpresaEntrada` | `salvarEmpresaSchema` | `SalvarEmpresaEntrada` (Pydantic) |
| `EmpresaSaida` (DTO) | `Empresa` (camelCase) | `EmpresaSaida` |
| `EmpresaCommandHandler` | n/a (mutation) | `EmpresaHandler` |
| `IEmpresaRepositorio` | `funcionalidades/empresas/api.ts` | `IEmpresaRepositorio` |
| `EmpresaController` | rota `app/(privado)/empresas/` | `empresa_controlador.py` |
| `ComandResult` | `{success, message, data, code}` | `ComandResult` Pydantic |
| `PagedResult<T>` | `ResultadoPaginado<T>` | `PagedResult[T]` |

## Regras de escrita Claude Code

### Token economy
- **NUNCA** ler arquivo sem checar `estado/index.json` primeiro
- **NUNCA** explicar código com comentários — nomes claros bastam
- **NUNCA** repetir conteúdo já visto na conversa
- **SEMPRE** usar `Edit` em vez de `Write` para modificar arquivo existente
- **SEMPRE** que possível, usar scripts (`scripts/csharp_scaffold.py`) em vez de gerar texto repetitivo

### Comentários
- Zero comentários em código de domínio (Entity, Handler, Repositório, Controller)
- Zero comentários explicando "o quê"
- Permitido apenas: workaround com motivo, invariante não óbvia
- Docstrings/XML-doc só em métodos públicos de Core/utilitários, e curtos

### Respostas ao usuário
- Tersas, sem narrativa. Update por etapa quando longa.
- Sem "vou fazer X agora" — fazer e reportar resultado
- Sem resumos finais quando o diff já fala
- Sem emojis salvo pedido explícito

### Nomes
- Singular para entidade, plural para pasta/coleção/DbSet
- `I` prefixo em interfaces
- Nomes em PT-BR para domínio mesmo em projetos em inglês

## Endpoints API padrão

Cada agregado expõe:
- `POST /api/{recurso}/v1/salvar` → cria
- `PUT /api/{recurso}/v1/alterar` → atualiza
- `GET /api/{recurso}/v1/listar/{pageIndex}/{pageSize}/{filter?}` → lista paginada
- `GET /api/{recurso}/v1/obter/{id}` → busca por id (quando necessário)
- `DELETE /api/{recurso}/v1/excluir/{id}` → remove (quando necessário)

Resposta sempre `ComandResult` para writes, `PagedResult<T>` ou DTO direto para reads.

## Banco de dados
- PostgreSQL para todas stacks (provider: Npgsql para C#, asyncpg/psycopg para Python, pg para Node)
- Strings: `varchar(200)` default
- DateTime: `timestamptz` (Postgres) — sempre UTC ou Brasília explicito
- IDs: `Guid`/`uuid`
- Sem cascade delete (`ClientSetNull` no EF Core)
- Migrações sempre nomeadas: `v1`, `v2`, `v3` ou descritivas curtas
- Soft delete via campo `Status` (bool) na `Entity` base, não `IsDeleted`
- Connection string padrão: `Host=localhost;Port=5432;Database={nome};Username=postgres;Password=postgres`

## Autenticação
- JWT Bearer com refresh token
- Identity (C#) ou JWT custom (Python)
- Claims: userId, email, roles
- Endpoint público: anotação explícita
- Default: protegido
