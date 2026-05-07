"""
Verifica ambiente: dependencias, versoes, conflitos de porta.
Saida estruturada (texto simples) que a skill /instalar consome.

Uso: python verificar_ambiente.py [--raiz .] [--portas 3000,5001,7001,5432]
"""
from __future__ import annotations
import argparse, re, shutil, socket, subprocess, sys
from pathlib import Path

DEPS = [
    ("node", ["node", "--version"], r"v(\d+)\.", 20),
    ("npm", ["npm", "--version"], r"(\d+)\.", 9),
    ("python", ["python", "--version"], r"Python (\d+)\.(\d+)", (3, 10)),
    ("dotnet", ["dotnet", "--version"], r"^(\d+)\.", 9),
    ("git", ["git", "--version"], r"git version (\d+)\.", 2),
    ("psql", ["psql", "--version"], r"\(PostgreSQL\) (\d+)\.", 14),
    ("docker", ["docker", "--version"], r"Docker version (\d+)\.", 20),
]


def detectar_python():
    """Tenta py, python3, python — retorna o primeiro que funciona >=3.10."""
    for cmd in (["py"], ["python3"], ["python"]):
        if shutil.which(cmd[0]) is None: continue
        try:
            r = subprocess.run(cmd + ["--version"], capture_output=True, text=True, timeout=5)
            v = (r.stdout or r.stderr or "").strip()
            m = re.search(r"Python (\d+)\.(\d+)", v)
            if m and (int(m.group(1)) > 3 or (int(m.group(1)) == 3 and int(m.group(2)) >= 10)):
                return ("OK", v, " ".join(cmd))
        except Exception: pass
    return ("FALTA", "", "")


def porta_em_uso(porta: int) -> bool:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        r = s.connect_ex(("127.0.0.1", porta))
        s.close()
        return r == 0
    except Exception: return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--portas", default="3000,3001,5001,5168,5289,7001,7156,7219,7297,5432",
                    help="portas a verificar (CSV)")
    args = ap.parse_args()

    print("=== Dependencias ===")
    falhas = 0
    for nome, cmd, padrao, minimo in DEPS:
        if nome == "python":
            status, ver, qual = detectar_python()
            if status == "OK":
                print(f"  OK   {nome}:    {ver}  ({qual})")
            else:
                print(f"  FALTA {nome}:    nao detectado (tentei py, python3, python)")
                falhas += 1
            continue
        if shutil.which(cmd[0]) is None:
            obrigatorio = nome in ("node", "npm", "git")
            tag = "FALTA" if obrigatorio else "OPCIONAL"
            print(f"  {tag} {nome}: nao instalado")
            if obrigatorio: falhas += 1
            continue
        try:
            # Windows: usar shell=True pra .cmd (npm, npx, dotnet em alguns casos)
            usar_shell = sys.platform == "win32"
            cmd_str = " ".join(cmd) if usar_shell else cmd
            r = subprocess.run(cmd_str, capture_output=True, text=True, timeout=5, shell=usar_shell)
            v = (r.stdout or r.stderr or "").strip().splitlines()[0]
            m = re.search(padrao, v)
            if not m:
                print(f"  ?    {nome}:    detectado mas nao consegui parsear: {v}")
                continue
            if isinstance(minimo, tuple):
                versao_atual = (int(m.group(1)), int(m.group(2)))
                ok = versao_atual >= minimo
                req = f">= {minimo[0]}.{minimo[1]}"
            else:
                versao_atual = int(m.group(1))
                ok = versao_atual >= minimo
                req = f">= {minimo}"
            tag = "OK   " if ok else "VELHO"
            print(f"  {tag} {nome}:    {v}  ({req})")
            if not ok: falhas += 1
        except Exception as e:
            print(f"  ?    {nome}:    erro ao executar ({e})")

    print("\n=== Portas ===")
    portas = [int(p) for p in args.portas.split(",") if p.strip().isdigit()]
    em_uso = []
    for p in portas:
        if porta_em_uso(p):
            em_uso.append(p)
            print(f"  EM USO  porta {p}")
        else:
            print(f"  livre   porta {p}")

    print("\n=== Resumo ===")
    if falhas == 0:
        print("OK ambiente pronto")
    else:
        print(f"FALHA {falhas} dependencias obrigatorias faltando")
    if em_uso:
        print(f"AVISO {len(em_uso)} portas em uso: {em_uso}")
        print("       (pode atrapalhar /run — feche processos antes ou use outras portas)")
    sys.exit(0 if falhas == 0 else 1)


if __name__ == "__main__":
    main()
