#!/usr/bin/env python3
"""Oraculo do framework.
Analisa o estado atual do projeto e diz o proximo passo logico.

Uso: python .framework/scripts/oraculo.py [--raiz .]
"""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path

def parse_yaml_simples(p: Path) -> dict:
    """Carrega YAML via pyyaml. Falha gracioso se arquivo invalido."""
    if not p.exists(): return {}
    try:
        import yaml
    except ImportError:
        return {}
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}

def estado_projeto(raiz: Path) -> dict:
    estado_dir = raiz / ".framework/estado"
    docs_dir = raiz / "documentacao"
    info = {
        "raiz": str(raiz),
        "tem_bmad": estado_dir.parent.exists(),
        "analise": parse_yaml_simples(estado_dir / "analise.yaml"),
        "tem_documentacao": docs_dir.exists() and any(docs_dir.glob("*.md")),
        "prd": parse_yaml_simples(estado_dir / "prd.yaml"),
        "arq": parse_yaml_simples(estado_dir / "arquitetura.yaml"),
        "ux": parse_yaml_simples(estado_dir / "ux.yaml"),
        "projeto": parse_yaml_simples(estado_dir / "projeto.yaml"),
        "index": None,
        "index_idade_min": None,
        "historias": [],
    }
    idx_path = estado_dir / "index.json"
    if idx_path.exists():
        try:
            idx = json.loads(idx_path.read_text(encoding="utf-8"))
            info["index"] = idx
            gerado = datetime.fromisoformat(idx["gerado_em"].replace("Z", "+00:00"))
            info["index_idade_min"] = int((datetime.now(timezone.utc) - gerado).total_seconds() / 60)
        except Exception: pass
    historias_dir = estado_dir / "historias"
    if historias_dir.exists():
        for h in sorted(historias_dir.glob("HIST-*.yaml")):
            info["historias"].append(parse_yaml_simples(h))
    return info

# Mapa de tipos legados (compatibilidade com projetos pre-hibridização)
TIPOS_LEGADOS = {
    "infra": "architecture",
    "agregado": "crud",
    "feature": "crud",
    "tela": "crud",
    "refatoracao": "refactor",
    "bug": "refactor",
}

def normalizar_tipo(tipo: str) -> str:
    """Converte tipos legados para os 8 tipos novos."""
    return TIPOS_LEGADOS.get(tipo, tipo)

def diagnosticar(s: dict) -> tuple[str, list[str]]:
    """Retorna (mensagem_proximo_passo, lista_comandos_relevantes)."""
    if not s["tem_bmad"]:
        return ("Pasta .framework/ nao encontrada. Voce esta no diretorio do projeto?", [])

    if not s["prd"]:
        # Se nao tem analise/documentacao, sugerir /ideia antes (modo conversacional + modelagem OO)
        if not s["analise"] and not s["tem_documentacao"]:
            return ("Nada criado ainda. Recomendo comecar pelo /ideia (engenheiro de software conversacional: "
                    "levanta requisitos em rodadas, modela OO, gera 7 docs estilo TCC). "
                    "Se preferir o caminho rapido, pule pra /prd.",
                    ["/ideia", "/prd"])
        # Tem analise mas nao tem PRD ainda — gerar PRD a partir dela
        return ("Analise pronta em documentacao/. Proximo: gerar PRD baseado na analise.",
                ["/prd"])

    prd = s["prd"]
    proj = prd.get("projeto", {})
    if not proj.get("nome") or not proj.get("stack"):
        return ("PRD existe mas tem campos obrigatorios faltando.",
                ["python .framework/scripts/validar_prd.py", "/editar-prd"])

    historias = s["historias"]
    web_ativa = bool(prd.get("plataformas", {}).get("web", {}).get("ativa", False))
    mobile_ativa = bool(prd.get("plataformas", {}).get("mobile", {}).get("ativa", False))

    # Se ja ha historias, pular checks de fases anteriores e ir direto pra analise
    if not historias:
        if not s["ux"] and (web_ativa or mobile_ativa):
            return ("PRD pronto. Como ha frontend, defina UX antes da arquitetura.",
                    ["/ux", "/uiux <tipo_produto>"])
        if not s["arq"]:
            return ("PRD pronto. Proximo: gerar arquitetura tecnica.",
                    ["/arq"])
        return ("Arquitetura pronta. Quebrar em historias de implementacao.",
                ["/historias"])

    # Analisar historias
    pendentes = [h for h in historias if h.get("estado") == "pendente"]
    aguardando = [h for h in historias if h.get("estado") == "aguardando_aprovacao"]
    em_prog = [h for h in historias if h.get("estado") == "em_progresso"]
    concluidas = [h for h in historias if h.get("estado") == "concluida"]
    revisao = [h for h in historias if h.get("revisao_necessaria")]

    if em_prog:
        h = em_prog[0]
        return (f"Historia em progresso: {h.get('id','?')} — {h.get('titulo','?')}. Continue ou marque como concluida.",
                [f"/impl {h.get('id','HIST-NNN')}", "/pos", "/commit"])

    if aguardando:
        h = aguardando[0]
        artefato = h.get("artefato") if isinstance(h.get("artefato"), dict) else {}
        cam = artefato.get("caminho", "?") if artefato else "?"
        return (f"Historia aguardando aprovacao: {h.get('id','?')} — {h.get('titulo','?')} (tipo {h.get('tipo','?')}). Artefato: {cam}",
                [f"/aprovar {h.get('id','HIST-NNN')}", f"/artefato {h.get('id','HIST-NNN')} (refazer se precisar)"])

    if revisao:
        h = revisao[0]
        return (f"Historia marcada para revisao: {h.get('id','?')} — {h.get('titulo','?')}. PRD/UX mudou.",
                [f"/impl {h.get('id','HIST-NNN')}", "/rev", "/editar-prd"])

    if pendentes:
        h = pendentes[0]
        tipo_raw = h.get("tipo", "crud")
        tipo = normalizar_tipo(tipo_raw)
        legado_aviso = f" (tipo legado '{tipo_raw}', tratado como '{tipo}' — rode /migrar-tipos)" if tipo_raw != tipo else ""
        artefato = h.get("artefato") if isinstance(h.get("artefato"), dict) else {}
        proximas = [p.get("id","?") for p in pendentes[:3]]
        # tipo nao-crud sem artefato aprovado: orientar gerar artefato
        if tipo not in ("crud", "architecture") and not (artefato and artefato.get("aprovado")):
            return (f"Proxima historia: {h.get('id','?')} — {h.get('titulo','?')} (tipo {tipo}{legado_aviso}). Precisa artefato antes de implementar.",
                    [f"/artefato {h.get('id','HIST-NNN')}", f"/aprovar {h.get('id','HIST-NNN')}", f"/impl {h.get('id','HIST-NNN')}"])
        return (f"Proxima historia: {h.get('id','?')} — {h.get('titulo','?')} (tipo {tipo}{legado_aviso}, {len(pendentes)} pendentes).",
                [f"/impl {h.get('id','HIST-NNN')}", "/impl proxima", "Proximas: " + ", ".join(proximas)])

    # Tudo concluido
    if s["index_idade_min"] is not None and s["index_idade_min"] > 60:
        return (f"Todas historias concluidas. Indice tem {s['index_idade_min']}min. Reindexar antes de seguir.",
                ["/idx", "/seguranca", "/observabilidade", "/ci", "/doc", "/run"])

    return (f"Todas as {len(concluidas)} historias concluidas. Hora de hardening + deploy.",
            ["/seguranca", "/observabilidade", "/ci", "/doc", "/run", "python .framework/scripts/aplicar_e2e.py --raiz pet-shop-web"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()

    s = estado_projeto(raiz)
    msg, comandos = diagnosticar(s)

    print("=== Estado do projeto ===")
    if s["prd"]:
        proj = s["prd"].get("projeto", {})
        print(f"Nome:  {proj.get('nome','?')}")
        print(f"Stack: {proj.get('stack','?')}")

    if s["historias"]:
        total = len(s["historias"])
        c = sum(1 for h in s["historias"] if h.get("estado") == "concluida")
        p = sum(1 for h in s["historias"] if h.get("estado") == "pendente")
        e = sum(1 for h in s["historias"] if h.get("estado") == "em_progresso")
        print(f"Historias: {c} concluidas, {e} em progresso, {p} pendentes (total {total})")

    auth = s["prd"].get("autenticacao", {}) if s["prd"] else {}
    if auth.get("ativa"):
        print(f"Auth: ativa ({auth.get('admin_seed', {}).get('email','admin@local')} seedado)")

    plat = s["prd"].get("plataformas", {}) if s["prd"] else {}
    plats = []
    if isinstance(plat, dict):
        if plat.get("api", {}).get("ativa") if isinstance(plat.get("api"), dict) else False: plats.append("api")
        if plat.get("web", {}).get("ativa") if isinstance(plat.get("web"), dict) else False: plats.append("web")
        if plat.get("mobile", {}).get("ativa") if isinstance(plat.get("mobile"), dict) else False: plats.append("mobile")
    if plats: print(f"Plataformas: {', '.join(plats)}")

    if s["index"]:
        e = s["index"].get("estatisticas", {})
        idade = f"{s['index_idade_min']}min" if s['index_idade_min'] is not None else "?"
        print(f"Indice: {e.get('total_arquivos','?')} arquivos, atualizado ha {idade}")

    print(f"\n=== Proximo passo recomendado ===")
    print(f"{msg}\n")
    if comandos:
        print("Comandos relevantes:")
        for c in comandos:
            print(f"  {c}")
    print()

if __name__ == "__main__":
    main()
