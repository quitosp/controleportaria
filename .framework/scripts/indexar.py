#!/usr/bin/env python3
"""Indexador de projeto. Gera .framework/estado/index.json com mapa de arquivos + simbolos.
Uso: python .framework/scripts/indexar.py [raiz_projeto] [--stack csharp-portaria]
Sem args: usa cwd e detecta stack."""
from __future__ import annotations
import json, os, re, sys, argparse
from datetime import datetime, timezone
from pathlib import Path

IGNORAR_DIRS = {".git", "node_modules", "bin", "obj", ".framework", ".vs", "dist", "build", ".next", "__pycache__", ".venv", "venv", "Migrations"}
IGNORAR_NA_RAIZ = {"Portaria-master"}  # so ignora se aparecer logo abaixo da raiz indexada
IGNORAR_EXT = {".dll", ".exe", ".pdb", ".zip", ".png", ".jpg", ".ico", ".woff", ".woff2", ".ttf", ".lock", ".log"}

REGEX_CS_CLASS = re.compile(r"^\s*(?:public|internal|private|protected)?\s*(?:abstract|sealed|static|partial)?\s*(class|interface|enum|record)\s+(\w+)")
REGEX_CS_METHOD = re.compile(r"^\s*public\s+(?:async\s+)?(?:virtual\s+|override\s+|static\s+)?[\w<>?,\s\[\]]+\s+(\w+)\s*\(")
REGEX_CS_NAMESPACE = re.compile(r"^\s*namespace\s+([\w\.]+)")
REGEX_CS_ROUTE = re.compile(r'\[(?:Http(\w+))(?:\("([^"]*)"\))?\]')
REGEX_CS_ROUTE_BASE = re.compile(r'\[Route\("([^"]+)"\)\]')

REGEX_TS_EXPORT = re.compile(r"^\s*export\s+(?:default\s+)?(?:async\s+)?(function|const|class|interface|type)\s+(\w+)")
REGEX_TS_HOOK = re.compile(r"^\s*(?:export\s+)?(?:default\s+)?function\s+(use[A-Z]\w*)")

REGEX_PY_DEF = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)\s*\(")
REGEX_PY_CLASS = re.compile(r"^\s*class\s+(\w+)")

# ~ 1 token = 4 chars (estimativa pessimista)
def estimar_tokens(tamanho_bytes: int) -> int:
    return max(1, tamanho_bytes // 4)

def detectar_tipo_arquivo(rel: str) -> str:
    p = rel.replace("\\", "/")
    if "/Entidades/" in p: return "entidade"
    if "/Comandos/Entradas/" in p: return "comando_entrada"
    if "/Comandos/Saidas/" in p: return "comando_saida"
    if "/Comandos/Handlers/" in p: return "handler"
    if "/IRepositorios/" in p: return "repositorio_iface"
    if "/Mapeamentos/" in p: return "mapeamento"
    if "/Repositorio/" in p and p.endswith(".cs"): return "repositorio_impl"
    if "/Controllers/" in p: return "controller"
    if "/Configuration/" in p or "appsettings" in p.lower(): return "config"
    if "/funcionalidades/" in p:
        if p.endswith("api.ts"): return "feature"
        if "/componentes/" in p: return "componente"
        if "/ganchos" in p: return "hook"
    return "outro"

def extrair_agregado(rel: str) -> str:
    p = rel.replace("\\", "/")
    m = re.search(r"/Dominios/([^/]+)/", p)
    if m: return m.group(1)
    m = re.search(r"/funcionalidades/([^/]+)/", p)
    if m: return m.group(1)
    return ""

def parse_csharp(texto: str, arquivo: str) -> tuple[list[dict], list[dict]]:
    simbolos, rotas = [], []
    namespace = ""
    base_route = ""
    controller_atual = ""
    for i, linha in enumerate(texto.splitlines(), 1):
        m = REGEX_CS_NAMESPACE.match(linha)
        if m: namespace = m.group(1); continue
        m = REGEX_CS_CLASS.match(linha)
        if m:
            tipo = m.group(1) if m.group(1) != "record" else "class"
            nome = m.group(2)
            simbolos.append({"nome": nome, "tipo": tipo, "arquivo": arquivo, "linha": i, "namespace": namespace, "assinatura": linha.strip()[:120]})
            if "Controller" in nome: controller_atual = nome
            continue
        m = REGEX_CS_ROUTE_BASE.search(linha)
        if m: base_route = m.group(1)
        m = REGEX_CS_ROUTE.search(linha)
        if m and controller_atual:
            metodo, sub = m.group(1).upper(), m.group(2) or ""
            rota = "/" + base_route.replace("[controller]", controller_atual.replace("Controller","").lower())
            if sub: rota = rota.rstrip("/") + "/" + sub.lstrip("/")
            rotas.append({"metodo": metodo, "rota": rota, "arquivo": arquivo, "linha": i, "controller": controller_atual})
        m = REGEX_CS_METHOD.match(linha)
        if m and "(" in linha:
            simbolos.append({"nome": m.group(1), "tipo": "method", "arquivo": arquivo, "linha": i, "assinatura": linha.strip()[:120]})
    return simbolos, rotas

def parse_ts(texto: str, arquivo: str) -> list[dict]:
    simbolos = []
    for i, linha in enumerate(texto.splitlines(), 1):
        m = REGEX_TS_EXPORT.match(linha)
        if m:
            tipo_raw, nome = m.group(1), m.group(2)
            tipo = {"function":"function","const":"function","class":"class","interface":"interface","type":"type"}.get(tipo_raw,"function")
            if tipo == "function" and nome.startswith("use") and len(nome) > 3 and nome[3].isupper():
                tipo = "hook"
            elif tipo == "function" and nome[0].isupper():
                tipo = "component"
            simbolos.append({"nome": nome, "tipo": tipo, "arquivo": arquivo, "linha": i, "assinatura": linha.strip()[:120]})
    return simbolos

def parse_py(texto: str, arquivo: str) -> list[dict]:
    simbolos = []
    for i, linha in enumerate(texto.splitlines(), 1):
        m = REGEX_PY_CLASS.match(linha)
        if m: simbolos.append({"nome": m.group(1), "tipo": "class", "arquivo": arquivo, "linha": i, "assinatura": linha.strip()[:120]}); continue
        m = REGEX_PY_DEF.match(linha)
        if m: simbolos.append({"nome": m.group(1), "tipo": "function", "arquivo": arquivo, "linha": i, "assinatura": linha.strip()[:120]})
    return simbolos

def detectar_stack(raiz: Path) -> str:
    if list(raiz.glob("**/*.sln")): return "csharp-portaria"
    if (raiz / "next.config.mjs").exists() or (raiz / "next.config.js").exists(): return "frontend-react"
    if (raiz / "pyproject.toml").exists() or (raiz / "requirements.txt").exists(): return "python-fastapi"
    return "hibrido"

def indexar(raiz: Path, stack: str | None = None) -> dict:
    stack = stack or detectar_stack(raiz)
    arquivos: dict[str, dict] = {}
    simbolos: list[dict] = []
    rotas: list[dict] = []
    agregados_esperados = ["Entidades", "Comandos/Entradas", "Comandos/Saidas", "Comandos/Handlers", "IRepositorios"]

    for caminho in raiz.rglob("*"):
        if caminho.is_dir(): continue
        try: rel_partes = caminho.relative_to(raiz).parts
        except ValueError: continue
        if any(p in IGNORAR_DIRS for p in rel_partes): continue
        if rel_partes and rel_partes[0] in IGNORAR_NA_RAIZ: continue
        if caminho.suffix in IGNORAR_EXT: continue
        try: stat = caminho.stat()
        except OSError: continue
        if stat.st_size > 500_000: continue  # arquivos enormes nao indexam conteudo

        rel = str(caminho.relative_to(raiz)).replace("\\", "/")
        meta = {
            "linhas": 0,
            "tamanho_bytes": stat.st_size,
            "tokens_estimados": estimar_tokens(stat.st_size),
            "tipo": detectar_tipo_arquivo(rel),
            "agregado": extrair_agregado(rel),
            "ultima_modificacao": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        }

        if caminho.suffix in {".cs", ".ts", ".tsx", ".js", ".jsx", ".py", ".md", ".yaml", ".yml", ".json"}:
            try:
                texto = caminho.read_text(encoding="utf-8", errors="replace")
                meta["linhas"] = texto.count("\n") + 1
                if caminho.suffix == ".cs":
                    s, r = parse_csharp(texto, rel); simbolos.extend(s); rotas.extend(r)
                elif caminho.suffix in {".ts", ".tsx", ".js", ".jsx"}:
                    simbolos.extend(parse_ts(texto, rel))
                elif caminho.suffix == ".py":
                    simbolos.extend(parse_py(texto, rel))
            except Exception:
                pass

        arquivos[rel] = meta

    # Agrupa por agregado
    agregados: dict[str, dict] = {}
    for rel, meta in arquivos.items():
        ag = meta["agregado"]
        if not ag: continue
        agregados.setdefault(ag, {"presentes": [], "ausentes": [], "completo": False})
        agregados[ag]["presentes"].append(rel)

    return {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "stack": stack,
        "raiz": str(raiz),
        "arquivos": arquivos,
        "simbolos": simbolos,
        "agregados": agregados,
        "rotas_api": rotas,
        "estatisticas": {
            "total_arquivos": len(arquivos),
            "total_simbolos": len(simbolos),
            "total_rotas": len(rotas),
            "tokens_total_estimados": sum(m["tokens_estimados"] for m in arquivos.values()),
        }
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raiz", nargs="?", default=".")
    ap.add_argument("--stack", default=None)
    ap.add_argument("--saida", default=None)
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()
    saida = Path(args.saida) if args.saida else raiz / ".framework" / "estado" / "index.json"
    saida.parent.mkdir(parents=True, exist_ok=True)
    dados = indexar(raiz, args.stack)
    saida.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    e = dados["estatisticas"]
    print(f"OK indexado: {e['total_arquivos']} arquivos, {e['total_simbolos']} simbolos, {e['total_rotas']} rotas, ~{e['tokens_total_estimados']} tokens")
    print(f"Saida: {saida}")

if __name__ == "__main__":
    main()
