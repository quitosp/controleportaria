#!/usr/bin/env python3
"""Estima tokens antes de Claude ler arquivo. Aborta se acima de --limite.
Uso: python .framework/scripts/token_check.py <arquivo> [--limite 5000]
Saida: linha "OK <tokens>" ou "BLOQUEADO <tokens> > <limite>" + sugestao."""
from __future__ import annotations
import sys, argparse
from pathlib import Path

def estimar(texto: str) -> int:
    # heuristica simples: ~4 chars por token
    return max(1, len(texto) // 4)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo")
    ap.add_argument("--limite", type=int, default=5000)
    args = ap.parse_args()
    p = Path(args.arquivo)
    if not p.exists():
        print(f"ERRO: {p} nao existe"); sys.exit(2)
    txt = p.read_text(encoding="utf-8", errors="replace")
    tokens = estimar(txt)
    linhas = txt.count("\n") + 1
    if tokens > args.limite:
        print(f"BLOQUEADO {tokens} > {args.limite} (linhas: {linhas})")
        print("Sugestoes:")
        print(f"  - Read parcial: passe offset/limit para ler regiao especifica")
        print(f"  - Use Grep para buscar simbolo dentro do arquivo")
        print(f"  - Use buscar.py se for codigo (consulta indice)")
        sys.exit(1)
    print(f"OK {tokens} tokens, {linhas} linhas")

if __name__ == "__main__":
    main()
