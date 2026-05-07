#!/usr/bin/env python3
"""Atualiza o template interno .framework/templates/csharp-core/ a partir de uma copia de
Portaria-master mais recente. Usa as mesmas whitelists do copiar_core_base.py.

Uso: python .framework/scripts/atualizar_csharp_core.py --portaria <path-de-portaria-master>

Quando usar:
- Voce atualizou Portaria-master localmente e quer trazer essas mudancas para o template interno
- Mudou um arquivo do Core que precisa propagar para projetos novos
- NAO usar para mudancas de projetos especificos — esses ficam no projeto, nao no template
"""
from __future__ import annotations
import argparse, shutil, sys
from pathlib import Path

# importa whitelists do copiar_core_base
sys.path.insert(0, str(Path(__file__).parent))
import copiar_core_base as ccb

DEST = Path(__file__).parent.parent / "templates/csharp-core"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--portaria", required=True, help="caminho de Portaria-master para sincronizar")
    ap.add_argument("--dry-run", action="store_true", help="so lista o que seria copiado")
    args = ap.parse_args()

    portaria = Path(args.portaria).resolve()
    if not portaria.exists():
        print(f"ERRO: {portaria} nao existe"); sys.exit(2)

    if not args.dry_run:
        DEST.mkdir(parents=True, exist_ok=True)

    core_src = portaria / "compartilhados/core/Core"
    web_src = portaria / "compartilhados/webApi.core/WebApi.Core"
    api_src = portaria / "servicos/api/Api"

    arquivos = []
    for rel in ccb.CORE_WHITELIST:
        src = core_src / rel
        if src.exists(): arquivos.append((src, DEST / "compartilhados/core/Core" / rel))
    for rel in ccb.WEBAPI_WHITELIST:
        src = web_src / rel
        if src.exists(): arquivos.append((src, DEST / "compartilhados/webApi.core/WebApi.Core" / rel))
    for rel in ["Configuration/IdentityConfig.cs", "Configuration/SwaggerConfig.cs",
                "Identidade/Servicos/AuthenticationService.cs",
                "Identidade/Extensions/IdentityMensagensPortugues.cs"]:
        src = api_src / rel
        if src.exists(): arquivos.append((src, DEST / "servicos/api/Api" / rel))

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Sincronizando {len(arquivos)} arquivos\n")
    for src, dst in arquivos:
        rel_str = str(dst.relative_to(DEST))
        if args.dry_run:
            print(f"  {rel_str}")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  + {rel_str}")

    if args.dry_run:
        print(f"\nDry run. Para aplicar: rode sem --dry-run")
        return

    # Patch IdentityConfig SqlServer -> Npgsql
    ic = DEST / "servicos/api/Api/Configuration/IdentityConfig.cs"
    if ic.exists():
        txt = ic.read_text(encoding="utf-8")
        if "UseSqlServer" in txt:
            txt = txt.replace("UseSqlServer", "UseNpgsql")
            ic.write_text(txt, encoding="utf-8")
            print(f"  ~ IdentityConfig.cs: SqlServer -> Npgsql")

    print(f"\nOK template atualizado em {DEST}")
    print(f"Projetos novos via novo_projeto.py vao usar essa versao automaticamente.")

if __name__ == "__main__":
    main()
