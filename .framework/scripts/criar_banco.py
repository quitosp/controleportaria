#!/usr/bin/env python3
"""Cria banco Postgres lendo connection string do appsettings. Auto-detecta psql no Windows.
Uso: python .framework/scripts/criar_banco.py [--raiz .] [--banco <nome>] [--senha <senha>]

Detecta nome do banco e credenciais do appsettings.Development.json (preferido) ou appsettings.json.
Usa TEMPLATE template0 para evitar problema de collation mismatch.
"""
from __future__ import annotations
import argparse, os, re, subprocess, sys
from pathlib import Path

PSQL_CANDIDATOS_WINDOWS = [
    r"C:\Program Files\PostgreSQL\17\bin\psql.exe",
    r"C:\Program Files\PostgreSQL\16\bin\psql.exe",
    r"C:\Program Files\PostgreSQL\15\bin\psql.exe",
    r"C:\Program Files\PostgreSQL\14\bin\psql.exe",
]

def achar_psql() -> str | None:
    # 1. PATH
    for cmd in ["psql", "psql.exe"]:
        try:
            r = subprocess.run([cmd, "--version"], capture_output=True, timeout=5)
            if r.returncode == 0: return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired): pass
    # 2. paths comuns Windows
    for p in PSQL_CANDIDATOS_WINDOWS:
        if Path(p).exists(): return p
    return None

def parse_appsettings(raiz: Path) -> dict | None:
    for nome in ["appsettings.Development.json", "appsettings.json"]:
        p = raiz / "servicos/api/Api" / nome
        if not p.exists(): continue
        txt = p.read_text(encoding="utf-8")
        m_cs = re.search(r'"DefaultConnection"\s*:\s*"([^"]+)"', txt)
        if not m_cs: continue
        cs = m_cs.group(1)
        cfg = {}
        for par in cs.split(";"):
            if "=" in par:
                k, v = par.split("=", 1)
                cfg[k.strip().lower()] = v.strip()
        return cfg
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--banco", default=None)
    ap.add_argument("--senha", default=None)
    ap.add_argument("--usuario", default=None)
    ap.add_argument("--host", default=None)
    args = ap.parse_args()

    raiz = Path(args.raiz).resolve()
    cfg = parse_appsettings(raiz) or {}

    banco = args.banco or cfg.get("database")
    usuario = args.usuario or cfg.get("username") or "postgres"
    senha = args.senha or cfg.get("password") or ""
    host = args.host or cfg.get("host") or "localhost"
    porta = cfg.get("port") or "5432"

    if not banco:
        print("ERRO: nao consegui detectar nome do banco. Use --banco"); sys.exit(2)

    psql = achar_psql()
    if not psql:
        print("ERRO: psql nao encontrado no PATH nem em C:\\Program Files\\PostgreSQL\\")
        print("Instale Postgres ou rode manualmente:")
        print(f'  CREATE DATABASE {banco} TEMPLATE template0;')
        sys.exit(2)

    env = os.environ.copy()
    env["PGPASSWORD"] = senha

    # checa se ja existe
    r = subprocess.run([psql, "-U", usuario, "-h", host, "-p", porta, "-d", "postgres", "-tAc",
                        f"SELECT 1 FROM pg_database WHERE datname='{banco}'"],
                       capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"ERRO ao conectar no Postgres como {usuario}@{host}:{porta}")
        print(r.stderr)
        sys.exit(r.returncode)

    if "1" in (r.stdout or ""):
        print(f"OK banco '{banco}' ja existe")
        return

    # cria
    r = subprocess.run([psql, "-U", usuario, "-h", host, "-p", porta, "-d", "postgres", "-c",
                        f'CREATE DATABASE "{banco}" TEMPLATE template0;'],
                       capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(f"ERRO ao criar banco:")
        print(r.stderr or r.stdout)
        sys.exit(r.returncode)
    print(f"OK banco '{banco}' criado (TEMPLATE template0)")

if __name__ == "__main__":
    main()
