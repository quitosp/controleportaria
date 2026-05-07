#!/usr/bin/env python3
"""Scaffold de agregado C# no padrao Portaria. Cria os 9 arquivos canonicos
e atualiza ContextoDB e DependencyInjectionConfig.

Uso:
  python .framework/scripts/csharp_scaffold.py <Singular> [opcoes]

Opcoes:
  --plural <Plural>           default: Singular + 's'
  --raiz <path>               raiz do projeto C#
  --sem-patch                 nao mexer em ContextoDB/DI
  --campos "nome:tipo[:flags...],..."   campos custom alem de Nome
                              tipos: string|int|long|decimal|bool|guid|datetime
                              flags: obrigatorio (default), opcional, max=N, min=N, unico

Campos com flag `unico` ganham metodo ObterPor{Campo} e checagem de duplicidade
no handler. O campo Nome sempre tem checagem de duplicidade (sem flag necessaria).

Exemplos:
  python .framework/scripts/csharp_scaffold.py Veiculo
  python .framework/scripts/csharp_scaffold.py Empresa --campos "cnpj:string:obrigatorio:max=14:unico,telefone:string:opcional,ativo:bool"
  python .framework/scripts/csharp_scaffold.py Pedido --campos "valor:decimal:obrigatorio,clienteId:guid:obrigatorio,observacao:string:opcional"
"""
from __future__ import annotations
import argparse, re, sys
from dataclasses import dataclass
from pathlib import Path

TIPOS_CS = {
    "string": "string", "int": "int", "long": "long",
    "decimal": "decimal", "bool": "bool",
    "guid": "Guid", "datetime": "DateTime",
}

@dataclass
class Campo:
    nome: str                     # camelCase, ex: cnpj
    tipo_cs: str                  # ex: string, Guid, decimal
    obrigatorio: bool = True
    max_len: int | None = None
    min_len: int | None = None
    nullable: bool = False        # para tipo de valor opcional vira "tipo?"
    unico: bool = False           # gera ObterPor{Campo} + checagem de duplicidade

    @property
    def nome_pascal(self) -> str:
        return self.nome[0].upper() + self.nome[1:]

    @property
    def tipo_decl(self) -> str:
        # string default "" para nao-null; int? long? quando opcional valor
        if self.tipo_cs == "string":
            return "string" if self.obrigatorio else "string?"
        if self.nullable:
            return self.tipo_cs + "?"
        return self.tipo_cs

    @property
    def default_inicial(self) -> str:
        if self.tipo_cs == "string": return "" if not self.obrigatorio else "string.Empty"
        return ""

def parse_campos(spec: str) -> list[Campo]:
    """Parse 'nome:tipo[:flags...]' separado por virgula."""
    if not spec: return []
    campos = []
    for raw in spec.split(","):
        raw = raw.strip()
        if not raw: continue
        partes = raw.split(":")
        if len(partes) < 2:
            print(f"ERRO campo invalido (precisa nome:tipo): {raw}"); sys.exit(2)
        nome, tipo = partes[0], partes[1].lower()
        if tipo not in TIPOS_CS:
            print(f"ERRO tipo invalido '{tipo}'. Use: {','.join(TIPOS_CS)}"); sys.exit(2)
        c = Campo(nome=nome, tipo_cs=TIPOS_CS[tipo])
        for flag in partes[2:]:
            f = flag.strip().lower()
            if f == "obrigatorio": c.obrigatorio = True
            elif f == "opcional":
                c.obrigatorio = False
                if c.tipo_cs not in ("string",): c.nullable = True
            elif f == "unico": c.unico = True
            elif f.startswith("max="): c.max_len = int(f.split("=",1)[1])
            elif f.startswith("min="): c.min_len = int(f.split("=",1)[1])
            else: print(f"AVISO flag desconhecida '{flag}' em {nome}")
        campos.append(c)
    return campos

def gerar_entidade(singular: str, plural: str, campos: list[Campo], auditavel: bool = False) -> str:
    todos = [Campo("nome", "string")] + campos
    parametros = ", ".join(f"{c.tipo_decl} {c.nome}" for c in todos)
    atribuicoes = "\n        ".join(f"{c.nome_pascal} = {c.nome};" for c in todos)
    propriedades = "\n    ".join(f"public {c.tipo_decl} {c.nome_pascal} {{ get; private set; }}" + ("" if c.tipo_cs != "string" or not c.obrigatorio else "") + (f" = {c.default_inicial};" if c.tipo_cs == "string" and c.obrigatorio else "") for c in todos)
    base_class = "EntityAuditable" if auditavel else "Entity"
    return f"""using Core.ObjetoDominio;

namespace Dominios.{plural}.Entidades;

public class {singular} : {base_class}
{{
    public {singular}({parametros})
    {{
        {atribuicoes}
    }}

    protected {singular}() {{ }}

    {propriedades}

    public void Alterar({parametros})
    {{
        {atribuicoes}
    }}
}}
"""

def gerar_validation(campos: list[Campo], tipo_classe: str) -> str:
    rules = ['        RuleFor(l => l.Nome).NotEmpty().WithMessage("O nome e obrigatorio");']
    for c in campos:
        if not c.obrigatorio: continue
        if c.tipo_cs == "string":
            rule = f'        RuleFor(l => l.{c.nome_pascal}).NotEmpty().WithMessage("{c.nome_pascal} e obrigatorio");'
            if c.max_len: rule += f'\n        RuleFor(l => l.{c.nome_pascal}).MaximumLength({c.max_len});'
            if c.min_len: rule += f'\n        RuleFor(l => l.{c.nome_pascal}).MinimumLength({c.min_len});'
            rules.append(rule)
        elif c.tipo_cs == "Guid":
            rules.append(f'        RuleFor(l => l.{c.nome_pascal}).NotEqual(Guid.Empty).WithMessage("{c.nome_pascal} e obrigatorio");')
        elif c.tipo_cs in ("int","long","decimal"):
            rules.append(f'        RuleFor(l => l.{c.nome_pascal}).GreaterThan(0).WithMessage("{c.nome_pascal} deve ser maior que zero");')
    return "\n".join(rules)

def gerar_props_dto(campos: list[Campo], inclui_id: bool = False) -> str:
    linhas = []
    if inclui_id:
        linhas.append(f"    public Guid Id {{ get; set; }}")
    todos = [Campo("nome", "string")] + campos
    for c in todos:
        default = ' = string.Empty;' if c.tipo_cs == "string" and c.obrigatorio else ''
        linhas.append(f"    public {c.tipo_decl} {c.nome_pascal} {{ get; set; }}{default}")
    return "\n".join(linhas)

def gerar_salvar_entrada(singular: str, plural: str, campos: list[Campo]) -> str:
    props = gerar_props_dto(campos)
    rules = gerar_validation(campos, "Salvar")
    return f"""using Core.ObjetoDominio;
using FluentValidation;

namespace Dominios.{plural}.Comandos.Entradas;

public class Salvar{singular}Entrada : Comand
{{
{props}

    public override bool EhValido()
    {{
        ValidationResult = new Salvar{singular}Validation().Validate(this);
        return ValidationResult.IsValid;
    }}

    public class Salvar{singular}Validation : AbstractValidator<Salvar{singular}Entrada>
    {{
        public Salvar{singular}Validation()
        {{
{rules}
        }}
    }}
}}
"""

def gerar_alterar_entrada(singular: str, plural: str, campos: list[Campo]) -> str:
    props = f"    public Guid {singular}Id {{ get; set; }}\n" + gerar_props_dto(campos)
    rules_id = f'        RuleFor(l => l.{singular}Id).NotEqual(Guid.Empty).WithMessage("Id invalido");'
    rules = rules_id + "\n" + gerar_validation(campos, "Alterar")
    return f"""using Core.ObjetoDominio;
using FluentValidation;

namespace Dominios.{plural}.Comandos.Entradas;

public class Alterar{singular}Entrada : Comand
{{
{props}

    public override bool EhValido()
    {{
        ValidationResult = new Alterar{singular}Validation().Validate(this);
        return ValidationResult.IsValid;
    }}

    public class Alterar{singular}Validation : AbstractValidator<Alterar{singular}Entrada>
    {{
        public Alterar{singular}Validation()
        {{
{rules}
        }}
    }}
}}
"""

def gerar_saida(singular: str, plural: str, campos: list[Campo]) -> str:
    todos = [Campo("nome","string")] + campos
    linhas = [f"    public Guid {singular}Id {{ get; set; }}"]
    for c in todos:
        default = ' = string.Empty;' if c.tipo_cs == "string" and c.obrigatorio else ''
        linhas.append(f"    public {c.tipo_decl} {c.nome_pascal} {{ get; set; }}{default}")
    return f"""namespace Dominios.{plural}.Comandos.Saidas;

public class {singular}Saida
{{
{chr(10).join(linhas)}
}}
"""

def campos_unicos(singular: str, campos: list[Campo]) -> list[Campo]:
    """Lista campos que devem ter checagem de duplicidade. Nome sempre entra, demais com flag unico."""
    nome_default = Campo("nome", "string")
    nome_default.unico = True  # marca para checagem
    return [nome_default] + [c for c in campos if c.unico]

def gerar_handler(singular: str, plural: str, campos: list[Campo]) -> str:
    todos = [Campo("nome","string")] + campos
    args_msg = ", ".join(f"msg.{c.nome_pascal}" for c in todos)
    unicos = campos_unicos(singular, campos)

    # checagens duplicidade no Salvar
    checks_salvar = []
    for c in unicos:
        checks_salvar.append(
            f"        if (await _repositorio.ObterPor{c.nome_pascal}(msg.{c.nome_pascal}) is not null)\n"
            f'            AdicionarErro("Ja existe {singular} com este {c.nome_pascal}");'
        )
    bloco_check_salvar = "\n".join(checks_salvar)

    # checagens duplicidade no Alterar (excluindo proprio id)
    checks_alterar = []
    for c in unicos:
        checks_alterar.append(
            f"        if (await _repositorio.ObterPor{c.nome_pascal}(msg.{c.nome_pascal}, msg.{singular}Id) is not null)\n"
            f'            AdicionarErro("Ja existe outro {singular} com este {c.nome_pascal}");'
        )
    bloco_check_alterar = "\n".join(checks_alterar)

    return f"""using Core.Mensagens;
using Core.ObjetoDominio;
using Dominios.{plural}.Comandos.Entradas;
using Dominios.{plural}.Entidades;
using Dominios.{plural}.IRepositorios;
using MediatR;

namespace Dominios.{plural}.Comandos.Handlers;

public class {singular}CommandHandler : CommandHandler,
    IRequestHandler<Salvar{singular}Entrada, ComandResult>,
    IRequestHandler<Alterar{singular}Entrada, ComandResult>
{{
    private readonly I{singular}Repositorio _repositorio;

    public {singular}CommandHandler(I{singular}Repositorio repositorio) => _repositorio = repositorio;

    public async Task<ComandResult> Handle(Salvar{singular}Entrada msg, CancellationToken ct)
    {{
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

{bloco_check_salvar}
        if (PossuiErros()) return new ComandResult(false, "Conflito", Erros(), 409);

        var entidade = new {singular}({args_msg});
        _repositorio.Salvar(entidade);
        return await PersistirDados(_repositorio.UnitOfWork, "{singular} salvo com sucesso!", new {{ id = entidade.Id }});
    }}

    public async Task<ComandResult> Handle(Alterar{singular}Entrada msg, CancellationToken ct)
    {{
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        var existe = await _repositorio.Existe(msg.{singular}Id);
        if (existe is null) AdicionarErro("{singular} nao encontrado");
        if (PossuiErros()) return new ComandResult(false, "Alerta", Erros(), 404);

{bloco_check_alterar}
        if (PossuiErros()) return new ComandResult(false, "Conflito", Erros(), 409);

        existe!.Alterar({args_msg});
        _repositorio.Alterar(existe);
        return await PersistirDados(_repositorio.UnitOfWork, "{singular} alterado com sucesso!", new {{ id = existe.Id }});
    }}
}}
"""

def gerar_irepo(singular: str, plural: str, campos: list[Campo]) -> str:
    unicos = campos_unicos(singular, campos)
    metodos_obter = "\n".join(
        f"    Task<{singular}?> ObterPor{c.nome_pascal}({c.tipo_decl} valor, Guid? excluirId = null);"
        for c in unicos
    )
    return f"""using Core.Data;
using Core.ObjetoDominio;
using Dominios.{plural}.Comandos.Saidas;
using Dominios.{plural}.Entidades;

namespace Dominios.{plural}.IRepositorios;

public interface I{singular}Repositorio : IRepository<{singular}>
{{
    {singular} Salvar({singular} entidade);
    void Alterar({singular} entidade);
    Task<{singular}?> Existe(Guid id);
{metodos_obter}
    Task<PagedResult<{singular}Saida>> Listar(int pageIndex, int pageSize, string? filter = null);
}}
"""

def gerar_maps(singular: str, plural: str, campos: list[Campo]) -> str:
    todos = [Campo("nome","string")] + campos
    linhas = []
    for c in todos:
        propriedade = f"        builder.Property(l => l.{c.nome_pascal})"
        if c.obrigatorio: propriedade += ".IsRequired(true)"
        if c.tipo_cs == "string":
            tamanho = c.max_len or 200
            propriedade += f'.HasColumnType("varchar({tamanho})")'
        propriedade += ";"
        linhas.append(propriedade)
    return f"""using Dominios.{plural}.Entidades;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Repositorios.Mapeamentos;

public class {singular}Maps : IEntityTypeConfiguration<{singular}>
{{
    public void Configure(EntityTypeBuilder<{singular}> builder)
    {{
        builder.HasKey(l => l.Id);
        builder.Property(l => l.Id).ValueGeneratedOnAdd().HasColumnName("{singular}Id");
{chr(10).join(linhas)}
    }}
}}
"""

def gerar_repositorio(singular: str, plural: str, campos: list[Campo]) -> str:
    todos = [Campo("nome","string")] + campos
    select = ", ".join([f"{singular}Id = l.Id"] + [f"{c.nome_pascal} = l.{c.nome_pascal}" for c in todos])
    unicos = campos_unicos(singular, campos)
    impl_obter = "\n".join(
        f"    public async Task<{singular}?> ObterPor{c.nome_pascal}({c.tipo_decl} valor, Guid? excluirId = null)\n"
        f"    {{\n"
        f"        var query = _context.{plural}.AsQueryable();\n"
        f"        if (excluirId.HasValue) query = query.Where(l => l.Id != excluirId.Value);\n"
        f"        return await query.FirstOrDefaultAsync(l => l.{c.nome_pascal} == valor);\n"
        f"    }}\n"
        for c in unicos
    )
    return f"""using Core.Data;
using Core.ObjetoDominio;
using Dominios.{plural}.Comandos.Saidas;
using Dominios.{plural}.Entidades;
using Dominios.{plural}.IRepositorios;
using Microsoft.EntityFrameworkCore;
using Repositorios.Contexto;

namespace Repositorios.Repositorio;

public class {singular}Repositorio : I{singular}Repositorio
{{
    private readonly ContextoDB _context;

    public {singular}Repositorio(ContextoDB context) => _context = context;

    public IUnitOfWork UnitOfWork => _context;

    public {singular} Salvar({singular} entidade)
    {{
        _context.ChangeTracker.Clear();
        return _context.{plural}.Add(entidade).Entity;
    }}

    public void Alterar({singular} entidade)
    {{
        _context.ChangeTracker.Clear();
        _context.{plural}.Update(entidade);
    }}

    public async Task<{singular}?> Existe(Guid id) =>
        await _context.{plural}.FirstOrDefaultAsync(l => l.Id == id);

{impl_obter}
    public async Task<PagedResult<{singular}Saida>> Listar(int pageIndex, int pageSize, string? filter = null)
    {{
        var query = _context.{plural}.AsQueryable();
        if (!string.IsNullOrEmpty(filter))
            query = query.Where(c => c.Nome.Contains(filter));
        var total = await query.CountAsync();
        var lista = await query
            .Skip((pageIndex - 1) * pageSize).Take(pageSize)
            .Select(l => new {singular}Saida {{ {select} }})
            .ToListAsync();
        return new PagedResult<{singular}Saida>
        {{
            List = lista, PageIndex = pageIndex, PageSize = pageSize,
            TotalResults = total, Query = filter
        }};
    }}

    public void Dispose() => _context.Dispose();
}}
"""

def gerar_teste_handler(singular: str, plural: str, campos: list[Campo]) -> str:
    todos = [Campo("nome","string")] + campos
    nome_arg = ", ".join(f'"{c.nome.capitalize()}"' if c.tipo_cs == "string" else (
        "Guid.NewGuid()" if c.tipo_cs == "Guid" else (
        "1" if c.tipo_cs in ("int","long","decimal") else "true")) for c in todos)
    primeiro_obrig = next((c for c in todos if c.obrigatorio), None)
    campo_invalido = f"{primeiro_obrig.nome_pascal} = " + ('""' if primeiro_obrig and primeiro_obrig.tipo_cs == "string" else "Guid.Empty") if primeiro_obrig else 'Nome = ""'
    return f"""using Dominios.{plural}.Comandos.Entradas;
using Dominios.{plural}.Comandos.Handlers;
using Dominios.{plural}.IRepositorios;
using FluentAssertions;
using Moq;
using Xunit;

namespace Api.Testes.{plural};

public class {singular}HandlerTests
{{
    private readonly Mock<I{singular}Repositorio> _repositorio = new();
    private readonly {singular}CommandHandler _handler;

    public {singular}HandlerTests()
    {{
        _repositorio.Setup(r => r.UnitOfWork.Commit()).ReturnsAsync(true);
        _handler = new {singular}CommandHandler(_repositorio.Object);
    }}

    [Fact]
    public async Task Salvar_ComDadosValidos_RetornaSucesso()
    {{
        var cmd = new Salvar{singular}Entrada {{ Nome = "Teste"{', ' + ', '.join(f'{c.nome_pascal} = ' + ('"' + c.nome.capitalize() + '"' if c.tipo_cs == "string" else 'Guid.NewGuid()' if c.tipo_cs == "Guid" else '1' if c.tipo_cs in ("int","long","decimal") else 'true') for c in campos if c.obrigatorio) if any(c.obrigatorio for c in campos) else ''} }};

        var result = await _handler.Handle(cmd, CancellationToken.None);

        result.Success.Should().BeTrue();
        _repositorio.Verify(r => r.Salvar(It.IsAny<Dominios.{plural}.Entidades.{singular}>()), Times.Once);
    }}

    [Fact]
    public async Task Salvar_ComNomeVazio_RetornaErro()
    {{
        var cmd = new Salvar{singular}Entrada {{ Nome = "" }};
        var result = await _handler.Handle(cmd, CancellationToken.None);
        result.Success.Should().BeFalse();
        result.Code.Should().Be(400);
    }}

    [Fact]
    public async Task Alterar_ComIdInexistente_RetornaErro()
    {{
        _repositorio.Setup(r => r.Existe(It.IsAny<Guid>())).ReturnsAsync((Dominios.{plural}.Entidades.{singular}?)null);
        var cmd = new Alterar{singular}Entrada {{ {singular}Id = Guid.NewGuid(), Nome = "X" }};
        var result = await _handler.Handle(cmd, CancellationToken.None);
        result.Success.Should().BeFalse();
        result.Code.Should().Be(404);
    }}
}}
"""

def gerar_controller(singular: str, plural: str) -> str:
    return f"""using Core.Mediator;
using Core.ObjetoDominio;
using Dominios.{plural}.Comandos.Entradas;
using Dominios.{plural}.Comandos.Saidas;
using Dominios.{plural}.IRepositorios;
using Microsoft.AspNetCore.Mvc;
using WebApi.Core.Controller;

namespace Api.Controllers;

[Route("api/[controller]")]
public class {singular}Controller : MainController
{{
    private readonly IMediatorHandler _mediator;
    private readonly I{singular}Repositorio _repositorio;

    public {singular}Controller(IMediatorHandler mediator, I{singular}Repositorio repositorio)
    {{
        _mediator = mediator;
        _repositorio = repositorio;
    }}

    [HttpPost("v1/salvar")]
    public async Task<IComandResult> Salvar(Salvar{singular}Entrada cmd) => await _mediator.EnviarComando(cmd);

    [HttpPut("v1/alterar")]
    public async Task<IComandResult> Alterar(Alterar{singular}Entrada cmd) => await _mediator.EnviarComando(cmd);

    [HttpGet("v1/listar/{{pageIndex:int}}/{{pageSize:int}}")]
    public async Task<PagedResult<{singular}Saida>> Listar(int pageIndex, int pageSize, [FromQuery] string? filter = null)
        => await _repositorio.Listar(pageIndex, pageSize, filter);
}}
"""

def patch_contexto(raiz: Path, singular: str, plural: str) -> bool:
    p = raiz / "repositorios/Repositorios/Contexto/ContextoDB.cs"
    if not p.exists():
        print(f"  AVISO: ContextoDB.cs nao encontrado, pule patch manual"); return False
    txt = p.read_text(encoding="utf-8")
    if f"DbSet<{singular}>" in txt:
        print(f"  ContextoDB ja contem DbSet<{singular}>"); return False

    dbset_line = f"    public DbSet<{singular}> {plural} {{ get; set; }}"
    using_line = f"using Dominios.{plural}.Entidades;"
    using_maps = "using Repositorios.Mapeamentos;"

    if using_line not in txt:
        txt = re.sub(r"(using [^\n]+\n)(?!using )", r"\1" + using_line + "\n", txt, count=1)

    if "public DbSet<" in txt:
        txt = re.sub(r"(public DbSet<[^\n]+\n)", r"\1" + dbset_line + "\n", txt, count=1)
    else:
        txt = re.sub(r"(public class ContextoDB[^\n]+\n\{\n)", r"\1" + dbset_line + "\n\n", txt, count=1)

    if using_maps not in txt:
        txt = re.sub(r"(using [^\n]+\n)(?!using )", r"\1" + using_maps + "\n", txt, count=1)

    apply = f"        modelBuilder.ApplyConfiguration(new {singular}Maps());"
    if apply not in txt:
        if "ApplyConfigurationsFromAssembly" in txt:
            txt = re.sub(r"(modelBuilder\.ApplyConfigurationsFromAssembly[^\n]+\n)", r"\1" + apply + "\n", txt, count=1)
        else:
            txt = re.sub(r"(\n\s+base\.OnModelCreating\(modelBuilder\);)", "\n" + apply + r"\1", txt, count=1)

    p.write_text(txt, encoding="utf-8")
    print(f"  ContextoDB atualizado")
    return True

def patch_di(raiz: Path, singular: str, plural: str) -> bool:
    p = raiz / "servicos/api/Api/Configuration/DependencyInjectionConfig.cs"
    if not p.exists():
        print(f"  AVISO: DI nao encontrado, pule patch manual"); return False
    txt = p.read_text(encoding="utf-8")
    if f"I{singular}Repositorio, {singular}Repositorio" in txt:
        print(f"  DI ja contem {singular}"); return False

    usings = [
        f"using Dominios.{plural}.Comandos.Entradas;",
        f"using Dominios.{plural}.Comandos.Handlers;",
        f"using Dominios.{plural}.IRepositorios;",
        f"using Repositorios.Repositorio;",
    ]
    for u in usings:
        if u not in txt:
            txt = re.sub(r"(using [^\n]+\n)(?!using )", r"\1" + u + "\n", txt, count=1)

    bloco = (
        f"        services.AddScoped<IRequestHandler<Salvar{singular}Entrada, ComandResult>, {singular}CommandHandler>();\n"
        f"        services.AddScoped<IRequestHandler<Alterar{singular}Entrada, ComandResult>, {singular}CommandHandler>();\n"
        f"        services.AddScoped<I{singular}Repositorio, {singular}Repositorio>();\n"
    )
    txt = re.sub(r"(public static void RegisterServices[^{]*\{\n)", r"\1" + bloco, txt, count=1)
    p.write_text(txt, encoding="utf-8")
    print(f"  DI atualizado")
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("singular")
    ap.add_argument("--plural", default=None)
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--sem-patch", action="store_true")
    ap.add_argument("--campos", default="")
    ap.add_argument("--migrate", action="store_true", help="apos scaffold: roda migrations add v{N} + database update")
    ap.add_argument("--reindexar", action="store_true", help="apos scaffold: roda indexar.py")
    ap.add_argument("--tudo", action="store_true", help="atalho: --migrate + --reindexar")
    ap.add_argument("--forcar", action="store_true", help="sobrescreve handler/controller/repositorio/irepositorio (preserva entidade/entradas/saidas/maps)")
    ap.add_argument("--auditavel", action="store_true", help="entidade herda EntityAuditable (CriadoPor/AlteradoPor)")
    ap.add_argument("--com-testes", action="store_true", help="gera tambem projeto de testes xUnit com handler tests")
    args = ap.parse_args()
    if args.tudo: args.migrate = args.reindexar = True

    REGENERAVEIS = {"handler", "controller", "irepo", "repo"}  # arquivos que --forcar sobrescreve

    singular = args.singular
    plural = args.plural or (singular + "s")
    raiz = Path(args.raiz).resolve()
    campos = parse_campos(args.campos)

    geradores = [
        ("entidade", f"dominios/Dominios/{plural}/Entidades/{singular}.cs", lambda: gerar_entidade(singular, plural, campos, args.auditavel)),
        ("entrada_salvar", f"dominios/Dominios/{plural}/Comandos/Entradas/Salvar{singular}Entrada.cs", lambda: gerar_salvar_entrada(singular, plural, campos)),
        ("entrada_alterar", f"dominios/Dominios/{plural}/Comandos/Entradas/Alterar{singular}Entrada.cs", lambda: gerar_alterar_entrada(singular, plural, campos)),
        ("saida", f"dominios/Dominios/{plural}/Comandos/Saidas/{singular}Saida.cs", lambda: gerar_saida(singular, plural, campos)),
        ("handler", f"dominios/Dominios/{plural}/Comandos/Handlers/{singular}CommandHandler.cs", lambda: gerar_handler(singular, plural, campos)),
        ("irepo", f"dominios/Dominios/{plural}/IRepositorios/I{singular}Repositorio.cs", lambda: gerar_irepo(singular, plural, campos)),
        ("maps", f"repositorios/Repositorios/Mapeamentos/{singular}Maps.cs", lambda: gerar_maps(singular, plural, campos)),
        ("repo", f"repositorios/Repositorios/Repositorio/{singular}Repositorio.cs", lambda: gerar_repositorio(singular, plural, campos)),
        ("controller", f"servicos/api/Api/Controllers/{singular}Controller.cs", lambda: gerar_controller(singular, plural)),
    ]

    criados, existentes, regenerados = [], [], []
    for tipo, rel, fn in geradores:
        alvo = raiz / rel
        if alvo.exists():
            if args.forcar and tipo in REGENERAVEIS:
                alvo.write_text(fn(), encoding="utf-8")
                regenerados.append(rel); continue
            existentes.append(rel); continue
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(fn(), encoding="utf-8")
        criados.append(rel)

    print(f"Agregado {singular} (plural: {plural}, campos extras: {len(campos)}):")
    for c in criados: print(f"  + {c}")
    for r in regenerados: print(f"  ~ {r} (regenerado)")
    for e in existentes: print(f"  = {e} (ja existia)")
    if not args.sem_patch:
        patch_contexto(raiz, singular, plural)
        patch_di(raiz, singular, plural)
    print(f"Total: {len(criados)} criados, {len(regenerados)} regenerados, {len(existentes)} preservados")

    if args.com_testes:
        teste_dir = raiz / f"testes/Api.Testes/{plural}"
        teste_dir.mkdir(parents=True, exist_ok=True)
        teste_file = teste_dir / f"{singular}HandlerTests.cs"
        if not teste_file.exists():
            teste_file.write_text(gerar_teste_handler(singular, plural, campos), encoding="utf-8")
            print(f"  + testes/Api.Testes/{plural}/{singular}HandlerTests.cs")
        else:
            print(f"  = testes/Api.Testes/{plural}/{singular}HandlerTests.cs (ja existe)")
        # garante csproj de testes existe
        csproj = raiz / "testes/Api.Testes/Api.Testes.csproj"
        if not csproj.exists():
            csproj.parent.mkdir(parents=True, exist_ok=True)
            csproj.write_text("""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.11.1" />
    <PackageReference Include="xunit" Version="2.9.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.8.2" />
    <PackageReference Include="Moq" Version="4.20.72" />
    <PackageReference Include="FluentAssertions" Version="6.12.0" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\\..\\dominios\\Dominios\\Dominios.csproj" />
    <ProjectReference Include="..\\..\\compartilhados\\core\\Core\\Core.csproj" />
  </ItemGroup>
</Project>
""", encoding="utf-8")
            print(f"  + testes/Api.Testes/Api.Testes.csproj")

    if args.migrate:
        import subprocess as _sp
        scripts_dir = Path(__file__).parent
        print("\n-> Rodando migrate.py")
        rc = _sp.run([sys.executable, str(scripts_dir / "migrate.py"), "--raiz", str(raiz)]).returncode
        if rc != 0:
            print(f"AVISO: migrate falhou (rc={rc}). Resolva e rode: python .framework/scripts/migrate.py")

    # --tudo agora roda pos_implementacao (review + seguranca + reindex)
    if args.reindexar:
        import subprocess as _sp
        scripts_dir = Path(__file__).parent
        print("\n-> Rodando pos_implementacao.py (review + seguranca + reindex)")
        rc = _sp.run([sys.executable, str(scripts_dir / "pos_implementacao.py"),
                      "--raiz", str(raiz), "--stack", "csharp",
                      "--apenas", singular,
                      "--sem-bloqueio"]).returncode
        if rc != 0:
            print(f"AVISO: pos_implementacao reportou desvios. Veja saida acima.")

    if not args.migrate:
        print("\nProximo: python .framework/scripts/migrate.py    (ou passe --migrate / --tudo no scaffold)")

if __name__ == "__main__":
    main()
