#!/usr/bin/env python3
"""Scaffold para capacidades NAO-CRUD em C# Portaria.
Gera esqueleto de business-flow, integration, report ou automation com DI registrado.
Deixa TODOs marcados onde a logica especifica precisa ser preenchida pelo dev/IA seguindo o contrato.

Uso:
  python .framework/scripts/csharp_scaffold_capacidade.py --tipo <T> --nome <Nome> [--agregado <Ag>] [--raiz <path>]

Tipos:
  business-flow  cria: Entrada + Handler + adiciona endpoint no Controller do agregado + DI
  integration    cria: Settings + Service/Importer + WebhookController endpoint + DI
  report         cria: Query + Saida + RelatorioController endpoint + DI
  automation     cria: Worker (IHostedService) + AddHostedService no DI

Exemplo:
  python .framework/scripts/csharp_scaffold_capacidade.py --tipo business-flow --nome TransferirEntreContas --agregado Movimento
  python .framework/scripts/csharp_scaffold_capacidade.py --tipo integration --nome Stripe
  python .framework/scripts/csharp_scaffold_capacidade.py --tipo report --nome SaldoMensal
  python .framework/scripts/csharp_scaffold_capacidade.py --tipo automation --nome LimpezaTokens
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

# ============================ TEMPLATES ============================

T_ENTRADA_BF = '''using Core.ObjetoDominio;
using FluentValidation;

namespace Dominios.{Plural}.Comandos.Entradas;

public class {Nome}Entrada : Comand
{{
    // TODO seguindo contrato: definir campos de entrada
    // public Guid AlgumId {{ get; set; }}
    // public decimal Valor {{ get; set; }}

    public override bool EhValido()
    {{
        ValidationResult = new {Nome}Validation().Validate(this);
        return ValidationResult.IsValid;
    }}

    public class {Nome}Validation : AbstractValidator<{Nome}Entrada>
    {{
        public {Nome}Validation()
        {{
            // TODO seguindo contrato: regras de validacao
            // RuleFor(l => l.AlgumId).NotEqual(Guid.Empty);
            // RuleFor(l => l.Valor).GreaterThan(0);
        }}
    }}
}}
'''

T_HANDLER_BF = '''using Core.Mensagens;
using Core.ObjetoDominio;
using Dominios.{Plural}.Comandos.Entradas;
using Dominios.{Plural}.Entidades;
using Dominios.{Plural}.IRepositorios;
using MediatR;

namespace Dominios.{Plural}.Comandos.Handlers;

public class {Nome}Handler : CommandHandler,
    IRequestHandler<{Nome}Entrada, ComandResult>
{{
    private readonly I{Singular}Repositorio _repositorio;
    // TODO: injetar outros repositorios necessarios pelo contrato

    public {Nome}Handler(I{Singular}Repositorio repositorio)
    {{
        _repositorio = repositorio;
    }}

    public async Task<ComandResult> Handle({Nome}Entrada msg, CancellationToken ct)
    {{
        if (!msg.EhValido())
            return new ComandResult(false, "Campos obrigatorios faltando", Erros(msg.ValidationResult), 400);

        // TODO seguindo contrato: implementar fluxo
        // 1. Buscar entidades necessarias (404 se nao existem)
        // 2. Aplicar regras de negocio (409 se conflito)
        // 3. Persistir mudancas
        // 4. Retornar saida com IDs/dados relevantes

        await Task.CompletedTask;
        return await PersistirDados(_repositorio.UnitOfWork, "{Nome} concluido", new {{ }});
    }}
}}
'''

T_SETTINGS_INT = '''namespace Api.Integracoes.{Nome};

public class {Nome}Settings
{{
    public string WebhookSecret {{ get; set; }} = "";
    public string BaseUrl {{ get; set; }} = "";
    // TODO: campos especificos do servico (api key, sandbox url, etc)
}}
'''

T_SERVICE_INT = '''using Microsoft.Extensions.Options;

namespace Api.Integracoes.{Nome};

public class {Nome}Service
{{
    private readonly {Nome}Settings _cfg;
    private readonly ILogger<{Nome}Service> _log;
    // TODO: injetar HttpClient (services.AddHttpClient<{Nome}Service>())
    // TODO: injetar repositorios afetados

    public {Nome}Service(IOptions<{Nome}Settings> cfg, ILogger<{Nome}Service> log)
    {{
        _cfg = cfg.Value;
        _log = log;
    }}

    public async Task<object> Processar(string payload)
    {{
        // TODO seguindo contrato:
        // 1. Validar payload (HMAC se webhook, schema se REST)
        // 2. Verificar idempotencia
        // 3. Parsear/transformar dados
        // 4. Persistir mudancas no dominio
        // 5. Retornar resultado

        _log.LogInformation("audit_{nome_lower} processando");
        await Task.CompletedTask;
        return new {{ ok = true }};
    }}
}}
'''

T_WEBHOOK_CTRL_INT = '''using System.Security.Cryptography;
using System.Text;
using Api.Integracoes.{Nome};
using Core.ObjetoDominio;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Options;
using WebApi.Core.Controller;

namespace Api.Controllers;

[Route("api/webhook")]
[AllowAnonymous]
public class {Nome}WebhookController : MainController
{{
    private readonly {Nome}Service _service;
    private readonly {Nome}Settings _cfg;

    public {Nome}WebhookController({Nome}Service service, IOptions<{Nome}Settings> cfg)
    {{
        _service = service;
        _cfg = cfg.Value;
    }}

    [HttpPost("v1/{nome_lower}")]
    public async Task<IActionResult> Receber([FromHeader(Name = "X-Signature")] string assinatura)
    {{
        Request.EnableBuffering();
        using var reader = new StreamReader(Request.Body, leaveOpen: true);
        var body = await reader.ReadToEndAsync();
        Request.Body.Position = 0;

        if (!ValidarHmac(body, assinatura, _cfg.WebhookSecret))
            return Unauthorized(new ComandResult(false, "Assinatura invalida", new List<string>(), 401));

        try
        {{
            var resultado = await _service.Processar(body);
            return Ok(new ComandResult(true, "Processado", resultado, 200));
        }}
        catch (Exception ex)
        {{
            return BadRequest(new ComandResult(false, "Erro", new List<string> {{ ex.Message }}, 400));
        }}
    }}

    private bool ValidarHmac(string payload, string assinatura, string segredo)
    {{
        if (string.IsNullOrEmpty(segredo) || string.IsNullOrEmpty(assinatura)) return false;
        using var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(segredo));
        var hash = Convert.ToHexString(hmac.ComputeHash(Encoding.UTF8.GetBytes(payload))).ToLowerInvariant();
        return assinatura.Trim().ToLowerInvariant() == hash;
    }}
}}
'''

T_QUERY_RPT = '''using Microsoft.EntityFrameworkCore;
using Repositorios.Contexto;

namespace Api.Relatorios;

public class {Nome}Query
{{
    private readonly ContextoDB _ctx;
    public {Nome}Query(ContextoDB ctx) => _ctx = ctx;

    public async Task<{Nome}Saida> Executar(/* TODO parametros: int ano, int mes, ... */)
    {{
        // TODO seguindo mockup:
        // 1. Consultar tabelas necessarias com .Where/.Sum/.GroupBy
        // 2. Agregar dados (totais, contadores, breakdowns)
        // 3. Mapear para {Nome}Saida

        await Task.CompletedTask;
        return new {Nome}Saida();
    }}
}}
'''

T_SAIDA_RPT = '''namespace Api.Relatorios;

public class {Nome}Saida
{{
    // TODO seguindo mockup: campos retornados
    // public decimal Total {{ get; set; }}
    // public List<...> Itens {{ get; set; }} = new();
}}
'''

T_RELATORIO_CTRL = '''using Api.Relatorios;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using WebApi.Core.Controller;

namespace Api.Controllers;

[Route("api/relatorio")]
[Authorize]
public partial class RelatorioController : MainController
{{
    // metodos sao adicionados via partial class por relatorio
}}
'''

T_RELATORIO_PARTIAL = '''using Api.Relatorios;
using Microsoft.AspNetCore.Mvc;

namespace Api.Controllers;

public partial class RelatorioController
{{
    private readonly {Nome}Query _{nomeLower}Query;

    public RelatorioController({Nome}Query {nomeLower}Query) => _{nomeLower}Query = {nomeLower}Query;

    [HttpGet("v1/{rota_lower}/{{/* TODO rota params */}}")]
    public async Task<{Nome}Saida> {Nome}(/* TODO params */)
        => await _{nomeLower}Query.Executar();
}}
'''

T_WORKER_AUTO = '''using Microsoft.Extensions.Hosting;

namespace Api.Workers;

public class {Nome}Worker : BackgroundService
{{
    private readonly IServiceProvider _sp;
    private readonly ILogger<{Nome}Worker> _log;
    // TODO: definir intervalo conforme contrato
    private readonly TimeSpan _intervalo = TimeSpan.FromHours(6);

    public {Nome}Worker(IServiceProvider sp, ILogger<{Nome}Worker> log)
    {{
        _sp = sp; _log = log;
    }}

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {{
        while (!stoppingToken.IsCancellationRequested)
        {{
            try
            {{
                using var scope = _sp.CreateScope();
                // TODO seguindo contrato: obter ContextoDB ou repositorios
                // var ctx = scope.ServiceProvider.GetRequiredService<ContextoDB>();
                // 1. Buscar items a processar
                // 2. Processar (com idempotencia)
                // 3. Persistir resultados

                _log.LogInformation("audit_{nome_lower} executado");
            }}
            catch (Exception ex)
            {{
                _log.LogError(ex, "Falha em {Nome}Worker");
            }}
            await Task.Delay(_intervalo, stoppingToken);
        }}
    }}
}}
'''

# ============================ DI PATCHES ============================

def patch_di_handler(raiz: Path, plural: str, nome: str, singular: str) -> bool:
    p = raiz / "servicos/api/Api/Configuration/DependencyInjectionConfig.cs"
    if not p.exists(): return False
    txt = p.read_text(encoding="utf-8")
    if f"{nome}Handler" in txt: return False
    for u in [f"using Dominios.{plural}.Comandos.Entradas;", f"using Dominios.{plural}.Comandos.Handlers;"]:
        if u not in txt:
            txt = re.sub(r"(using [^\n]+\n)(?!using )", r"\1" + u + "\n", txt, count=1)
    bloco = f"        services.AddScoped<IRequestHandler<{nome}Entrada, ComandResult>, {nome}Handler>();\n"
    txt = re.sub(r"(public static void RegisterServices[^{]*\{\n)", r"\1" + bloco, txt, count=1)
    p.write_text(txt, encoding="utf-8")
    return True

def patch_di_integracao(raiz: Path, nome: str) -> bool:
    p = raiz / "servicos/api/Api/Configuration/DependencyInjectionConfig.cs"
    if not p.exists(): return False
    txt = p.read_text(encoding="utf-8")
    if f"{nome}Service" in txt: return False
    if f"using Api.Integracoes.{nome};" not in txt:
        txt = re.sub(r"(using [^\n]+\n)(?!using )", rf"\1using Api.Integracoes.{nome};" + "\n", txt, count=1)
    bloco = (
        f'        services.Configure<{nome}Settings>(options => {{ options.WebhookSecret = "trocar-em-producao"; }});\n'
        f'        services.AddScoped<{nome}Service>();\n'
    )
    txt = re.sub(r"(public static void RegisterServices[^{]*\{\n)", r"\1" + bloco, txt, count=1)
    p.write_text(txt, encoding="utf-8")
    return True

def patch_di_report(raiz: Path, nome: str) -> bool:
    p = raiz / "servicos/api/Api/Configuration/DependencyInjectionConfig.cs"
    if not p.exists(): return False
    txt = p.read_text(encoding="utf-8")
    if f"{nome}Query" in txt: return False
    if "using Api.Relatorios;" not in txt:
        txt = re.sub(r"(using [^\n]+\n)(?!using )", r"\1using Api.Relatorios;\n", txt, count=1)
    bloco = f"        services.AddScoped<{nome}Query>();\n"
    txt = re.sub(r"(public static void RegisterServices[^{]*\{\n)", r"\1" + bloco, txt, count=1)
    p.write_text(txt, encoding="utf-8")
    return True

def patch_di_worker(raiz: Path, nome: str) -> bool:
    p = raiz / "servicos/api/Api/Configuration/DependencyInjectionConfig.cs"
    if not p.exists(): return False
    txt = p.read_text(encoding="utf-8")
    if f"{nome}Worker" in txt: return False
    if "using Api.Workers;" not in txt:
        txt = re.sub(r"(using [^\n]+\n)(?!using )", r"\1using Api.Workers;\n", txt, count=1)
    bloco = f"        services.AddHostedService<{nome}Worker>();\n"
    txt = re.sub(r"(public static void RegisterServices[^{]*\{\n)", r"\1" + bloco, txt, count=1)
    p.write_text(txt, encoding="utf-8")
    return True

def patch_controller_acao(raiz: Path, agregado: str, nome: str) -> bool:
    """Adiciona endpoint /v1/{acao} no Controller do agregado existente."""
    plural = agregado + "s" if not agregado.endswith("s") else agregado
    ctrl = raiz / f"servicos/api/Api/Controllers/{agregado}Controller.cs"
    if not ctrl.exists(): return False
    txt = ctrl.read_text(encoding="utf-8")
    if f"{nome}Entrada" in txt: return False
    if f"using Dominios.{plural}.Comandos.Entradas;" not in txt:
        txt = re.sub(r"(using [^\n]+\n)(?!using )", rf"\1using Dominios.{plural}.Comandos.Entradas;" + "\n", txt, count=1)
    rota = re.sub(r'(?<!^)(?=[A-Z])', '-', nome).lower()
    endpoint = (
        f'\n    [HttpPost("v1/{rota}")]\n'
        f'    public async Task<IComandResult> {nome}({nome}Entrada cmd) => await _mediator.EnviarComando(cmd);\n'
    )
    # inserir antes do fechamento da classe
    txt = re.sub(r"\n}\s*$", endpoint + "}\n", txt, count=1)
    ctrl.write_text(txt, encoding="utf-8")
    return True

# ============================ MAIN ============================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tipo", required=True, choices=["business-flow","integration","report","automation"])
    ap.add_argument("--nome", required=True, help="Ex: TransferirEntreContas, Stripe, SaldoMensal, LimpezaTokens")
    ap.add_argument("--agregado", default=None, help="business-flow: agregado afetado (ex: Movimento)")
    ap.add_argument("--raiz", default=".")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()

    if not (raiz / "servicos/api/Api/Api.csproj").exists():
        print(f"ERRO: nao parece projeto C#-portaria em {raiz}"); sys.exit(2)

    nome = args.nome
    nome_lower = nome[0].lower() + nome[1:]
    criados = []

    if args.tipo == "business-flow":
        if not args.agregado:
            print("ERRO: business-flow precisa --agregado"); sys.exit(2)
        ag = args.agregado
        plural = ag + "s" if not ag.endswith("s") else ag
        # detectar plural real pela pasta existente
        dom = raiz / "dominios/Dominios"
        candidatos = [d.name for d in dom.iterdir() if d.is_dir() and ag.lower() in d.name.lower()]
        if candidatos: plural = candidatos[0]

        # Entrada
        f1 = raiz / f"dominios/Dominios/{plural}/Comandos/Entradas/{nome}Entrada.cs"
        f1.parent.mkdir(parents=True, exist_ok=True)
        if not f1.exists():
            f1.write_text(T_ENTRADA_BF.format(Nome=nome, Plural=plural), encoding="utf-8")
            criados.append(f1.relative_to(raiz))

        # Handler
        f2 = raiz / f"dominios/Dominios/{plural}/Comandos/Handlers/{nome}Handler.cs"
        f2.parent.mkdir(parents=True, exist_ok=True)
        if not f2.exists():
            f2.write_text(T_HANDLER_BF.format(Nome=nome, Plural=plural, Singular=ag), encoding="utf-8")
            criados.append(f2.relative_to(raiz))

        if patch_di_handler(raiz, plural, nome, ag): print("  DI atualizado")
        if patch_controller_acao(raiz, ag, nome): print(f"  {ag}Controller: endpoint /v1/{re.sub(r'(?<!^)(?=[A-Z])', '-', nome).lower()} adicionado")

    elif args.tipo == "integration":
        base = raiz / f"servicos/api/Api/Integracoes/{nome}"
        base.mkdir(parents=True, exist_ok=True)
        f1 = base / f"{nome}Settings.cs"
        if not f1.exists(): f1.write_text(T_SETTINGS_INT.format(Nome=nome), encoding="utf-8"); criados.append(f1.relative_to(raiz))
        f2 = base / f"{nome}Service.cs"
        if not f2.exists(): f2.write_text(T_SERVICE_INT.format(Nome=nome, nome_lower=nome.lower()), encoding="utf-8"); criados.append(f2.relative_to(raiz))
        f3 = raiz / f"servicos/api/Api/Controllers/{nome}WebhookController.cs"
        if not f3.exists(): f3.write_text(T_WEBHOOK_CTRL_INT.format(Nome=nome, nome_lower=nome.lower()), encoding="utf-8"); criados.append(f3.relative_to(raiz))
        if patch_di_integracao(raiz, nome): print("  DI atualizado")

    elif args.tipo == "report":
        base = raiz / "servicos/api/Api/Relatorios"
        base.mkdir(parents=True, exist_ok=True)
        f1 = base / f"{nome}Query.cs"
        if not f1.exists(): f1.write_text(T_QUERY_RPT.format(Nome=nome), encoding="utf-8"); criados.append(f1.relative_to(raiz))
        f2 = base / f"{nome}Saida.cs"
        if not f2.exists(): f2.write_text(T_SAIDA_RPT.format(Nome=nome), encoding="utf-8"); criados.append(f2.relative_to(raiz))
        # RelatorioController base (so cria se nao existe)
        ctrl = raiz / "servicos/api/Api/Controllers/RelatorioController.cs"
        if not ctrl.exists():
            ctrl.write_text(T_RELATORIO_CTRL, encoding="utf-8"); criados.append(ctrl.relative_to(raiz))
        # partial com endpoint deste relatorio
        rota_lower = re.sub(r'(?<!^)(?=[A-Z])', '-', nome).lower()
        f3 = raiz / f"servicos/api/Api/Controllers/RelatorioController.{nome}.cs"
        if not f3.exists():
            f3.write_text(T_RELATORIO_PARTIAL.format(Nome=nome, nomeLower=nome[0].lower()+nome[1:], rota_lower=rota_lower), encoding="utf-8")
            criados.append(f3.relative_to(raiz))
        if patch_di_report(raiz, nome): print("  DI atualizado")

    elif args.tipo == "automation":
        base = raiz / "servicos/api/Api/Workers"
        base.mkdir(parents=True, exist_ok=True)
        f1 = base / f"{nome}Worker.cs"
        if not f1.exists(): f1.write_text(T_WORKER_AUTO.format(Nome=nome, nome_lower=nome.lower()), encoding="utf-8"); criados.append(f1.relative_to(raiz))
        if patch_di_worker(raiz, nome): print("  DI atualizado")

    print(f"\nCapacidade {args.tipo}: {nome}")
    for c in criados: print(f"  + {c}")
    if not criados: print("  (nada criado — arquivos ja existiam)")

    print(f"\nProximo: editar arquivos com TODO seguindo o contrato em estado/artefatos/")
    print(f"Apos editar: dotnet build && python .framework/scripts/migrate.py (se mudou schema)")

if __name__ == "__main__":
    main()
