# Contrato HIST-002 — RBAC com policies hierarquicas

## Papel hierarquico
```
Admin > Supervisor > Lider > Porteiro
```
Cada papel "OuMaior" significa: o proprio + todos acima.

## Policies (registradas em `Configuration/AuthorizationConfig.cs`)

| Policy | Aceita papeis | Uso tipico |
|--------|---------------|------------|
| `PorteiroOuMaior` | Porteiro, Lider, Supervisor, Admin | Cadastro/edicao de chegada/entrada/saida; cadastros de apoio em-linha |
| `LiderOuMaior` | Lider, Supervisor, Admin | Painel de chamada, chamar veiculo, recancelar chamada, edicao critica de movimento |
| `SupervisorOuMaior` | Supervisor, Admin | Alterar status de motorista, ver auditoria completa |
| `SomenteAdmin` | Admin | Cadastros de usuario, portaria, unidade, configuracoes de integracao |

## Claims do JWT
Apos login, JWT carrega:
- `sub` — id do usuario (Identity)
- `name` — nome do usuario
- `email` — email
- `papel` — `Porteiro|Lider|Supervisor|Admin`
- `unidadeId` — guid da unidade
- `portariaPadraoId` — guid da portaria padrao (pode ser null para admin)

## Mapping endpoints x policy

| Endpoint | Policy |
|----------|--------|
| `POST /api/auth/v1/entrar` | publico |
| `POST /api/auth/v1/refresh` | publico |
| `POST /api/auth/v1/registrar` | `SomenteAdmin` |
| `POST /api/auth/v1/trocar-senha` | autenticado (qualquer papel) |
| `GET  /api/movimentos/v1/listar/...` | `PorteiroOuMaior` |
| `POST /api/movimentos/v1/cadastrar-chegada` | `PorteiroOuMaior` |
| `POST /api/movimentos/v1/{id}/confirmar-entrada` | `PorteiroOuMaior` |
| `POST /api/movimentos/v1/{id}/registrar-saida` | `PorteiroOuMaior` |
| `POST /api/movimentos/v1/{id}/cancelar` | `PorteiroOuMaior` |
| `POST /api/movimentos/v1/{id}/desistir` | `PorteiroOuMaior` |
| `POST /api/movimentos/v1/anexar` | `PorteiroOuMaior` |
| `PUT  /api/movimentos/v1/{id}` (edicao) | dinamico — `PorteiroOuMaior` para campos comuns; campos criticos pos-NoPateoInterno exigem `LiderOuMaior` (RN-021) |
| `GET  /api/painel-chamada/v1/listar` | `LiderOuMaior` |
| `POST /api/movimentos/v1/{id}/chamar` | `LiderOuMaior` |
| `POST /api/movimentos/v1/{id}/recancelar-chamada` | `LiderOuMaior` |
| `GET  /api/movimentos/v1/{id}/eventos` | `SupervisorOuMaior` |
| `PUT  /api/motoristas/v1/{id}/status` | `SupervisorOuMaior` |
| `POST /api/usuarios/v1/cadastrar` | `SomenteAdmin` |
| `POST /api/portarias/v1/cadastrar` | `SomenteAdmin` |
| `POST /api/unidades/v1/cadastrar` | `SomenteAdmin` |

## Erros
- Sem JWT valido → 401
- JWT valido mas papel insuficiente → 403
- Tentativa de acesso a recurso de outra `UnidadeId` → 404 (filtro global do DbContext nem retorna resultado)

## Regras de negocio cobertas
- **RN-001** — toda operacao exige usuario autenticado (atributo `[Authorize]` herdado)
- **RN-014** — multi-tenant via claim `unidadeId` consumida pelo `IUnidadeContext`
- **RN-021** — edicao critica pos-NoPateoInterno exige `LiderOuMaior`

## Artefatos a criar/editar
- `api/servicos/api/Api/Configuration/AuthorizationConfig.cs` (novo) — registra policies
- `api/servicos/api/Api/Startup.cs` — `services.AddAuthorizationConfig()` antes de Build
- `api/servicos/api/Api/Controllers/AuthController.cs` — adicionar claims (papel, unidadeId, portariaPadraoId) no token
- `api/compartilhados/webApi.core/WebApi.Core/Multitenant/IUnidadeContext.cs` (novo)
- `api/compartilhados/webApi.core/WebApi.Core/Multitenant/UnidadeContextHttp.cs` (novo)
- `api/servicos/api/Api/Configuration/DependencyInjectionConfig.cs` — registrar `IUnidadeContext`
- Constantes `PoliticasAuth.cs` em `Core/ObjetoDominio/`

## Aceite
1. Build OK; pos_implementacao OK
2. Tentativa de chamar `/api/usuarios/v1/cadastrar` sem ser admin retorna 403
3. JWT contem claims `papel`, `unidadeId`, `portariaPadraoId`
4. `IUnidadeContext.UnidadeId` e injetavel e retorna o valor da claim
