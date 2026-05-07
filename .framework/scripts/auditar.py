"""
Auditoria de seguranca + LGPD sobre o codigo C#.
Uso: python auditar.py [--raiz .]
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

CRITICO, ALTO, MEDIO, BAIXO = "CRITICO", "ALTO", "MEDIO", "BAIXO"
SENSIVEIS = ["cpf", "senha", "password", "token", "apikey", "api_key", "creditcard", "rg"]


class Issue:
    def __init__(self, sev, regra, msg, arq, linha=0):
        self.sev = sev; self.regra = regra; self.msg = msg; self.arq = arq; self.linha = linha


def grep_lines(arq: Path, pattern: str):
    if not arq.is_file(): return []
    try: txt = arq.read_text(encoding="utf-8", errors="replace")
    except Exception: return []
    return [(i, ln.strip()) for i, ln in enumerate(txt.splitlines(), 1) if re.search(pattern, ln, re.IGNORECASE)]


def auditar(raiz: Path) -> list[Issue]:
    out: list[Issue] = []
    IGNORAR = ("bin", "obj", "Migrations", "node_modules", "temp-build", ".next")
    cs_files = [f for f in raiz.rglob("*.cs") if not any(p in f.parts for p in IGNORAR)]

    # 1. LGPD: logs com dados sensiveis
    for f in cs_files:
        try: txt = f.read_text(encoding="utf-8", errors="replace")
        except: continue
        for i, ln in enumerate(txt.splitlines(), 1):
            if any(re.search(rf'_log\.\w+\([^)]*\b{s}\b', ln, re.IGNORECASE) for s in SENSIVEIS):
                out.append(Issue(ALTO, "log-com-dados-sensiveis",
                    f"Log pode estar registrando dado sensivel — mascarar antes",
                    str(f.relative_to(raiz)), i))

    # 2. Endpoints sem [Authorize] em controllers (exceto Auth/Health/Webhook)
    # Webhooks usam validacao alternativa (HMAC, ApiKey) — nao sao bug
    for f in cs_files:
        if "Controller.cs" not in f.name: continue
        if "Auth" in f.name or "Health" in f.name or "Webhook" in f.name: continue
        try: txt = f.read_text(encoding="utf-8", errors="replace")
        except: continue
        if "[AllowAnonymous]" in txt and "[Authorize]" not in txt:
            out.append(Issue(CRITICO, "controller-sem-authorize",
                f"{f.name} usa [AllowAnonymous] mas nao tem [Authorize] base",
                str(f.relative_to(raiz))))

    # 3. Saidas com campos sensiveis
    for f in cs_files:
        if "Saida" not in f.name: continue
        try: txt = f.read_text(encoding="utf-8", errors="replace")
        except: continue
        for i, ln in enumerate(txt.splitlines(), 1):
            for s in ("Senha", "Password", "Token", "ApiKey"):
                if re.search(rf'\bpublic\s+\w+\s+{s}\b', ln) and "[JsonIgnore]" not in txt:
                    out.append(Issue(ALTO, "saida-com-campo-sensivel",
                        f"Saida expoe campo {s} sem [JsonIgnore]",
                        str(f.relative_to(raiz)), i))

    # 4. AllowAnyOrigin em prod
    for f in cs_files:
        for ln_num, ln in grep_lines(f, r"AllowAnyOrigin\(\)"):
            out.append(Issue(MEDIO, "cors-aberto",
                "AllowAnyOrigin() — usar SetIsOriginAllowed para producao",
                str(f.relative_to(raiz)), ln_num))

    # 5. Secrets hardcoded
    for f in [*cs_files, *raiz.rglob("appsettings*.json")]:
        if any(p in f.parts for p in IGNORAR): continue
        try: txt = f.read_text(encoding="utf-8", errors="replace")
        except: continue
        for i, ln in enumerate(txt.splitlines(), 1):
            # senha hardcoded em ConnectionString diferente do default postgres/postgres
            m = re.search(r'Password=([^;"\s]+)', ln)
            if m and m.group(1) not in ("postgres", "Admin@123"):
                out.append(Issue(BAIXO, "senha-hardcoded",
                    f"ConnectionString com senha em texto — considere User Secrets",
                    str(f.relative_to(raiz)), i))
            if re.search(r'\b(api_?key|jwt_?secret)\s*[:=]\s*["\'][a-zA-Z0-9_\-]{20,}', ln, re.IGNORECASE):
                out.append(Issue(ALTO, "secret-hardcoded",
                    "API key / secret hardcoded — mover para User Secrets ou env var",
                    str(f.relative_to(raiz)), i))

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()

    issues = auditar(raiz)
    if not issues:
        print("OK auditoria limpa")
        sys.exit(0)

    issues.sort(key=lambda x: ["CRITICO", "ALTO", "MEDIO", "BAIXO"].index(x.sev))
    for i in issues:
        loc = f"{i.arq}:{i.linha}" if i.linha else i.arq
        print(f"[{i.sev}] {i.regra}: {i.msg}  ({loc})")

    n_crit = sum(1 for i in issues if i.sev == "CRITICO")
    n_alto = sum(1 for i in issues if i.sev == "ALTO")
    print(f"\nResumo: {len(issues)} issues ({n_crit} CRITICO, {n_alto} ALTO)")
    sys.exit(1 if n_crit > 0 else 0)


if __name__ == "__main__":
    main()
