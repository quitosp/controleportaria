#!/usr/bin/env python3
"""Captura saida de dotnet build e extrai apenas erros relevantes em formato compacto.
Reduz centenas de linhas de saida para uma lista de 'arquivo:linha:mensagem'.

Uso:
  python .framework/scripts/parse_dotnet_errors.py < saida.txt
  dotnet build 2>&1 | python .framework/scripts/parse_dotnet_errors.py
  python .framework/scripts/parse_dotnet_errors.py --rodar --raiz .
"""
from __future__ import annotations
import argparse, re, subprocess, sys
from pathlib import Path

# Padroes msbuild/dotnet errors:
# C:\path\file.cs(12,34): error CS0103: ...
RE_ERR = re.compile(r"^(.+?)\((\d+)(?:,\d+)?\):\s+(error|warning)\s+(\w+):\s+(.+?)(?:\s+\[.+\])?$")
# Tambem captura "error MSB...":
RE_MSB = re.compile(r"^(?:.*?:\s+)?error\s+(MSB\d+):\s+(.+)$")

def parse(linhas: list[str], so_erros: bool = True) -> list[dict]:
    out = []
    for ln in linhas:
        ln = ln.rstrip()
        m = RE_ERR.match(ln)
        if m:
            arq, linha, sev, codigo, msg = m.groups()
            if so_erros and sev != "error": continue
            out.append({"arquivo": arq, "linha": int(linha), "severidade": sev, "codigo": codigo, "msg": msg.strip()})
            continue
        m = RE_MSB.match(ln)
        if m and so_erros:
            out.append({"arquivo": "<msbuild>", "linha": 0, "severidade": "error", "codigo": m.group(1), "msg": m.group(2).strip()})
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rodar", action="store_true", help="executa 'dotnet build' e parseia")
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--avisos", action="store_true", help="incluir warnings")
    args = ap.parse_args()

    if args.rodar:
        proc = subprocess.run(["dotnet", "build", "--nologo"], cwd=args.raiz,
                              capture_output=True, text=True, encoding="utf-8", errors="replace")
        linhas = (proc.stdout + "\n" + proc.stderr).splitlines()
        codigo_saida = proc.returncode
    else:
        linhas = sys.stdin.read().splitlines()
        codigo_saida = 0

    erros = parse(linhas, so_erros=not args.avisos)
    raiz_abs = str(Path(args.raiz).resolve())

    if not erros:
        print("OK sem erros" if codigo_saida == 0 else f"FALHA codigo {codigo_saida} mas nenhum erro extraido")
        return

    # encurta paths
    for e in erros:
        try:
            arq = Path(e["arquivo"])
            if arq.is_absolute():
                e["arquivo"] = str(arq.resolve().relative_to(raiz_abs)).replace("\\","/")
        except Exception: pass

    # agrupa por arquivo
    por_arq = {}
    for e in erros:
        por_arq.setdefault(e["arquivo"], []).append(e)

    print(f"FALHA {len(erros)} erros em {len(por_arq)} arquivos:")
    for arq, lst in por_arq.items():
        print(f"\n{arq}:")
        for e in lst:
            print(f"  L{e['linha']:>4} {e['codigo']}: {e['msg']}")

if __name__ == "__main__":
    main()
