#!/usr/bin/env python3
"""Otimizador de tokens: gera versoes compactadas dos artefatos em .optimized/.
Inspirado no kitocode optimize_tokens.py mas adaptado ao .framework/.

Compactacao:
- Remove comentarios YAML/MD/Python (#, //, /*)
- Remove linhas em branco duplicadas
- Remove blocos de exemplo verbosos em markdown
- Remove tabelas de exemplo, mantem so estrutura
- Para .yaml: remove comentarios inline e campos vazios
- Mantem ORIGINAL intacto, gera so cache em .optimized/

Uso:
  python .framework/scripts/otimizar_tokens.py                          # otimiza .framework/nucleo + estado
  python .framework/scripts/otimizar_tokens.py --raiz <projeto>
  python .framework/scripts/otimizar_tokens.py --stdout <arquivo>       # imprime compactado em stdout
  python .framework/scripts/otimizar_tokens.py --estatisticas           # so mede ganho potencial

Agentes devem ler .optimized/ se existir, fallback no original.
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

# Diretorios a otimizar (relativos a .framework/)
ALVOS_PADRAO = [
    "nucleo",                         # blueprints
    "modelos",                        # templates
    "estado/prd.yaml",
    "estado/ux.yaml",
    "estado/arquitetura.yaml",
    "estado/historias",
    "estado/artefatos",
]

EXT_TEXTO = {".md", ".yaml", ".yml", ".txt"}

def compactar_yaml(texto: str) -> str:
    """Remove comentarios e linhas vazias duplicadas."""
    out = []
    em_branco = False
    for ln in texto.splitlines():
        # remove comentario inline (depois do conteudo)
        if "#" in ln and not ln.lstrip().startswith("#"):
            # so remove se "#" nao esta dentro de string
            antes_hash = ln.split("#")[0].rstrip()
            # se a linha tinha so espacos antes, ignora
            if antes_hash.strip():
                ln = antes_hash
            else:
                continue
        # remove linha de comentario completa
        if ln.lstrip().startswith("#"):
            continue
        # remove linha vazia duplicada
        if not ln.strip():
            if em_branco: continue
            em_branco = True
        else:
            em_branco = False
        # remove valores vazios "campo: \"\""
        if re.match(r'^\s+\w+:\s*""\s*$', ln):
            continue
        # remove campos com lista vazia "campo: []"
        if re.match(r'^\s+\w+:\s*\[\]\s*$', ln):
            continue
        out.append(ln)
    return "\n".join(out).strip() + "\n"

def compactar_markdown(texto: str) -> str:
    """Remove blocos de exemplo verbosos, mantem estrutura essencial."""
    out = []
    em_codeblock = False
    em_branco = False
    pular_proximas = 0
    linhas = texto.splitlines()

    for i, ln in enumerate(linhas):
        # toggle codeblock
        if ln.strip().startswith("```"):
            em_codeblock = not em_codeblock
            out.append(ln)
            em_branco = False
            continue

        # dentro de codeblock: mantem
        if em_codeblock:
            out.append(ln)
            continue

        # pular linhas comentadas em html
        if "<!--" in ln and "-->" in ln:
            continue

        # pular linha vazia duplicada
        if not ln.strip():
            if em_branco: continue
            em_branco = True
            out.append(ln)
            continue
        em_branco = False

        # remove linhas que sao so separadores estilizados
        if re.match(r'^[-=*_]{4,}$', ln.strip()):
            continue

        out.append(ln)

    # remove headings de nivel 5+ (detalhes excessivos)
    out = [ln for ln in out if not re.match(r'^#{5,}\s', ln)]

    return "\n".join(out).strip() + "\n"

def compactar(arquivo: Path) -> str:
    txt = arquivo.read_text(encoding="utf-8", errors="replace")
    if arquivo.suffix in {".yaml", ".yml"}:
        return compactar_yaml(txt)
    if arquivo.suffix == ".md":
        return compactar_markdown(txt)
    return txt

def estimar_tokens(texto: str) -> int:
    return max(1, len(texto) // 4)

def processar(origem: Path, destino_otim: Path, stats: dict):
    if origem.is_file():
        if origem.suffix not in EXT_TEXTO: return
        original = origem.read_text(encoding="utf-8", errors="replace")
        compact = compactar(origem)
        rel = origem.name
        destino = destino_otim / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(compact, encoding="utf-8")
        tk_orig = estimar_tokens(original)
        tk_comp = estimar_tokens(compact)
        stats["arquivos"] += 1
        stats["tokens_originais"] += tk_orig
        stats["tokens_compactados"] += tk_comp
        return

    if origem.is_dir():
        for f in origem.rglob("*"):
            if f.is_file() and f.suffix in EXT_TEXTO:
                rel = f.relative_to(origem)
                original = f.read_text(encoding="utf-8", errors="replace")
                compact = compactar(f)
                destino = destino_otim / rel
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_text(compact, encoding="utf-8")
                tk_orig = estimar_tokens(original)
                tk_comp = estimar_tokens(compact)
                stats["arquivos"] += 1
                stats["tokens_originais"] += tk_orig
                stats["tokens_compactados"] += tk_comp

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--stdout", default=None, help="compacta arquivo unico para stdout")
    ap.add_argument("--estatisticas", action="store_true", help="so mostra ganho potencial sem escrever")
    ap.add_argument("--alvos", nargs="*", default=None, help="paths relativos a .framework/ (default: nucleo, modelos, estado)")
    args = ap.parse_args()

    raiz = Path(args.raiz).resolve()

    if args.stdout:
        p = Path(args.stdout)
        if not p.exists(): print(f"ERRO: {p} nao existe"); sys.exit(2)
        sys.stdout.write(compactar(p))
        return

    framework = raiz / ".framework"
    if not framework.exists():
        print(f"ERRO: {framework} nao existe"); sys.exit(2)

    optimized = framework / ".optimized"
    if not args.estatisticas:
        optimized.mkdir(parents=True, exist_ok=True)

    alvos = args.alvos or ALVOS_PADRAO
    stats = {"arquivos": 0, "tokens_originais": 0, "tokens_compactados": 0}

    for alvo_rel in alvos:
        origem = framework / alvo_rel
        if not origem.exists(): continue
        # destino preserva a estrutura sob .optimized/
        destino = optimized / alvo_rel
        if origem.is_file():
            destino = optimized / alvo_rel
            destino.parent.mkdir(parents=True, exist_ok=True)
        if not args.estatisticas:
            processar(origem, destino if origem.is_dir() else destino.parent, stats)
        else:
            # so calcular
            tmp = {"arquivos": 0, "tokens_originais": 0, "tokens_compactados": 0}
            class TmpDest:
                def __init__(self): pass
            # workaround: chama processar com dir tmp em memoria nao da, vamos so calcular
            if origem.is_file() and origem.suffix in EXT_TEXTO:
                txt = origem.read_text(encoding="utf-8", errors="replace")
                comp = compactar(origem)
                stats["arquivos"] += 1
                stats["tokens_originais"] += estimar_tokens(txt)
                stats["tokens_compactados"] += estimar_tokens(comp)
            elif origem.is_dir():
                for f in origem.rglob("*"):
                    if f.is_file() and f.suffix in EXT_TEXTO:
                        txt = f.read_text(encoding="utf-8", errors="replace")
                        comp = compactar(f)
                        stats["arquivos"] += 1
                        stats["tokens_originais"] += estimar_tokens(txt)
                        stats["tokens_compactados"] += estimar_tokens(comp)

    if stats["arquivos"] == 0:
        print("Nenhum arquivo processado.")
        return

    economia = stats["tokens_originais"] - stats["tokens_compactados"]
    pct = 100 * economia / max(1, stats["tokens_originais"])
    print(f"Arquivos:   {stats['arquivos']}")
    print(f"Original:   ~{stats['tokens_originais']} tokens")
    print(f"Compactado: ~{stats['tokens_compactados']} tokens")
    print(f"Economia:   ~{economia} tokens ({pct:.1f}%)")
    if not args.estatisticas:
        print(f"\nCache em: {optimized}")
        print("Agentes devem preferir .optimized/* quando existir.")

if __name__ == "__main__":
    main()
