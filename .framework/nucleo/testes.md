# Blueprint de testes

Filosofia: smoke tests pragmaticos. Cobrir caso feliz + 1-2 erros. Nao TDD purista.

## C# — xUnit + WebApplicationFactory + Testcontainers

### Estrutura
```
testes/
└── Api.Testes/
    ├── Api.Testes.csproj           # depende de Api, FluentAssertions, xunit, Mvc.Testing, Testcontainers.PostgreSql
    ├── Fixtures/
    │   ├── PostgresFixture.cs      # IAsyncLifetime, sobe container, expoe ConnectionString
    │   └── ApiWebFactory.cs        # WebApplicationFactory<Program> trocando ConnectionString
    └── {Agregado}/
        ├── {Agregado}HandlerTests.cs        # unitario com EF InMemory ou mock
        └── {Agregado}ControllerTests.cs     # integration com Postgres real
```

### Padrao Handler test (unitario)
```csharp
public class EmpresaHandlerTests
{
    private readonly ContextoDB _ctx;
    private readonly EmpresaRepositorio _repo;
    private readonly EmpresaCommandHandler _handler;

    public EmpresaHandlerTests()
    {
        var opt = new DbContextOptionsBuilder<ContextoDB>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString()).Options;
        var mediator = Mock.Of<IMediatorHandler>();
        _ctx = new ContextoDB(opt, mediator);
        _repo = new EmpresaRepositorio(_ctx);
        _handler = new EmpresaCommandHandler(_repo);
    }

    [Fact]
    public async Task Salvar_ComNomeValido_RetornaSucesso()
    {
        var cmd = new SalvarEmpresaEntrada { Nome = "ACME" };
        var result = await _handler.Handle(cmd, CancellationToken.None);
        result.Success.Should().BeTrue();
    }

    [Fact]
    public async Task Salvar_SemNome_RetornaErro()
    {
        var cmd = new SalvarEmpresaEntrada { Nome = "" };
        var result = await _handler.Handle(cmd, CancellationToken.None);
        result.Success.Should().BeFalse();
    }
}
```

### Padrao Controller integration test
```csharp
public class EmpresaControllerTests : IClassFixture<ApiWebFactory>
{
    private readonly HttpClient _client;
    public EmpresaControllerTests(ApiWebFactory f) => _client = f.CreateClient();

    [Fact]
    public async Task POST_Salvar_RetornaOk()
    {
        var resp = await _client.PostAsJsonAsync("/api/empresa/v1/salvar", new { Nome = "ACME" });
        resp.EnsureSuccessStatusCode();
        var body = await resp.Content.ReadFromJsonAsync<JsonElement>();
        body.GetProperty("success").GetBoolean().Should().BeTrue();
    }
}
```

## Frontend — Vitest + React Testing Library

### Estrutura
```
src/funcionalidades/{feature}/
├── api.ts
├── ganchos.ts
├── tipos.ts
├── pagina.tsx
├── componentes/Formulario{Singular}.tsx
└── __testes__/
    ├── api.test.ts                 # mock fetch, valida payload
    └── Formulario{Singular}.test.tsx  # render + submit
```

### Padrao
```ts
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { FormularioEmpresa } from "../componentes/FormularioEmpresa";
import { vi } from "vitest";

vi.mock("../api", () => ({ salvarEmpresa: vi.fn(() => Promise.resolve({ success: true })) }));

test("submete formulario com nome valido", async () => {
  const qc = new QueryClient();
  render(<QueryClientProvider client={qc}><FormularioEmpresa /></QueryClientProvider>);
  await userEvent.type(screen.getByLabelText(/nome/i), "ACME");
  await userEvent.click(screen.getByRole("button", { name: /salvar/i }));
  expect(await screen.findByText(/salvo com sucesso/i)).toBeInTheDocument();
});
```

## Python — pytest + httpx + testcontainers

```python
import pytest
from httpx import AsyncClient
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16") as pg:
        yield pg.get_connection_url()

@pytest.mark.asyncio
async def test_salvar_empresa(app_client: AsyncClient):
    r = await app_client.post("/api/empresa/v1/salvar", json={"nome": "ACME"})
    assert r.status_code == 200
    assert r.json()["success"] is True
```

## Cobertura minima por agregado
- 1 teste de salvar com sucesso
- 1 teste de salvar com validacao falha
- 1 teste de alterar inexistente (404)
- 1 teste de listar com paginacao

Total: ~4 testes por agregado. Para 8 agregados = 32 testes. Roda em <30s.

## Quando nao testar
- Getters/setters
- Mapeamentos EF (Maps.cs)
- Code generated (scaffolds)
- Fluxos com >3 mocks (sinal de design ruim, refatorar antes)
