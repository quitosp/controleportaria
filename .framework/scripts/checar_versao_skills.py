"""
Compara versao do framework instalado no projeto contra a do package atual.
Sugere atualizacao se diferente.

Uso: python checar_versao_skills.py [--raiz .]
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()

    versao_local = (raiz / ".framework/.version").read_text(encoding="utf-8").strip() if (raiz / ".framework/.version").exists() else None

    # Versao do CLI/pacote (se rodando dentro do node_modules ou do source)
    pkg_path = raiz / "package.json"
    versao_pacote = None
    if pkg_path.exists():
        try:
            data = json.loads(pkg_path.read_text(encoding="utf-8"))
            if data.get("name") == "kitocode":
                versao_pacote = data.get("version")
        except Exception: pass

    if versao_local is None:
        print("AVISO: .framework/.version nao existe (instalacao antiga ou incompleta).")
        print("       Recomendado: npx kitocode@latest .  (com --force)")
        sys.exit(2)

    if versao_pacote and versao_local != versao_pacote:
        print(f"DRIFT detectado: framework instalado v{versao_local} != source v{versao_pacote}")
        print(f"Atualize: npx kitocode@latest .  (com --force)")
        sys.exit(1)

    print(f"OK framework v{versao_local}")


if __name__ == "__main__":
    main()
