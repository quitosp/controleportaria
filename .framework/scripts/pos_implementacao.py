#!/usr/bin/env python3
"""Orquestrador automatico pos-implementacao:
1. Reindexa o projeto (indexar.py)
2. Roda lint estrutural (revisar_codigo.py)
3. Roda auditoria de seguranca (verificar_seguranca.py)
4. Reporta consolidado

Falha (exit 1) se houver criticos/altos no review ou criticos na seguranca.

Uso: python .framework/scripts/pos_implementacao.py [--raiz .] [--stack csharp|next|flutter|all]
                                            [--sem-bloqueio] [--apenas <feat>]
"""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

def rodar(script: str, args: list[str]) -> int:
    cmd = [sys.executable, str(SCRIPTS_DIR / script)] + args
    print(f"\n>>> {script} {' '.join(args)}")
    try:
        return subprocess.run(cmd, check=False).returncode
    except Exception as e:
        print(f"  ERRO ao executar {script}: {e}")
        return 0  # nao bloqueia se erro de execucao

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--stack", choices=["csharp", "next", "flutter", "all"], default="all")
    ap.add_argument("--apenas", default=None, help="filtra agregado/feature")
    ap.add_argument("--sem-bloqueio", action="store_true", help="nao falha se houver issues (so reporta)")
    ap.add_argument("--sem-seguranca", action="store_true", help="pula auditoria de seguranca")
    ap.add_argument("--sem-review", action="store_true", help="pula review estrutural")
    args = ap.parse_args()
    raiz = str(Path(args.raiz).resolve())

    print(f"=== POS-IMPLEMENTACAO em {raiz} ===")

    # 1. Reindexar
    rc_idx = rodar("indexar.py", [raiz])

    # 2. Review estrutural
    rc_rev = 0
    if not args.sem_review:
        rev_args = [raiz] if False else ["--raiz", raiz, "--stack", args.stack]
        if args.apenas: rev_args += ["--apenas", args.apenas]
        rc_rev = rodar("revisar_codigo.py", rev_args)

    # 3. Seguranca
    rc_sec = 0
    if not args.sem_seguranca:
        sec_args = ["--raiz", raiz, "--stack", args.stack]
        rc_sec = rodar("verificar_seguranca.py", sec_args)

    # Resumo
    print("\n=== RESUMO POS-IMPLEMENTACAO ===")
    print(f"  indexar:           {'OK' if rc_idx == 0 else f'falhou ({rc_idx})'}")
    print(f"  review estrutural: {'OK' if rc_rev == 0 else 'desvios CRITICO/ALTO'}")
    print(f"  seguranca:         {'OK' if rc_sec == 0 else 'achados CRITICOS'}")

    bloqueia = (rc_rev != 0) or (rc_sec != 0)
    if bloqueia and not args.sem_bloqueio:
        print("\nFALHA: corrija desvios criticos/altos antes de prosseguir.")
        print("Para ignorar (nao recomendado): adicionar --sem-bloqueio")
        sys.exit(1)

    print("\nOK pronto para commit.")

if __name__ == "__main__":
    main()
