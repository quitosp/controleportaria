#!/usr/bin/env python3
"""Valida estado/prd.yaml antes de avancar para arquitetura.
Detecta campos obrigatorios faltantes, contradicoes e inconsistencias.

Uso: python .framework/scripts/validar_prd.py [--raiz .]
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

def carregar_yaml(p: Path) -> dict:
    """Carrega YAML usando pyyaml (instalavel via pip install pyyaml)."""
    if not p.exists(): return {}
    try:
        import yaml
    except ImportError:
        print("ERRO: pyyaml nao instalado. Rode: py -m pip install pyyaml")
        sys.exit(2)
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        print(f"ERRO de parsing YAML em {p}: {e}")
        sys.exit(2)

class Erro:
    def __init__(self, sev: str, campo: str, msg: str):
        self.sev = sev; self.campo = campo; self.msg = msg
    def __repr__(self):
        return f"[{self.sev}] {self.campo}: {self.msg}"

def validar(prd: dict) -> list[Erro]:
    erros = []
    OBR = "OBRIG"
    AVISO = "AVISO"

    proj = prd.get("projeto", {})
    if not proj.get("nome"): erros.append(Erro(OBR, "projeto.nome", "obrigatorio"))
    if not proj.get("stack"): erros.append(Erro(OBR, "projeto.stack", "obrigatorio (csharp-portaria | frontend-react | flutter-mobile | hibrido)"))
    elif proj.get("stack") not in ("csharp-portaria","frontend-react","flutter-mobile","hibrido","python-fastapi"):
        erros.append(Erro(OBR, "projeto.stack", f"valor invalido: {proj['stack']}"))

    prob = prd.get("problema", {})
    if not prob.get("dor"): erros.append(Erro(AVISO, "problema.dor", "recomendado preencher"))
    if not prob.get("metrica_sucesso"): erros.append(Erro(AVISO, "problema.metrica_sucesso", "como saber se deu certo?"))

    usuarios = prd.get("usuarios", [])
    if not usuarios: erros.append(Erro(OBR, "usuarios", "ao menos 1 perfil"))

    agregados = prd.get("agregados", [])
    if not agregados: erros.append(Erro(OBR, "agregados", "ao menos 1 agregado"))
    nomes = []
    for i, a in enumerate(agregados):
        if not isinstance(a, dict): continue
        nome = a.get("nome", "")
        if not nome:
            erros.append(Erro(OBR, f"agregados[{i}].nome", "obrigatorio")); continue
        if nome in nomes:
            erros.append(Erro(OBR, f"agregados[{i}].nome", f"duplicado: {nome}"))
        nomes.append(nome)
        if nome[0].islower():
            erros.append(Erro(AVISO, f"agregados[{i}].nome", "deve comecar com maiuscula (PascalCase)"))
        if not a.get("plural"):
            erros.append(Erro(AVISO, f"agregados[{i}].plural", "preencher para evitar pluralizacao automatica"))

    auth = prd.get("autenticacao", {})
    if auth.get("ativa") and not auth.get("estrategia"):
        erros.append(Erro(AVISO, "autenticacao.estrategia", "preencher (jwt|nenhuma)"))

    rbac = prd.get("rbac", {})
    if rbac.get("ativo"):
        roles = rbac.get("roles", [])
        if not roles:
            erros.append(Erro(OBR, "rbac.roles", "rbac ativo mas sem roles definidas"))

    plat = prd.get("plataformas", {})
    if not plat:
        erros.append(Erro(AVISO, "plataformas", "preencher se PRD novo (api/web/mobile)"))
    web = plat.get("web", {}) if isinstance(plat, dict) else {}
    if web.get("ativa") and not web.get("modo"):
        erros.append(Erro(AVISO, "plataformas.web.modo", "apenas-desktop|responsivo|pwa-instalavel"))
    mobile = plat.get("mobile", {}) if isinstance(plat, dict) else {}
    if mobile.get("ativa") and not mobile.get("tipo"):
        erros.append(Erro(AVISO, "plataformas.mobile.tipo", "nao|so-pwa|flutter-nativo"))

    # Coerencia: features_frontend declaradas mas plataformas.web.ativa=false
    feats = prd.get("features_frontend", [])
    if feats and not web.get("ativa"):
        erros.append(Erro(AVISO, "consistencia", "features_frontend definidas mas plataformas.web.ativa=false"))

    # Validar integracoes
    integracoes = prd.get("integracoes", [])
    for i, integ in enumerate(integracoes):
        if not isinstance(integ, dict): continue
        if not integ.get("nome"):
            erros.append(Erro(OBR, f"integracoes[{i}].nome", "obrigatorio"))
        if not integ.get("tipo"):
            erros.append(Erro(OBR, f"integracoes[{i}].tipo", "obrigatorio (webhook|rest|grpc|broker)"))
        if integ.get("tipo") == "webhook" and not integ.get("auth"):
            erros.append(Erro(AVISO, f"integracoes[{i}].auth", "webhook sem auth (HMAC/Bearer/...) e inseguro"))
        if not integ.get("proposito"):
            erros.append(Erro(AVISO, f"integracoes[{i}].proposito", "preencher para clareza"))

    return erros

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()
    prd_path = raiz / ".framework/estado/prd.yaml"
    if not prd_path.exists():
        print(f"ERRO: {prd_path} nao existe. Rode /prd primeiro."); sys.exit(2)

    prd = carregar_yaml(prd_path)
    erros = validar(prd)

    obr = [e for e in erros if e.sev == "OBRIG"]
    avi = [e for e in erros if e.sev == "AVISO"]

    print(f"Validacao de {prd_path}\n")
    print(f"Projeto: {prd.get('projeto',{}).get('nome','?')}")
    print(f"Stack: {prd.get('projeto',{}).get('stack','?')}")
    print(f"Agregados: {len(prd.get('agregados',[]))}")
    print(f"Plataformas: api={prd.get('plataformas',{}).get('api',{}).get('ativa','?')} web={prd.get('plataformas',{}).get('web',{}).get('ativa','?')} mobile={prd.get('plataformas',{}).get('mobile',{}).get('ativa','?')}")
    print()

    if obr:
        print(f"=== {len(obr)} ERROS OBRIGATORIOS ===")
        for e in obr: print(f"  {e}")
    if avi:
        print(f"\n=== {len(avi)} avisos ===")
        for e in avi: print(f"  {e}")

    if not erros:
        print("OK PRD valido. Pronto para /arq.")
        return

    if obr:
        print("\nFALHA: corrija obrigatorios antes de prosseguir.")
        sys.exit(1)
    print("\nOK PRD com avisos (nao bloqueia /arq).")

if __name__ == "__main__":
    main()
