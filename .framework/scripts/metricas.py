#!/usr/bin/env python3
"""Telemetria local do framework.
Cada script importante registra evento; este script agrega e mostra estatisticas.

Uso:
  python .framework/scripts/metricas.py registrar <evento> [--detalhes "json"]
  python .framework/scripts/metricas.py mostrar [--ultimos N]
  python .framework/scripts/metricas.py limpar
"""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path

ARQ_PADRAO = Path(__file__).parent.parent / "estado" / "metricas.jsonl"

def registrar(evento: str, detalhes: dict | None = None, arq: Path = ARQ_PADRAO):
    arq.parent.mkdir(parents=True, exist_ok=True)
    entrada = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evento": evento,
        "detalhes": detalhes or {},
    }
    with arq.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entrada, ensure_ascii=False) + "\n")

def carregar(arq: Path) -> list[dict]:
    if not arq.exists(): return []
    eventos = []
    for ln in arq.read_text(encoding="utf-8").splitlines():
        try: eventos.append(json.loads(ln))
        except json.JSONDecodeError: pass
    return eventos

def mostrar(arq: Path, ultimos: int = 0):
    eventos = carregar(arq)
    if not eventos:
        print("Nenhum evento registrado."); return
    if ultimos:
        eventos = eventos[-ultimos:]

    # contagem por evento
    contagem: dict[str, int] = {}
    for e in eventos:
        contagem[e["evento"]] = contagem.get(e["evento"], 0) + 1

    print(f"=== {len(eventos)} eventos ===\n")
    print("Por tipo:")
    for evento, n in sorted(contagem.items(), key=lambda x: -x[1]):
        print(f"  {n:4d}  {evento}")

    if ultimos:
        print(f"\nUltimos {ultimos}:")
        for e in eventos:
            ts = e["timestamp"][:19].replace("T", " ")
            d = e.get("detalhes", {})
            d_str = " ".join(f"{k}={v}" for k, v in d.items()) if d else ""
            print(f"  {ts}  {e['evento']:35} {d_str}")

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    s_reg = sub.add_parser("registrar")
    s_reg.add_argument("evento")
    s_reg.add_argument("--detalhes", default="{}", help="JSON com detalhes")

    s_mostrar = sub.add_parser("mostrar")
    s_mostrar.add_argument("--ultimos", type=int, default=20)

    sub.add_parser("limpar")

    args = ap.parse_args()
    arq = ARQ_PADRAO

    if args.cmd == "registrar":
        try: detalhes = json.loads(args.detalhes)
        except: detalhes = {}
        registrar(args.evento, detalhes, arq)
        print(f"OK registrado: {args.evento}")
    elif args.cmd == "mostrar":
        mostrar(arq, args.ultimos)
    elif args.cmd == "limpar":
        if arq.exists(): arq.unlink()
        print("OK limpo")

if __name__ == "__main__":
    main()
