#!/usr/bin/env python3
"""Roda migration add + database update no projeto C# atual.
Auto-detecta proxima versao (v1, v2, v3...) lendo a pasta Migrations/.

Uso:
  python .framework/scripts/migrate.py [--raiz <path>] [--nome <nome>] [--so-add | --so-update]

Sem args: detecta proxima versao e roda add + update.
"""
from __future__ import annotations
import argparse, re, subprocess, sys
from pathlib import Path

def proxima_versao(migrations_dir: Path) -> str:
    if not migrations_dir.exists(): return "v1"
    versoes = []
    for f in migrations_dir.glob("*_v*.cs"):
        m = re.search(r"_v(\d+)\.cs$", f.name)
        if m: versoes.append(int(m.group(1)))
    return f"v{max(versoes) + 1 if versoes else 1}"

def ef(cwd: Path, *args: str) -> tuple[int, str]:
    cmd = ["dotnet", "ef", *args,
           "--project", "repositorios/Repositorios",
           "--startup-project", "servicos/api/Api"]
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--nome", default=None, help="nome da migration; default: v{N+1}")
    ap.add_argument("--so-add", action="store_true")
    ap.add_argument("--so-update", action="store_true")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()

    if not (raiz / "repositorios/Repositorios/Repositorios.csproj").exists():
        print(f"ERRO: nao parece projeto C# no padrao Portaria em {raiz}"); sys.exit(2)

    if not args.so_update:
        nome = args.nome or proxima_versao(raiz / "repositorios/Repositorios/Migrations")
        print(f"-> dotnet ef migrations add {nome}")
        rc, out = ef(raiz, "migrations", "add", nome)
        if rc != 0:
            print(out); sys.exit(rc)
        print(f"   OK migration {nome} criada")

    if not args.so_add:
        print("-> dotnet ef database update")
        rc, out = ef(raiz, "database", "update")
        if rc != 0:
            print(out)
            if "does not exist" in out or "nao existe" in out or "não existe" in out:
                print("\nBanco nao existe. Crie antes:")
                print("  python .framework/scripts/criar_banco.py")
                print("Ou manualmente via psql:")
                # extrair nome do banco do connection string
                appsettings = raiz / "servicos/api/Api/appsettings.Development.json"
                if not appsettings.exists():
                    appsettings = raiz / "servicos/api/Api/appsettings.json"
                if appsettings.exists():
                    txt = appsettings.read_text(encoding="utf-8")
                    m = re.search(r"Database=([^;\"]+)", txt)
                    db = m.group(1) if m else "<nome_banco>"
                    print(f'  psql -U postgres -c "CREATE DATABASE {db} TEMPLATE template0;"')
            sys.exit(rc)
        print("   OK banco atualizado")

if __name__ == "__main__":
    main()
