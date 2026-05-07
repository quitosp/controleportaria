#!/usr/bin/env python3
"""Auditoria automatica de seguranca para projetos Framework.

Detecta:
- Backend C#: deps vulneraveis, secrets hardcoded, CORS frouxo, raw SQL, password policy fraca
- Frontend Next.js: deps vulneraveis, dangerouslySetInnerHTML, security headers ausentes, NEXT_PUBLIC_* sensivel
- Flutter: secret hardcoded, dependencias outdated

Uso: python .framework/scripts/verificar_seguranca.py [--raiz .] [--stack csharp|next|flutter|all]
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

# ============================ HELPERS ============================

class Achado:
    def __init__(self, severidade: str, categoria: str, mensagem: str, arquivo: str = "", linha: int = 0):
        self.severidade = severidade  # CRITICO | ALTO | MEDIO | INFO
        self.categoria = categoria
        self.mensagem = mensagem
        self.arquivo = arquivo
        self.linha = linha

    def __repr__(self):
        loc = f" ({self.arquivo}:{self.linha})" if self.arquivo else ""
        return f"[{self.severidade}] {self.categoria}: {self.mensagem}{loc}"

CRITICO, ALTO, MEDIO, INFO = "CRITICO", "ALTO", "MEDIO", "INFO"

def grep_lines(arquivo: Path, pattern: str, exclude: list[str] | None = None) -> list[tuple[int, str]]:
    if not arquivo.exists() or not arquivo.is_file(): return []
    try: txt = arquivo.read_text(encoding="utf-8", errors="replace")
    except Exception: return []
    out = []
    rx = re.compile(pattern)
    for i, ln in enumerate(txt.splitlines(), 1):
        if exclude and any(e in ln for e in exclude): continue
        if rx.search(ln): out.append((i, ln.strip()))
    return out

# ============================ BACKEND C# ============================

def auditar_csharp(raiz: Path) -> list[Achado]:
    achados = []
    api_dir = raiz / "servicos/api/Api"
    if not (raiz / "servicos/api/Api/Api.csproj").exists():
        return [Achado(INFO, "stack", "nao parece projeto C#-portaria, pulando")]

    # 1. Deps vulneraveis
    print("  -> dotnet list package --vulnerable...")
    try:
        r = subprocess.run(
            ["dotnet", "list", str(raiz), "package", "--vulnerable", "--include-transitive"],
            capture_output=True, text=True, timeout=120
        )
        if "no vulnerable packages" in r.stdout.lower() or "nenhum pacote vulneravel" in r.stdout.lower():
            pass
        elif "vulnerable" in r.stdout.lower() or "vulnera" in r.stdout.lower():
            for ln in r.stdout.splitlines():
                if ">" in ln and ("Critical" in ln or "High" in ln or "Moderate" in ln):
                    sev = CRITICO if "Critical" in ln else (ALTO if "High" in ln else MEDIO)
                    achados.append(Achado(sev, "deps-vulneraveis", ln.strip()))
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        achados.append(Achado(INFO, "deps-vulneraveis", f"nao foi possivel rodar dotnet list: {e}"))

    # 2. Connection string com secret hardcoded em arquivos commitaveis
    appsettings = api_dir / "appsettings.json"
    if appsettings.exists():
        txt = appsettings.read_text(encoding="utf-8")
        # password nao-trivial em appsettings.json e considerado risco (deveria ser env/user-secrets)
        m = re.search(r'"DefaultConnection"[^"]*"[^"]*Password=([^;"]+)', txt)
        if m and m.group(1) not in ("postgres", "trocar-em-producao"):
            achados.append(Achado(ALTO, "secret-hardcoded",
                f"Senha de DB visivel em appsettings.json. Use dotnet user-secrets ou env var.",
                "servicos/api/Api/appsettings.json"))
        # JWT secret hardcoded
        m = re.search(r'"AutenticacaoJwksUrl"|"Secret"\s*:\s*"([^"]{1,30})"', txt)
        # se houver algum "Secret" curto demais
        m2 = re.search(r'"Secret"\s*:\s*"([^"]+)"', txt)
        if m2 and len(m2.group(1)) < 32:
            achados.append(Achado(CRITICO, "jwt-secret-fraco",
                f"JWT Secret tem {len(m2.group(1))} chars. Minimo 32.",
                "servicos/api/Api/appsettings.json"))

    # 3. CORS frouxo + AllowCredentials
    for cfg in api_dir.rglob("*.cs"):
        for ln_num, ln in grep_lines(cfg, r"AllowAnyOrigin\(\)"):
            ja_tem = grep_lines(cfg, r"AllowCredentials")
            sev = CRITICO if ja_tem else ALTO
            achados.append(Achado(sev, "cors-frouxo",
                "AllowAnyOrigin() em producao expoe API. Use WithOrigins('https://...').",
                str(cfg.relative_to(raiz)), ln_num))
            break

    # 4. Raw SQL nao-parametrizado
    for cs in raiz.rglob("*.cs"):
        if "/obj/" in str(cs) or "/bin/" in str(cs): continue
        for ln_num, ln in grep_lines(cs, r"FromSqlRaw\([^@\{$]"):
            achados.append(Achado(CRITICO, "sql-injection",
                f"FromSqlRaw com string concatenada (suspeita SQL injection)",
                str(cs.relative_to(raiz)), ln_num))

    # 5. UseDeveloperExceptionPage sem checagem
    for cs in api_dir.rglob("*.cs"):
        for ln_num, ln in grep_lines(cs, r"UseDeveloperExceptionPage"):
            # busca se proximas 3 linhas tem IsDevelopment
            try: txt = cs.read_text(encoding="utf-8")
            except: continue
            linhas = txt.splitlines()
            antes = "\n".join(linhas[max(0,ln_num-3):ln_num])
            if "IsDevelopment" not in antes:
                achados.append(Achado(ALTO, "stack-trace-prod",
                    f"UseDeveloperExceptionPage sem checagem IsDevelopment expoe stack trace em prod",
                    str(cs.relative_to(raiz)), ln_num))
                break

    # 6. Password policy fraca
    for cs in api_dir.rglob("IdentityConfig.cs"):
        ach = grep_lines(cs, r"RequiredLength\s*=\s*1\b")
        if ach:
            achados.append(Achado(ALTO, "password-policy-fraca",
                "Password.RequiredLength = 1 ok em dev, mas alterar para >=8 em prod",
                str(cs.relative_to(raiz)), ach[0][0]))

    # 7. HSTS ausente
    cfg_files = list(api_dir.rglob("*.cs"))
    todo_txt = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in cfg_files if p.exists())
    if "UseHsts" not in todo_txt:
        achados.append(Achado(ALTO, "hsts-ausente",
            "app.UseHsts() nao encontrado. Necessario em prod (alem de UseHttpsRedirection)."))

    # 8. Rate limiting ausente
    if "AddRateLimiter" not in todo_txt and "UseRateLimiter" not in todo_txt:
        achados.append(Achado(MEDIO, "rate-limit-ausente",
            "Rate limiting nao configurado. Atacante pode brute-force o /entrar."))

    # 9. Security headers
    for h in ["X-Content-Type-Options", "X-Frame-Options", "Referrer-Policy", "Permissions-Policy"]:
        if h not in todo_txt and h.lower() not in todo_txt.lower():
            achados.append(Achado(MEDIO, "security-header",
                f"Header '{h}' nao encontrado em middleware."))

    return achados

# ============================ FRONTEND NEXT ============================

def auditar_next(raiz: Path) -> list[Achado]:
    achados = []
    pkg = raiz / "package.json"
    if not pkg.exists() or not (raiz / "next.config.mjs").exists() and not (raiz / "next.config.js").exists():
        return [Achado(INFO, "stack", "nao parece projeto Next.js, pulando")]

    # 1. npm audit
    print("  -> npm audit...")
    try:
        r = subprocess.run(["npm", "audit", "--omit=dev", "--json"],
                           cwd=raiz, capture_output=True, text=True, timeout=120)
        try: data = json.loads(r.stdout) if r.stdout else {}
        except json.JSONDecodeError: data = {}
        meta = data.get("metadata", {}).get("vulnerabilities", {})
        for sev_name, contagem in meta.items():
            if contagem == 0: continue
            sev = {"critical": CRITICO, "high": ALTO, "moderate": MEDIO, "low": INFO, "info": INFO}.get(sev_name.lower(), INFO)
            achados.append(Achado(sev, "deps-vulneraveis",
                f"npm audit: {contagem} vulnerabilidade(s) {sev_name}"))
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        achados.append(Achado(INFO, "deps-vulneraveis", f"nao foi possivel rodar npm audit: {e}"))

    # 2. dangerouslySetInnerHTML
    src = raiz / "src"
    if src.exists():
        for tsx in src.rglob("*.tsx"):
            for ln_num, ln in grep_lines(tsx, r"dangerouslySetInnerHTML"):
                achados.append(Achado(ALTO, "xss-risk",
                    "dangerouslySetInnerHTML pode permitir XSS. Sanitize com DOMPurify ou evite.",
                    str(tsx.relative_to(raiz)), ln_num))

    # 3. NEXT_PUBLIC_* com palavras suspeitas (secret, key, token, password)
    for env_file in [raiz / ".env", raiz / ".env.local", raiz / ".env.production"]:
        if not env_file.exists(): continue
        for ln_num, ln in grep_lines(env_file, r"NEXT_PUBLIC_.*(SECRET|TOKEN|PASSWORD|API_KEY|PRIVATE)", exclude=["#"]):
            achados.append(Achado(CRITICO, "secret-exposto",
                f"NEXT_PUBLIC_* nao deve ter SECRET/TOKEN/PASSWORD (vai pro bundle do cliente!)",
                str(env_file.relative_to(raiz)), ln_num))

    # 4. Security headers no next.config
    for cfg_name in ["next.config.mjs", "next.config.js", "next.config.ts"]:
        cfg = raiz / cfg_name
        if not cfg.exists(): continue
        txt = cfg.read_text(encoding="utf-8")
        if "headers" not in txt and "Strict-Transport-Security" not in txt:
            achados.append(Achado(ALTO, "security-headers-ausentes",
                "next.config nao define security headers (HSTS, CSP, X-Frame-Options, etc).",
                cfg_name))
        else:
            # checar headers especificos
            for h in ["Strict-Transport-Security", "X-Content-Type-Options", "X-Frame-Options", "Content-Security-Policy"]:
                if h not in txt:
                    achados.append(Achado(MEDIO, "security-header",
                        f"Header '{h}' nao encontrado em next.config", cfg_name))
        break

    # 5. Token storage em localStorage (info, mas vale alertar)
    api_ts = raiz / "src/compartilhados/servicos/api.ts"
    if api_ts.exists():
        if "localStorage.setItem" in api_ts.read_text(encoding="utf-8"):
            achados.append(Achado(MEDIO, "token-storage",
                "Tokens em localStorage estao vulneraveis a XSS. Considere httpOnly cookie + access token em memoria.",
                "src/compartilhados/servicos/api.ts"))

    # 6. eval / new Function
    if src.exists():
        for tsx in list(src.rglob("*.ts")) + list(src.rglob("*.tsx")):
            for ln_num, ln in grep_lines(tsx, r"\beval\(|new Function\("):
                achados.append(Achado(CRITICO, "code-injection",
                    "Uso de eval()/new Function() pode permitir code injection",
                    str(tsx.relative_to(raiz)), ln_num))

    return achados

# ============================ FLUTTER ============================

def auditar_flutter(raiz: Path) -> list[Achado]:
    achados = []
    if not (raiz / "pubspec.yaml").exists():
        return [Achado(INFO, "stack", "nao parece projeto Flutter, pulando")]

    # 1. Secrets hardcoded em .dart
    lib = raiz / "lib"
    if lib.exists():
        for dart in lib.rglob("*.dart"):
            for ln_num, ln in grep_lines(dart, r"(api[_-]?key|apikey|secret|password|token)\s*=\s*[\"'][A-Za-z0-9_\-]{16,}[\"']", exclude=["//"]):
                achados.append(Achado(CRITICO, "secret-hardcoded",
                    "Possivel secret hardcoded no codigo Dart. Use --dart-define ou envied.",
                    str(dart.relative_to(raiz)), ln_num))

    # 2. SharedPreferences guardando token (deve ser flutter_secure_storage)
    if lib.exists():
        for dart in lib.rglob("*.dart"):
            txt = dart.read_text(encoding="utf-8", errors="replace") if dart.is_file() else ""
            if "SharedPreferences" in txt and ("token" in txt.lower() or "jwt" in txt.lower()):
                achados.append(Achado(ALTO, "token-storage-inseguro",
                    "Token em SharedPreferences. Use flutter_secure_storage (Keychain/Keystore).",
                    str(dart.relative_to(raiz))))
                break

    # 3. HTTP em vez de HTTPS
    pubspec = raiz / "pubspec.yaml"
    if pubspec.exists():
        if lib.exists():
            for dart in lib.rglob("*.dart"):
                for ln_num, ln in grep_lines(dart, r'["\']http://[^/]+', exclude=["localhost", "127.0.0.1"]):
                    achados.append(Achado(ALTO, "http-inseguro",
                        "URL http:// em codigo Dart. Use https:// ou aceite so em dev.",
                        str(dart.relative_to(raiz)), ln_num))

    return achados

# ============================ MAIN ============================

def imprimir_relatorio(achados: list[Achado], stack: str):
    if not achados:
        print(f"\n[{stack}] OK: nenhum problema detectado.")
        return
    grupos = {CRITICO: [], ALTO: [], MEDIO: [], INFO: []}
    for a in achados: grupos.setdefault(a.severidade, []).append(a)
    print(f"\n=== [{stack}] {len(achados)} achados ===")
    for sev in [CRITICO, ALTO, MEDIO, INFO]:
        if not grupos[sev]: continue
        print(f"\n--- {sev} ({len(grupos[sev])}) ---")
        for a in grupos[sev]:
            loc = f"  ({a.arquivo}{':'+str(a.linha) if a.linha else ''})" if a.arquivo else ""
            print(f"  [{a.categoria}] {a.mensagem}{loc}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--stack", choices=["csharp", "next", "flutter", "all"], default="all")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()

    if not raiz.exists():
        print(f"ERRO: {raiz} nao existe"); sys.exit(2)

    print(f"Auditoria de seguranca em {raiz}\n")
    total = 0
    criticos = 0

    if args.stack in ("csharp", "all"):
        print("[backend C#]")
        achados = auditar_csharp(raiz)
        imprimir_relatorio(achados, "C#")
        total += len([a for a in achados if a.severidade != INFO])
        criticos += len([a for a in achados if a.severidade == CRITICO])

    if args.stack in ("next", "all"):
        print("\n[frontend Next]")
        # tenta diretorio irmao "*-web" se nao for o atual
        next_root = raiz
        if not (raiz / "package.json").exists():
            for sib in raiz.parent.glob("*-web"):
                if (sib / "package.json").exists():
                    next_root = sib
                    print(f"  (auditando projeto Next em {sib})")
                    break
        achados = auditar_next(next_root)
        imprimir_relatorio(achados, "Next")
        total += len([a for a in achados if a.severidade != INFO])
        criticos += len([a for a in achados if a.severidade == CRITICO])

    if args.stack in ("flutter", "all"):
        print("\n[mobile Flutter]")
        flutter_root = raiz
        if not (raiz / "pubspec.yaml").exists():
            for sib in raiz.parent.glob("*-mobile"):
                if (sib / "pubspec.yaml").exists():
                    flutter_root = sib
                    print(f"  (auditando projeto Flutter em {sib})")
                    break
        achados = auditar_flutter(flutter_root)
        imprimir_relatorio(achados, "Flutter")
        total += len([a for a in achados if a.severidade != INFO])
        criticos += len([a for a in achados if a.severidade == CRITICO])

    print(f"\n=== RESUMO: {total} achados ({criticos} CRITICOS) ===")
    if criticos > 0:
        print("Acao requerida antes de prod. Use:")
        print("  python .framework/scripts/aplicar_seguranca_csharp.py --raiz <projeto>")
        print("  python .framework/scripts/aplicar_seguranca_next.py --raiz <projeto>")
        sys.exit(1)

if __name__ == "__main__":
    main()
