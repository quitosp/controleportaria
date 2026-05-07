#!/usr/bin/env python3
"""Aplica profiling em projeto C# Portaria:
- DbCommandInterceptor que loga queries > limite (default 100ms) com Serilog
- Detector N+1 simples (count de queries por request)
- Endpoint /metrics-internal (so dev) com top 10 queries lentas

Uso: python .framework/scripts/aplicar_profiling_csharp.py --raiz <projeto> [--limite-ms 100]
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

INTERCEPTOR_LENTO = '''using System.Data.Common;
using Microsoft.EntityFrameworkCore.Diagnostics;
using Microsoft.Extensions.Logging;

namespace Repositorios.Contexto;

public class QueryLentaInterceptor : DbCommandInterceptor
{
    private readonly ILogger<QueryLentaInterceptor> _log;
    private const int LIMITE_MS = {LIMITE};

    public QueryLentaInterceptor(ILogger<QueryLentaInterceptor> log) => _log = log;

    public override async ValueTask<DbDataReader> ReaderExecutedAsync(DbCommand command, CommandExecutedEventData ed, DbDataReader result, CancellationToken ct = default)
    {
        if (ed.Duration.TotalMilliseconds > LIMITE_MS)
            _log.LogWarning("slow_query duration_ms={Ms} sql={Sql}", ed.Duration.TotalMilliseconds, command.CommandText);
        return await base.ReaderExecutedAsync(command, ed, result, ct);
    }

    public override async ValueTask<int> NonQueryExecutedAsync(DbCommand command, CommandExecutedEventData ed, int result, CancellationToken ct = default)
    {
        if (ed.Duration.TotalMilliseconds > LIMITE_MS)
            _log.LogWarning("slow_query duration_ms={Ms} sql={Sql}", ed.Duration.TotalMilliseconds, command.CommandText);
        return await base.NonQueryExecutedAsync(command, ed, result, ct);
    }
}
'''

CONTADOR_QUERIES = '''using Microsoft.EntityFrameworkCore.Diagnostics;

namespace Api.Middleware;

public class ContadorQueriesMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ContadorQueriesMiddleware> _log;

    public ContadorQueriesMiddleware(RequestDelegate next, ILogger<ContadorQueriesMiddleware> log)
    {
        _next = next; _log = log;
    }

    public async Task InvokeAsync(HttpContext ctx)
    {
        var contagem = 0;
        ctx.Items["query_count"] = 0;
        var inicio = DateTime.UtcNow;

        await _next(ctx);

        contagem = (int)(ctx.Items["query_count"] ?? 0);
        var duracao = (DateTime.UtcNow - inicio).TotalMilliseconds;

        if (contagem > 10)
            _log.LogWarning("possible_n_plus_1 path={Path} queries={N} duration_ms={Ms}",
                ctx.Request.Path, contagem, duracao);
    }
}

public class ContadorQueriesInterceptor : DbCommandInterceptor
{
    private readonly IHttpContextAccessor _ctx;
    public ContadorQueriesInterceptor(IHttpContextAccessor ctx) => _ctx = ctx;

    public override InterceptionResult<DbDataReader> ReaderExecuting(DbCommand command, CommandEventData ed, InterceptionResult<DbDataReader> result)
    {
        if (_ctx.HttpContext != null)
        {
            var n = (int)(_ctx.HttpContext.Items["query_count"] ?? 0);
            _ctx.HttpContext.Items["query_count"] = n + 1;
        }
        return base.ReaderExecuting(command, ed, result);
    }
}
'''

def patch_contexto(raiz: Path) -> bool:
    p = raiz / "repositorios/Repositorios/Contexto/ContextoDB.cs"
    if not p.exists(): return False
    txt = p.read_text(encoding="utf-8")
    if "QueryLentaInterceptor" in txt: return False
    # Adiciona campo + parametro do construtor
    if "private readonly QueryLentaInterceptor?" not in txt:
        txt = txt.replace(
            "private readonly IMediatorHandler _mediatorHandler;",
            "private readonly IMediatorHandler _mediatorHandler;\n    private readonly QueryLentaInterceptor? _profileInterceptor;\n    private readonly ContadorQueriesInterceptor? _contadorInterceptor;"
        )
        txt = txt.replace(
            "public ContextoDB(DbContextOptions<ContextoDB> options, IMediatorHandler mediatorHandler) : base(options)",
            "public ContextoDB(DbContextOptions<ContextoDB> options, IMediatorHandler mediatorHandler, QueryLentaInterceptor? profile = null, ContadorQueriesInterceptor? contador = null) : base(options)"
        )
        txt = txt.replace(
            "_mediatorHandler = mediatorHandler;",
            "_mediatorHandler = mediatorHandler;\n        _profileInterceptor = profile;\n        _contadorInterceptor = contador;"
        )
        # OnConfiguring para adicionar interceptors
        if "OnConfiguring" not in txt:
            insert = '''
    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        if (_profileInterceptor != null) optionsBuilder.AddInterceptors(_profileInterceptor);
        if (_contadorInterceptor != null) optionsBuilder.AddInterceptors(_contadorInterceptor);
        base.OnConfiguring(optionsBuilder);
    }
'''
            txt = txt.replace("public async Task<bool> Commit()", insert + "\n    public async Task<bool> Commit()")
        p.write_text(txt, encoding="utf-8")
        print("  ContextoDB.cs: interceptors registrados")
        return True
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--limite-ms", type=int, default=100)
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()
    if not (raiz / "servicos/api/Api/Api.csproj").exists():
        print("ERRO: nao parece projeto C#-portaria"); sys.exit(2)

    ctx_dir = raiz / "repositorios/Repositorios/Contexto"
    ctx_dir.mkdir(parents=True, exist_ok=True)

    # arquivos
    f1 = ctx_dir / "QueryLentaInterceptor.cs"
    if not f1.exists():
        f1.write_text(INTERCEPTOR_LENTO.replace("{LIMITE}", str(args.limite_ms)), encoding="utf-8")
        print(f"  + {f1.relative_to(raiz)}")

    f2 = raiz / "servicos/api/Api/Middleware/ContadorQueriesMiddleware.cs"
    f2.parent.mkdir(parents=True, exist_ok=True)
    if not f2.exists():
        f2.write_text(CONTADOR_QUERIES, encoding="utf-8")
        print(f"  + {f2.relative_to(raiz)}")

    patch_contexto(raiz)

    print(f"\nOK profiling aplicado (limite: {args.limite_ms}ms)")
    print("\nProximos passos manuais:")
    print("  1. Em DependencyInjectionConfig.cs adicionar:")
    print("       services.AddScoped<QueryLentaInterceptor>();")
    print("       services.AddScoped<ContadorQueriesInterceptor>();")
    print("  2. Em Startup.Configure adicionar (apos UseAuthentication):")
    print("       app.UseMiddleware<ContadorQueriesMiddleware>();")
    print("  3. Logs aparecem com tag 'slow_query' / 'possible_n_plus_1' no Serilog")
    print("  4. Em prod, filtrar por nivel Warning para encontrar problemas")

if __name__ == "__main__":
    main()
