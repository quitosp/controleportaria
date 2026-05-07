"""
Aplica correcoes idempotentes em projeto Next.js gerado pelo create-next-app.

Patches aplicados:
1. app/layout.tsx — adiciona suppressHydrationWarning no <html> e <body>
   (tolera extensoes do navegador como ColorZilla que injetam cz-shortcut-listen).
2. middleware.ts — nao usado mas reservado para futuras correcoes.
3. tsconfig.json — garante "@/*": ["./src/*"] alias (caso create-next-app nao tenha colocado).

Uso:
  python .framework/scripts/aplicar_correcoes_frontend.py [--raiz .]

Idempotente: rodar varias vezes nao quebra nada.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path


def patch_layout(raiz: Path) -> bool:
    candidatos = [raiz / "src/app/layout.tsx", raiz / "app/layout.tsx"]
    layout = next((c for c in candidatos if c.exists()), None)
    if not layout:
        print("  -- app/layout.tsx nao encontrado, pulando")
        return False

    txt = layout.read_text(encoding="utf-8")
    mudou = False

    # 1. suppressHydrationWarning no <html>
    if "<html" in txt and "suppressHydrationWarning" not in txt.split("<body")[0]:
        txt = re.sub(r"(<html\b)([^>]*)(>)", r'\1\2 suppressHydrationWarning\3', txt, count=1)
        mudou = True

    # 2. suppressHydrationWarning no <body>
    body_match = re.search(r"<body\b([^>]*)>", txt)
    if body_match and "suppressHydrationWarning" not in body_match.group(0):
        txt = txt.replace(body_match.group(0), body_match.group(0)[:-1] + " suppressHydrationWarning>")
        mudou = True

    if mudou:
        layout.write_text(txt, encoding="utf-8")
        print(f"  OK {layout.relative_to(raiz)}: suppressHydrationWarning aplicado")
    else:
        print(f"  -- {layout.relative_to(raiz)}: ja tem suppressHydrationWarning")
    return mudou


def patch_tsconfig(raiz: Path) -> bool:
    p = raiz / "tsconfig.json"
    if not p.exists(): return False
    try:
        cfg = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  AVISO tsconfig.json invalido ({e})"); return False
    co = cfg.setdefault("compilerOptions", {})
    paths = co.setdefault("paths", {})
    if paths.get("@/*") != ["./src/*"]:
        paths["@/*"] = ["./src/*"]
        co["baseUrl"] = "."
        p.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
        print("  OK tsconfig.json: alias @/* -> src/*")
        return True
    print("  -- tsconfig.json: alias ja configurado")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()
    print(f"Aplicando correcoes em {raiz}")
    patch_layout(raiz)
    patch_tsconfig(raiz)
    print("OK")


if __name__ == "__main__":
    main()
