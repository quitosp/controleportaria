# Blueprint C# / API — padrão Portaria

Stack travada: .NET 9, EF Core 9 + Npgsql (PostgreSQL), MediatR 12, FluentValidation 11, NetDevPack JWT 5, Newtonsoft 13, Swashbuckle 6.

## Camadas (4 pastas raiz)

```
{Solucao}/
├── compartilhados/
│   ├── core/Core/Core.csproj                  # base sem ASP.NET
│   └── webApi.core/WebApi.Core/WebApi.Core.csproj  # depende de Core, base controller, JWT, claims
├── dominios/Dominios/Dominios.csproj          # depende de Core
├── repositorios/Repositorios/Repositorios.csproj  # depende de Core, WebApi.Core, Dominios
├── servicos/api/Api/Api.csproj                # WebApi: depende de todos
└── {Solucao}.sln
```

Dependências (sentido único, sem ciclo):
- Core → ninguém
- WebApi.Core → Core
- Dominios → Core
- Repositorios → Core, WebApi.Core, Dominios
- Api → Core, WebApi.Core, Dominios, Repositorios

## Core — conteúdo fixo (não recriar, copiar)

```
Core/
├── Communication/ResponseResult.cs
├── Data/IRepository.cs                IRepository<T>: Salvar, Alterar, Existe(Guid)
├── Data/IUnitOfWork.cs                IUnitOfWork: Task<bool> Commit()
├── Enuns/                             enums com prefixo E (EFormaPagamento)
├── Exeptions/ApiException.cs          (sic Exeptions)
├── Mediator/IMediatorHandler.cs       EnviarComando, PublicarEvento, Enviar
├── Mediator/MediatorHandler.cs
├── Mensagens/Message.cs
├── Mensagens/CommandHandler.cs        base abstrata: AdicionarErro, PossuiErros, Erros, PersistirDados
├── Mensagens/Event.cs
├── Mensagens/Integrations/{IntegrationEvent,ResponseMessage}.cs
├── ObjetoDominio/Entity.cs            base entity, Id Guid, DataCadastro, Status, eventos
├── ObjetoDominio/IAggregateRoot.cs
├── ObjetoDominio/Comand.cs            base command IRequest<ComandResult>, EhValido()
├── ObjetoDominio/ComandResult.cs      Success, Message, Data, Code
├── ObjetoDominio/IComandResult.cs
├── ObjetoDominio/PagedResult.cs       List<T>, TotalResults, PageIndex, PageSize, Query
└── Util/DataBrasilia.cs               HorarioBrasilia()
```

## Padrão por Agregado (CQRS-lite, repete idêntico)

Para cada agregado novo (ex: Veiculo), criar exatamente 9 arquivos:

### 1. dominios/Dominios/{Plural}/Entidades/{Singular}.cs
```csharp
using Core.ObjetoDominio;
namespace Dominios.{Plural}.Entidades;

public class {Singular} : Entity
{
    public {Singular}(string nome /*...campos...*/)
    {
        Nome = nome;
    }
    protected {Singular}() { }

    public string Nome { get; private set; }
    // demais propriedades com private set

    public void Alterar(string nome /*...*/)
    {
        Nome = nome;
    }
}
```

### 2. dominios/Dominios/{Plural}/Comandos/Entradas/Salvar{Singular}Entrada.cs
```csharp
using Core.ObjetoDominio;
using FluentValidation;
namespace Dominios.{Plural}.Comandos.Entradas;

public class Salvar{Singular}Entrada : Comand
{
    public string Nome { get; set; }

    public override bool EhValido()
    {
        ValidationResult = new Salvar{Singular}Validation().Validate(this);
        return ValidationResult.IsValid;
    }

    public class Salvar{Singular}Validation : AbstractValidator<Salvar{Singular}Entrada>
    {
        public Salvar{Singular}Validation()
        {
            RuleFor(l => l.Nome).NotEmpty().WithMessage("O nome é obrigatório");
        }
    }
}
```

### 3. dominios/Dominios/{Plural}/Comandos/Entradas/Alterar{Singular}Entrada.cs
Igual ao Salvar mas com `public Guid {Singular}Id { get; set; }` adicional. Validação inclui `RuleFor(l => l.{Singular}Id).NotEqual(Guid.Empty)`.

### 4. dominios/Dominios/{Plural}/Comandos/Saidas/{Singular}Saida.cs
```csharp
namespace Dominios.{Plural}.Comandos.Saidas;
public class {Singular}Saida
{
    public Guid {Singular}Id { get; set; }
    public string Nome { get; set; }
}
```

### 5. dominios/Dominios/{Plural}/Comandos/Handlers/{Singular}CommandHandler.cs
```csharp
using Core.Mensagens;
using Core.ObjetoDominio;
using Dominios.{Plural}.Comandos.Entradas;
using Dominios.{Plural}.Entidades;
using Dominios.{Plural}.IRepositorios;
using MediatR;
namespace Dominios.{Plural}.Comandos.Handlers;

public class {Singular}CommandHandler : CommandHandler,
    IRequestHandler<Salvar{Singular}Entrada, ComandResult>,
    IRequestHandler<Alterar{Singular}Entrada, ComandResult>
{
    private readonly I{Singular}Repositorio _repositorio;

    public {Singular}CommandHandler(I{Singular}Repositorio repositorio) => _repositorio = repositorio;

    public async Task<ComandResult> Handle(Salvar{Singular}Entrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatórios faltando", Erros(msg.ValidationResult), 400);

        var entidade = new {Singular}(msg.Nome);
        _repositorio.Salvar(entidade);
        return await PersistirDados(_repositorio.UnitOfWork, "{Singular} salvo com sucesso!", new List<string>());
    }

    public async Task<ComandResult> Handle(Alterar{Singular}Entrada msg, CancellationToken ct)
    {
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatórios faltando", Erros(msg.ValidationResult), 400);

        var existe = await _repositorio.Existe(msg.{Singular}Id);
        if (existe is null) AdicionarErro("{Singular} não encontrado");
        if (PossuiErros()) return new ComandResult(false, "Alerta", Erros());

        existe!.Alterar(msg.Nome);
        _repositorio.Alterar(existe);
        return await PersistirDados(_repositorio.UnitOfWork, "{Singular} alterado com sucesso!", new List<string>());
    }
}
```

### 6. dominios/Dominios/{Plural}/IRepositorios/I{Singular}Repositorio.cs
```csharp
using Core.Data;
using Core.ObjetoDominio;
using Dominios.{Plural}.Comandos.Saidas;
using Dominios.{Plural}.Entidades;
namespace Dominios.{Plural}.IRepositorios;

public interface I{Singular}Repositorio : IRepository<{Singular}>
{
    {Singular} Salvar({Singular} entidade);
    void Alterar({Singular} entidade);
    Task<{Singular}?> Existe(Guid id);
    Task<PagedResult<{Singular}Saida>> Listar(int pageIndex, int pageSize, string? filter = null);
}
```

### 7. repositorios/Repositorios/Mapeamentos/{Singular}Maps.cs
```csharp
using Dominios.{Plural}.Entidades;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
namespace Repositorios.Mapeamentos;

public class {Singular}Maps : IEntityTypeConfiguration<{Singular}>
{
    public void Configure(EntityTypeBuilder<{Singular}> builder)
    {
        builder.HasKey(l => l.Id);
        builder.Property(l => l.Id).ValueGeneratedOnAdd().HasColumnName("{Singular}Id");
        builder.Property(l => l.Nome).IsRequired(true).HasColumnType("varchar(200)");
    }
}
```

### 8. repositorios/Repositorios/Repositorio/{Singular}Repositorio.cs
```csharp
using Core.Data;
using Core.ObjetoDominio;
using Dominios.{Plural}.Comandos.Saidas;
using Dominios.{Plural}.Entidades;
using Dominios.{Plural}.IRepositorios;
using Microsoft.EntityFrameworkCore;
using Repositorios.Contexto;
namespace Repositorios.Repositorio;

public class {Singular}Repositorio : I{Singular}Repositorio
{
    private readonly ContextoDB _context;
    public {Singular}Repositorio(ContextoDB context) => _context = context;
    public IUnitOfWork UnitOfWork => _context;

    public {Singular} Salvar({Singular} entidade)
    {
        _context.ChangeTracker.Clear();
        return _context.{Plural}.Add(entidade).Entity;
    }

    public void Alterar({Singular} entidade)
    {
        _context.ChangeTracker.Clear();
        _context.{Plural}.Update(entidade);
    }

    public async Task<{Singular}?> Existe(Guid id) =>
        await _context.{Plural}.FirstOrDefaultAsync(l => l.Id == id);

    public async Task<PagedResult<{Singular}Saida>> Listar(int pageIndex, int pageSize, string? filter = null)
    {
        var query = _context.{Plural}.AsQueryable();
        if (!string.IsNullOrEmpty(filter))
            query = query.Where(c => c.Nome.Contains(filter));
        var total = await query.CountAsync();
        var lista = await query
            .Skip((pageIndex - 1) * pageSize).Take(pageSize)
            .Select(l => new {Singular}Saida { {Singular}Id = l.Id, Nome = l.Nome })
            .ToListAsync();
        return new PagedResult<{Singular}Saida>
        {
            List = lista, PageIndex = pageIndex, PageSize = pageSize,
            TotalResults = total, Query = filter
        };
    }

    public void Dispose() => _context.Dispose();
}
```

### Regras de Controller (thin / sem logica)
- Apenas roteamento. Nao tem `try/catch` — o `ExceptionMiddleware` (registrado via `app.UseTratamentoErros()`) traduz `ValidationException`, `ApiException`/`DominioException`/`NaoAutorizadoException`/`NaoEncontradoException` para HTTP + `ComandResult`.
- Validacao SEMPRE no Comando (`Comand.EhValido()` + `AbstractValidator<T>` no mesmo arquivo da Entrada).
- Validacoes de negocio (ex: saldo insuficiente, recurso nao encontrado) lancam `DominioException`/`NaoEncontradoException` no Handler ou Service. Nao retornar `ComandResult` de erro manualmente — lance a exception.
- Validacoes de auth/integracao (HMAC, ApiKey, etc) viram `IAsyncActionFilter` separado (`[ValidarXAttribute]`), nao codigo no controller.
- Body parsing/headers: aceitar como parametros do action ou empacotar num `Comand` com `Validacao` no proprio arquivo.

### 9. servicos/api/Api/Controllers/{Singular}Controller.cs
```csharp
using Core.Mediator;
using Core.ObjetoDominio;
using Dominios.{Plural}.Comandos.Entradas;
using Dominios.{Plural}.Comandos.Saidas;
using Dominios.{Plural}.IRepositorios;
using Microsoft.AspNetCore.Mvc;
using WebApi.Core.Controller;
namespace Api.Controllers;

[Route("api/[controller]")]
public class {Singular}Controller : MainController
{
    private readonly IMediatorHandler _mediator;
    private readonly I{Singular}Repositorio _repositorio;

    public {Singular}Controller(IMediatorHandler mediator, I{Singular}Repositorio repositorio)
    {
        _mediator = mediator;
        _repositorio = repositorio;
    }

    [HttpPost("v1/salvar")]
    public async Task<IComandResult> Salvar(Salvar{Singular}Entrada cmd) => await _mediator.EnviarComando(cmd);

    [HttpPut("v1/alterar")]
    public async Task<IComandResult> Alterar(Alterar{Singular}Entrada cmd) => await _mediator.EnviarComando(cmd);

    [HttpGet("v1/listar/{pageIndex:int}/{pageSize:int}/{filter?}")]
    public async Task<PagedResult<{Singular}Saida>> Listar(int pageIndex, int pageSize, string? filter = null)
        => await _repositorio.Listar(pageIndex, pageSize, filter);
}
```

## Atualizações obrigatórias após criar agregado

### ContextoDB (repositorios/Repositorios/Contexto/ContextoDB.cs)
- Adicionar `public DbSet<{Singular}> {Plural} { get; set; }`
- Adicionar `modelBuilder.ApplyConfiguration(new {Singular}Maps());` em `OnModelCreating`

### DependencyInjectionConfig (servicos/api/Api/Configuration/DependencyInjectionConfig.cs)
- `services.AddScoped<IRequestHandler<Salvar{Singular}Entrada, ComandResult>, {Singular}CommandHandler>();`
- `services.AddScoped<IRequestHandler<Alterar{Singular}Entrada, ComandResult>, {Singular}CommandHandler>();`
- `services.AddScoped<I{Singular}Repositorio, {Singular}Repositorio>();`

### Migração
`dotnet ef migrations add v{n} --project repositorios/Repositorios --startup-project servicos/api/Api`

## Convenções inegociáveis

| Tipo | Padrão |
|------|--------|
| Idioma domínio | PT-BR sempre |
| Pasta plural | `Empresas`, `Veiculos`, `Portarias` |
| Entidade | Singular PascalCase |
| Comando entrada | `{Acao}{Entidade}Entrada` (Salvar, Alterar, Excluir) |
| Comando saída/DTO | `{Entidade}Saida` |
| Handler | `{Entidade}CommandHandler` |
| Repositório iface | `I{Entidade}Repositorio` (sem "rio" final, é "Repositorio") |
| Maps | `{Entidade}Maps` |
| Construtor sem args | `protected` (necessário p/ EF) |
| Setter | `private set` em entidades |
| Métodos async | sem sufixo "Async", retorno `Task<T>` |
| Métodos comuns | Salvar, Alterar, Existe, Listar, Obter |
| Validação | FluentValidation embutida no Comando |
| ID | `Guid`, gerado em `Entity` base |
| Mensagens erro | PT-BR, friendly |
| String column | `varchar(200)` default |
| DeleteBehavior | `ClientSetNull` (sem cascade) |
| Tracking | `NoTracking` global, `ChangeTracker.Clear()` antes Add/Update |

## Configurações fixas no Startup.cs

```csharp
services.AddIdentityConfiguration(Configuration);
services.AddApiConfiguration(Configuration);
services.AddJwtConfiguration(Configuration);
services.AddSwaggerConfiguration();
var handlers = AppDomain.CurrentDomain.Load("Dominios");
services.AddMediatR(cfg => cfg.RegisterServicesFromAssemblies(handlers));
services.RegisterServices();
```

## Configuração Postgres (Npgsql)

Pacote: `Npgsql.EntityFrameworkCore.PostgreSQL` 9.0.x no projeto Repositorios.

```csharp
// Repositorios/Contexto/ContextoDB.cs — provider
services.AddDbContext<ContextoDB>(options =>
    options.UseNpgsql(configuration.GetConnectionString("DefaultConnection")));
```

Connection string padrão (`appsettings.json`):
```json
"ConnectionStrings": {
  "DefaultConnection": "Host=localhost;Port=5432;Database={nome};Username=postgres;Password=postgres"
}
```

Notas Postgres:
- Tipos: `varchar(200)`, `text`, `timestamptz` (default para DateTime)
- Identidade: `Guid` em `uuid` (Postgres tem tipo nativo). EF Core mapeia automaticamente.
- Naming convention: por padrão Npgsql preserva PascalCase. Se quiser snake_case, adicionar `EFCore.NamingConventions` e `.UseSnakeCaseNamingConvention()`. Default: manter PascalCase para compatibilidade visual com C#.
- Migration: `dotnet ef migrations add v{n} --project repositorios/Repositorios --startup-project servicos/api/Api`
- Não usar `nvarchar` (não existe no Postgres)
- Não usar `IDENTITY` — EF Core gerencia Guid via `ValueGeneratedOnAdd`

## Resposta padrão API (sempre ComandResult)
```json
{ "success": true, "message": "Empresa salva com sucesso!", "data": [], "code": 400 }
```

## Pesquisa rápida — onde fica o quê
- **Lógica de negócio** → `dominios/Dominios/{Plural}/Comandos/Handlers/`
- **Persistência** → `repositorios/Repositorios/Repositorio/`
- **HTTP routes** → `servicos/api/Api/Controllers/`
- **DI registry** → `servicos/api/Api/Configuration/DependencyInjectionConfig.cs`
- **DbContext** → `repositorios/Repositorios/Contexto/ContextoDB.cs`
- **Validação** → classe aninhada dentro do `{Acao}{Entidade}Entrada`
