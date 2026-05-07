"""
Atualiza skills/ui-ux-pro-max/repo-original/ a partir do upstream
(github.com/nextlevelbuilder/ui-ux-pro-max-skill).

Estrategia: clone temporario raso → copia conteudo → remove .git → preserva
nosso SKILL.md adaptado em ../SKILL.md (apenas o repo-original e substituido).

Uso:
  python .framework/scripts/atualizar_uiux.py
  python .framework/scripts/atualizar_uiux.py --branch main
  python .framework/scripts/atualizar_uiux.py --dry  # mostra o que mudaria
"""
from __future__ import annotations
import argparse, shutil, subprocess, sys, tempfile, hashlib
from pathlib import Path

REPO = "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git"
ROOT = Path(__file__).resolve().parent.parent  # .framework/
ALVO = ROOT / "skills/ui-ux-pro-max/repo-original"


def hash_dir(p: Path) -> dict[str, str]:
    h = {}
    if not p.exists(): return h
    for f in p.rglob("*"):
        if f.is_file() and ".git" not in f.parts:
            rel = f.relative_to(p).as_posix()
            h[rel] = hashlib.md5(f.read_bytes()).hexdigest()
    return h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", default="main")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    if shutil.which("git") is None:
        print("ERRO: git nao encontrado no PATH.")
        sys.exit(2)

    antes = hash_dir(ALVO)

    with tempfile.TemporaryDirectory() as td:
        print(f"-> Clonando {REPO}@{args.branch} ...")
        r = subprocess.run(
            ["git", "clone", "--depth=1", "--branch", args.branch, REPO, td],
            capture_output=True, text=True
        )
        if r.returncode != 0:
            print("FALHA clone:", r.stderr.strip())
            sys.exit(1)

        novo = Path(td)
        depois = hash_dir(novo)

        adicionados = sorted(set(depois) - set(antes))
        removidos = sorted(set(antes) - set(depois))
        modificados = sorted(k for k in (set(antes) & set(depois)) if antes[k] != depois[k])

        print(f"   diff: +{len(adicionados)} ~{len(modificados)} -{len(removidos)}")
        if args.dry:
            for f in adicionados[:10]: print("   +", f)
            for f in modificados[:10]: print("   ~", f)
            for f in removidos[:10]: print("   -", f)
            if len(adicionados)+len(modificados)+len(removidos) > 30:
                print("   ... (truncado)")
            return

        if not (adicionados or modificados or removidos):
            print("Nada a fazer (ja sincronizado).")
            return

        if ALVO.exists():
            shutil.rmtree(ALVO)
        ALVO.parent.mkdir(parents=True, exist_ok=True)
        # copia, ignorando .git
        shutil.copytree(novo, ALVO, ignore=shutil.ignore_patterns(".git"))
        print(f"OK repo-original atualizado em {ALVO.relative_to(ROOT.parent)}")
        print("   nosso SKILL.md (../SKILL.md) preservado intocado.")


if __name__ == "__main__":
    main()
