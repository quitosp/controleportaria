#!/usr/bin/env python3
"""Busca em estado/index.json sem ler arquivos. Uso:
  python .framework/scripts/buscar.py <termo>                       -> simbolos contendo termo
  python .framework/scripts/buscar.py --rota /api/empresa           -> rotas
  python .framework/scripts/buscar.py --tipo handler                -> arquivos por tipo
  python .framework/scripts/buscar.py --agregado Empresa            -> agregado completo
  python .framework/scripts/buscar.py --simbolo Empresa --tipo class  -> filtra
  python .framework/scripts/buscar.py --conteudo "ConnectionString" -> grep em arquivos do indice
  python .framework/scripts/buscar.py --conteudo "throw" --tipo handler  -> grep so em handlers
"""
from __future__ import annotations
import json, sys, argparse
from pathlib import Path

def carregar_indice(raiz: Path) -> dict:
    p = raiz / ".framework" / "estado" / "index.json"
    if not p.exists():
        print(f"ERRO: {p} nao existe. Rode indexar.py primeiro.", file=sys.stderr); sys.exit(2)
    return json.loads(p.read_text(encoding="utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("termo", nargs="?")
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--simbolo")
    ap.add_argument("--tipo", help="class | interface | method | function | hook | component | enum | type | schema | (ou tipo de arquivo: handler, controller, etc)")
    ap.add_argument("--rota")
    ap.add_argument("--agregado")
    ap.add_argument("--conteudo", help="grep regex em arquivos indexados")
    ap.add_argument("--limite", type=int, default=50)
    args = ap.parse_args()

    raiz = Path(args.raiz).resolve()
    idx = carregar_indice(raiz)

    if args.conteudo:
        import re
        try: pattern = re.compile(args.conteudo, re.IGNORECASE)
        except re.error as e: print(f"ERRO regex invalido: {e}"); sys.exit(2)
        achados = []
        for rel, meta in idx["arquivos"].items():
            if args.tipo and meta.get("tipo") != args.tipo: continue
            arq = raiz / rel
            if not arq.exists(): continue
            try: txt = arq.read_text(encoding="utf-8", errors="replace")
            except Exception: continue
            for i, linha in enumerate(txt.splitlines(), 1):
                if pattern.search(linha):
                    achados.append((rel, i, linha.strip()[:120]))
                    if len(achados) >= args.limite: break
            if len(achados) >= args.limite: break
        for rel, n, ln in achados:
            print(f"{rel}:{n}  {ln}")
        if not achados: print("(nenhuma ocorrencia)")
        return

    if args.agregado:
        ag = idx["agregados"].get(args.agregado)
        if not ag: print(f"Agregado {args.agregado} nao encontrado"); return
        print(f"=== Agregado {args.agregado} ===")
        for f in ag["presentes"]: print(f"  {f}")
        return

    if args.rota:
        achados = [r for r in idx["rotas_api"] if args.rota.lower() in r["rota"].lower()]
        for r in achados[:args.limite]:
            print(f"{r['metodo']:6} {r['rota']:50} -> {r['arquivo']}:{r['linha']}")
        return

    if args.tipo and not (args.termo or args.simbolo):
        # filtra arquivos por tipo
        achados = [(p, m) for p, m in idx["arquivos"].items() if m.get("tipo") == args.tipo]
        for p, m in achados[:args.limite]:
            print(f"{p}  ({m['linhas']} linhas, ~{m['tokens_estimados']}tk)")
        return

    termo = (args.simbolo or args.termo or "").lower()
    if not termo:
        print("Forneca termo, --simbolo, --rota, --tipo ou --agregado"); sys.exit(1)

    simbolos = idx["simbolos"]
    achados = [s for s in simbolos if termo in s["nome"].lower()]
    if args.tipo:
        achados = [s for s in achados if s["tipo"] == args.tipo]
    for s in achados[:args.limite]:
        ns = f" [{s.get('namespace','')}]" if s.get("namespace") else ""
        print(f"{s['tipo']:10} {s['nome']:35} {s['arquivo']}:{s['linha']}{ns}")
    if len(achados) > args.limite:
        print(f"... +{len(achados)-args.limite} (use --limite)")

if __name__ == "__main__":
    main()
