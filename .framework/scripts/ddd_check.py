"""
Detecta agregados anemicos e logica que deveria estar no agregado.
Uso: python ddd_check.py [--raiz .]
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()

    dom_dir = raiz / "dominios/Dominios"
    if not dom_dir.exists():
        # tenta api/dominios
        dom_dir = raiz / "api/dominios/Dominios"
    if not dom_dir.exists():
        print("AVISO: dominios/Dominios nao encontrado, pulando")
        sys.exit(0)

    issues = []

    # 1. Anemicos
    for ent_dir in dom_dir.glob("*/Entidades"):
        for cs in ent_dir.glob("*.cs"):
            txt = cs.read_text(encoding="utf-8", errors="replace")
            # contar propriedades public T X { get; set; } (anemicas)
            props_anemicas = len(re.findall(r'^\s*public\s+\w[\w<>?,\s]*\s+\w+\s*{\s*get;\s*set;\s*}', txt, re.MULTILINE))
            # contar metodos publicos (nao construtor, nao properties)
            metodos = len(re.findall(r'^\s*public\s+(?!class\b|partial\b|static\s+class\b)(?:async\s+)?(?:Task<?\w*>?\s+|void\s+|\w[\w<>]*\s+)(\w+)\s*\([^)]*\)', txt, re.MULTILINE))
            # excluir construtor (mesmo nome da classe)
            nome_classe = cs.stem
            metodos_construtor = len(re.findall(rf'^\s*public\s+{nome_classe}\s*\(', txt, re.MULTILINE))
            metodos_efetivos = max(0, metodos - metodos_construtor)

            if metodos_efetivos == 0 and props_anemicas >= 3:
                issues.append((
                    "ANEMICO",
                    str(cs.relative_to(raiz)),
                    f"{props_anemicas} propriedades, 0 metodos de comportamento. "
                    f"Se {nome_classe} tem regras de negocio, considere extrair logica de Handler para {nome_classe}.MetodoX()."
                ))

    # 2. Logica em Handler que muta agregados
    handlers_dirs = [
        raiz / "dominios/Dominios",
        raiz / "api/dominios/Dominios",
    ]
    for hdir in handlers_dirs:
        if not hdir.exists(): continue
        for handler in hdir.rglob("*Handler.cs"):
            txt = handler.read_text(encoding="utf-8", errors="replace")
            # procurar blocos com >= 3 atribuicoes seguidas a propriedades de uma var
            # padrao: var x = ...; depois 3+ x.Y = ...
            # heuristica simples: 3 ou mais "<algo>.<Prop> = " consecutivos
            for m in re.finditer(r'(\w+)\.\w+\s*=\s*[^;]+;\s*(?:\1\.\w+\s*=\s*[^;]+;\s*){2,}', txt):
                linha = txt[:m.start()].count("\n") + 1
                issues.append((
                    "LOGICA-NO-HANDLER",
                    f"{handler.relative_to(raiz)}:{linha}",
                    f"Multiplas mutacoes consecutivas em '{m.group(1)}' — considere encapsular em metodo do agregado"
                ))

    if not issues:
        print("OK nenhum problema DDD detectado")
        sys.exit(0)

    # ordem: anemico primeiro
    issues.sort(key=lambda x: 0 if x[0] == "ANEMICO" else 1)
    for tag, loc, msg in issues:
        print(f"[{tag}]  {msg}")
        print(f"        ({loc})")
    print(f"\n{len(issues)} possiveis melhorias DDD")
    print("Nota: ANEMICO em agregados de cadastro puro (Categoria, Tag) e aceitavel — ignore nesses casos.")


if __name__ == "__main__":
    main()
