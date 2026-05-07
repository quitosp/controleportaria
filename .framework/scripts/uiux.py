#!/usr/bin/env python3
"""Wrapper para skill ui-ux-pro-max (repo nextlevelbuilder/ui-ux-pro-max-skill).

Uso identico ao search.py original mas com path curto:
  python .framework/scripts/uiux.py "petshop wellness" --design-system
  python .framework/scripts/uiux.py "fintech" --domain color
  python .framework/scripts/uiux.py "minimal dark" --domain style -n 5

Equivale a:
  python .framework/skills/ui-ux-pro-max/repo-original/src/ui-ux-pro-max/scripts/search.py ...
"""
from __future__ import annotations
import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # .framework/
SCRIPTS_DIR = ROOT / "skills/ui-ux-pro-max/repo-original/src/ui-ux-pro-max/scripts"
SEARCH_PY = SCRIPTS_DIR / "search.py"

if not SEARCH_PY.exists():
    print(f"ERRO: {SEARCH_PY} nao existe.")
    print("O repo ui-ux-pro-max-skill foi removido? Reclone:")
    print("  cd .framework/skills/ui-ux-pro-max && git clone --depth=1 https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git repo-original && rm -rf repo-original/.git")
    sys.exit(2)

# Adiciona scripts dir ao sys.path para imports relativos do core/design_system
sys.path.insert(0, str(SCRIPTS_DIR))

# Muda cwd para o root do repo original (para CSVs serem encontrados via rel paths)
os.chdir(SCRIPTS_DIR.parent)

# Re-executa search.py mantendo argv
import runpy
sys.argv[0] = str(SEARCH_PY)
runpy.run_path(str(SEARCH_PY), run_name="__main__")
