#!/usr/bin/env python3
"""Detecta drift entre estado/index.json e filesystem real.
Avisa se o indice esta desatualizado.

Uso: python .framework/scripts/check_drift.py [--raiz .] [--max-idade-min 60]
"""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path

IGNORAR = {".git", "node_modules", "bin", "obj", ".framework", ".vs", "dist", "build", ".next", "__pycache__", ".venv", "venv", "Migrations"}
IGNORAR_EXT = {".dll", ".exe", ".pdb", ".zip", ".png", ".jpg", ".ico", ".woff", ".woff2", ".ttf", ".lock", ".log"}

def listar_atual(raiz: Path) -> set[str]:
    out = set()
    for f in raiz.rglob("*"):
        if not f.is_file(): continue
        try: rel = f.relative_to(raiz).parts
        except ValueError: continue
        if any(p in IGNORAR for p in rel): continue
        if f.suffix in IGNORAR_EXT: continue
        try:
            if f.stat().st_size > 500_000: continue
        except OSError: continue
        out.add("/".join(rel))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--max-idade-min", type=int, default=60)
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()
    idx_path = raiz / ".framework/estado/index.json"

    if not idx_path.exists():
        print("DRIFT: index.json nao existe — rode python .framework/scripts/indexar.py"); sys.exit(1)

    idx = json.loads(idx_path.read_text(encoding="utf-8"))
    gerado = datetime.fromisoformat(idx["gerado_em"].replace("Z","+00:00"))
    idade_min = (datetime.now(timezone.utc) - gerado).total_seconds() / 60

    indexados = set(idx["arquivos"].keys())
    atuais = listar_atual(raiz)

    novos = atuais - indexados
    sumidos = indexados - atuais

    msgs = []
    if idade_min > args.max_idade_min:
        msgs.append(f"indice tem {idade_min:.0f}min de idade (limite: {args.max_idade_min}min)")
    if novos: msgs.append(f"{len(novos)} arquivos novos no FS nao indexados")
    if sumidos: msgs.append(f"{len(sumidos)} arquivos no indice ja nao existem")

    if not msgs:
        print(f"OK indice atualizado ({idade_min:.0f}min, {len(atuais)} arquivos)"); return

    print("DRIFT:")
    for m in msgs: print(f"  - {m}")
    if novos:
        print("\nNovos (max 10):")
        for f in sorted(novos)[:10]: print(f"  + {f}")
    if sumidos:
        print("\nRemovidos (max 10):")
        for f in sorted(sumidos)[:10]: print(f"  - {f}")
    print("\nRode: python .framework/scripts/indexar.py")
    sys.exit(1)

if __name__ == "__main__":
    main()
