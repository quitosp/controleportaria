#!/usr/bin/env python3
"""Migra tipos legados de historias para os 8 tipos novos (capacidades).

Mapeamento:
  infra        -> architecture
  agregado     -> crud
  feature      -> crud
  tela         -> crud
  refatoracao  -> refactor
  bug          -> refactor

Tambem garante que cada historia tenha o bloco `artefato`. Para tipo != crud/architecture,
deixa `artefato.tipo_artefato` em branco para o usuario decidir e rodar /artefato HIST-NNN.

Uso:
  python .framework/scripts/migrar_tipos.py [--raiz .] [--dry-run]
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

MAPA = {
    "infra": "architecture",
    "agregado": "crud",
    "feature": "crud",
    "tela": "crud",
    "refatoracao": "refactor",
    "bug": "refactor",
}

def migrar_arquivo(path: Path, dry_run: bool) -> tuple[bool, str]:
    """Retorna (mudou, motivo)."""
    txt = path.read_text(encoding="utf-8")
    novo = txt
    motivos = []

    # 1. Converter tipo legado
    m = re.search(r'^tipo:\s*(\w+)', novo, re.MULTILINE)
    if m and m.group(1) in MAPA:
        legado = m.group(1)
        novo_tipo = MAPA[legado]
        novo = re.sub(rf'^tipo:\s*{legado}\s*$', f'tipo: {novo_tipo}', novo, flags=re.MULTILINE)
        motivos.append(f"tipo {legado}->{novo_tipo}")

    # 2. Adicionar bloco artefato se nao existe
    if "artefato:" not in novo:
        # detectar tipo apos eventual conversao
        m_tipo = re.search(r'^tipo:\s*(\S+)', novo, re.MULTILINE)
        tipo = m_tipo.group(1) if m_tipo else "crud"

        # Se tipo crud/architecture, artefato pode ficar com defaults vazios (nao bloqueia)
        # Se outro tipo, tipo_artefato fica vazio para o /artefato decidir
        bloco = (
            "\n# Gate de aprovacao (gerado por migrar_tipos.py)\n"
            "artefato:\n"
            "  tipo_artefato: \"\"\n"
            "  caminho: \"\"\n"
            f"  aprovado: {'true' if tipo in ('crud','architecture') else 'false'}\n"
            "  aprovado_em: \"\"\n"
        )
        # inserir antes de "aceite:" ou "validacao:" ou no final
        if re.search(r'^aceite:', novo, re.MULTILINE):
            novo = re.sub(r'^(aceite:)', bloco + r"\n\1", novo, count=1, flags=re.MULTILINE)
        elif re.search(r'^validacao:', novo, re.MULTILINE):
            novo = re.sub(r'^(validacao:)', bloco + r"\n\1", novo, count=1, flags=re.MULTILINE)
        else:
            novo += bloco
        motivos.append("bloco artefato adicionado")

    if novo != txt and not dry_run:
        path.write_text(novo, encoding="utf-8")

    return novo != txt, ", ".join(motivos)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--dry-run", action="store_true", help="so reporta sem alterar")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()
    historias = raiz / ".framework/estado/historias"
    if not historias.exists():
        print(f"ERRO: {historias} nao existe"); sys.exit(2)

    files = sorted(historias.glob("HIST-*.yaml"))
    if not files:
        print("Nenhuma historia encontrada."); return

    mudados = 0
    print(f"{'[DRY RUN] ' if args.dry_run else ''}Analisando {len(files)} historias...\n")
    for f in files:
        mudou, motivo = migrar_arquivo(f, args.dry_run)
        if mudou:
            print(f"  {f.name}: {motivo}")
            mudados += 1
        else:
            print(f"  {f.name}: ja atualizada")

    print(f"\n{mudados} arquivo(s) {'seriam alterados' if args.dry_run else 'alterados'}.")
    if args.dry_run:
        print("Para aplicar: rode sem --dry-run")

if __name__ == "__main__":
    main()
