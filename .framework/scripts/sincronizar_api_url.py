"""
Sincroniza NEXT_PUBLIC_API_URL do(s) frontend(s) com a URL real da API .NET.

Uso:
  py sincronizar_api_url.py                       # auto: detecta API e frontends a partir do CWD
  py sincronizar_api_url.py --api <path-api-csproj-dir>
  py sincronizar_api_url.py --front <path-frontend-dir>
  py sincronizar_api_url.py --preferir http       # default: https
  py sincronizar_api_url.py --raiz <pasta-base>   # default: CWD; sobe ate achar irmao com Api/

Comportamento:
  1. Acha launchSettings.json (Api/Properties/launchSettings.json)
  2. Extrai URL do profile https (ou http se --preferir http)
  3. Acha frontends: pasta atual e irmaos contendo package.json com "next"
  4. Cria/atualiza .env.local:  NEXT_PUBLIC_API_URL=<url>
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path


def achar_launch_settings(raiz: Path) -> Path | None:
    candidatos = list(raiz.rglob("Properties/launchSettings.json"))
    candidatos = [c for c in candidatos if "node_modules" not in c.parts and "bin" not in c.parts and "obj" not in c.parts]
    if not candidatos:
        return None
    # priorizar o que tem "Api" no caminho
    com_api = [c for c in candidatos if "Api" in c.parts or "api" in c.parts]
    return com_api[0] if com_api else candidatos[0]


def extrair_url(launch_settings: Path, preferir: str) -> str | None:
    try:
        dados = json.loads(launch_settings.read_text(encoding="utf-8-sig"))
    except Exception as e:
        print(f"FALHA ao ler {launch_settings}: {e}")
        return None

    profiles = dados.get("profiles", {})
    profile = profiles.get(preferir) or profiles.get("https") or profiles.get("http")
    if not profile:
        for nome, p in profiles.items():
            if isinstance(p, dict) and p.get("applicationUrl"):
                profile = p
                break
    if not profile:
        return None

    urls = profile.get("applicationUrl", "")
    if not urls:
        return None

    candidatas = [u.strip() for u in urls.split(";") if u.strip()]
    if preferir == "http":
        for u in candidatas:
            if u.startswith("http://"):
                return u
    for u in candidatas:
        if u.startswith("https://"):
            return u
    return candidatas[0] if candidatas else None


def eh_frontend_next(pasta: Path) -> bool:
    pkg = pasta / "package.json"
    if not pkg.is_file():
        return False
    try:
        dados = json.loads(pkg.read_text(encoding="utf-8"))
    except Exception:
        return False
    deps = {**dados.get("dependencies", {}), **dados.get("devDependencies", {})}
    return "next" in deps


def achar_frontends(raiz: Path) -> list[Path]:
    """Prefere casar pelo nome: <projeto> -> <projeto>-web. Senao, frontend embutido."""
    achados: list[Path] = []
    if eh_frontend_next(raiz):
        achados.append(raiz)

    pai = raiz.parent
    if pai and pai.exists():
        nome_par = f"{raiz.name}-web"
        candidato = pai / nome_par
        if candidato.is_dir() and eh_frontend_next(candidato):
            achados.append(candidato)
            return achados
        # fallback: irmao com -web no nome
        for irmao in pai.iterdir():
            if irmao.is_dir() and irmao != raiz and irmao.name.endswith("-web") and eh_frontend_next(irmao):
                if irmao.name.startswith(raiz.name) or raiz.name.startswith(irmao.name.removesuffix("-web")):
                    achados.append(irmao)
    return achados


def atualizar_env_local(front: Path, url: str) -> tuple[bool, str]:
    env = front / ".env.local"
    nova_linha = f"NEXT_PUBLIC_API_URL={url}"
    if not env.is_file():
        env.write_text(nova_linha + "\n", encoding="utf-8")
        return True, "criado"

    conteudo = env.read_text(encoding="utf-8")
    if re.search(r"^NEXT_PUBLIC_API_URL=.*$", conteudo, flags=re.MULTILINE):
        antigo = re.search(r"^NEXT_PUBLIC_API_URL=(.*)$", conteudo, flags=re.MULTILINE).group(1).strip()
        if antigo == url:
            return False, "ja sincronizado"
        novo = re.sub(r"^NEXT_PUBLIC_API_URL=.*$", nova_linha, conteudo, flags=re.MULTILINE)
        env.write_text(novo, encoding="utf-8")
        return True, f"atualizado ({antigo} -> {url})"
    if not conteudo.endswith("\n"):
        conteudo += "\n"
    env.write_text(conteudo + nova_linha + "\n", encoding="utf-8")
    return True, "adicionado"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=os.getcwd())
    ap.add_argument("--api", default=None, help="pasta do projeto Api (contem Properties/launchSettings.json)")
    ap.add_argument("--front", default=None, help="forcar pasta especifica do frontend")
    ap.add_argument("--preferir", choices=["http", "https"], default="https")
    args = ap.parse_args()

    raiz = Path(args.raiz).resolve()

    if args.api:
        ls_path = Path(args.api).resolve() / "Properties" / "launchSettings.json"
    else:
        ls_path = achar_launch_settings(raiz) or (achar_launch_settings(raiz.parent) if raiz.parent != raiz else None)

    if not ls_path or not ls_path.is_file():
        print("FALHA: launchSettings.json nao encontrado")
        sys.exit(1)

    url = extrair_url(ls_path, args.preferir)
    if not url:
        print(f"FALHA: nao consegui extrair URL de {ls_path}")
        sys.exit(1)

    print(f"-> API detectada: {url}")
    print(f"   (de {ls_path.relative_to(raiz.parent if raiz.parent.exists() else raiz)})")

    if args.front:
        fronts = [Path(args.front).resolve()]
    else:
        fronts = achar_frontends(raiz)

    if not fronts:
        print("Nenhum frontend Next.js encontrado (procurei em " + str(raiz) + " e irmaos)")
        sys.exit(0)

    for f in fronts:
        mudou, msg = atualizar_env_local(f, url)
        marca = "OK" if mudou else "--"
        print(f"   {marca} {f.name}/.env.local: {msg}")


if __name__ == "__main__":
    main()
