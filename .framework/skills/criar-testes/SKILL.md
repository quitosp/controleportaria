---
name: criar-testes
description: Cria testes para um agregado ou feature. Smoke tests pragmaticos, nao TDD completo. Triggers: "/testar HIST-NNN", "/testar Empresa", "criar testes", "smoke test do agregado X".
---

# Skill: criar-testes

## Entrada
- Nome do agregado ou ID da historia
- `nucleo/{stack}.md` (blueprint da stack)
- `nucleo/testes.md` (blueprint de testes)

## Acao por stack

### C# (xUnit + Microsoft.AspNetCore.Mvc.Testing)
1. Criar projeto de testes se nao existe: `testes/Api.Testes/Api.Testes.csproj`
   - Pacotes: xUnit 2.9, Microsoft.AspNetCore.Mvc.Testing 9, FluentAssertions 6, Testcontainers.PostgreSql 4
2. Para cada agregado:
   - `testes/Api.Testes/{Agregado}/{Agregado}HandlerTests.cs` — testa CommandHandler com repositorio fake (in-memory ou mock)
   - `testes/Api.Testes/{Agregado}/{Agregado}ControllerIntegrationTests.cs` — chama endpoint via WebApplicationFactory + Testcontainers Postgres
3. Cobrir: caso feliz salvar, caso feliz listar, validacao falha, ID inexistente em alterar.

### Frontend (Vitest + Testing Library)
1. Criar `vitest.config.ts` se nao existe.
2. Para cada feature:
   - `src/funcionalidades/{feature}/{Componente}.test.tsx` — render basico, interacoes principais
   - Mock de `api.ts` via vi.mock

### Python (pytest + httpx)
1. Criar `testes/test_{agregado}.py` com client TestClient + fixture de DB postgres via testcontainers-python.

## Saida
- Arquivos de teste criados
- Comando para rodar:
  - C#: `dotnet test`
  - Frontend: `npm test`
  - Python: `pytest`
- Reportar % de cobertura se ferramenta disponivel

## Restricoes
- NAO criar testes longos com muitos casos — 4-6 cenarios por handler basta
- NAO mockar profundamente — preferir integration test com banco real (testcontainers)
- NAO usar mocks que duplicam logica de producao
- SEMPRE usar arrange/act/assert claro
- Se TestContainers nao disponivel localmente (Docker off), reportar e usar in-memory provider EF Core como fallback
- NAO criar testes para getters/setters triviais
