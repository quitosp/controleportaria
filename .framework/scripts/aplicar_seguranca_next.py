#!/usr/bin/env python3
"""Aplica seguranca em projeto Next.js:
- Security headers no next.config.mjs (HSTS, CSP, X-Frame, X-Content-Type, Referrer, Permissions)
- Helper de validacao de returnUrl (anti open-redirect)
- Sanitizacao opcional via DOMPurify (instala pacote)
- Verifica .env por NEXT_PUBLIC_* sensivel

Uso: python .framework/scripts/aplicar_seguranca_next.py --raiz <projeto> [--api-host https://api.exemplo.com] [--instalar-dompurify]
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

NEXT_CONFIG_TEMPLATE = '''/** @type {{import('next').NextConfig}} */

const securityHeaders = [
  {{ key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" }},
  {{ key: "X-Content-Type-Options", value: "nosniff" }},
  {{ key: "X-Frame-Options", value: "DENY" }},
  {{ key: "Referrer-Policy", value: "strict-origin-when-cross-origin" }},
  {{ key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" }},
  {{
    key: "Content-Security-Policy",
    value: [
      "default-src 'self'",
      "img-src 'self' data: https:",
      "script-src 'self' 'unsafe-inline'",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "font-src 'self' https://fonts.gstatic.com",
      "connect-src 'self' {api_host}",
      "frame-ancestors 'none'",
    ].join("; "),
  }},
];

const nextConfig = {{
  reactStrictMode: true,
  poweredByHeader: false,
  async headers() {{
    return [
      {{
        source: "/:path*",
        headers: securityHeaders,
      }},
    ];
  }},
}};

export default nextConfig;
'''

URL_VALIDATOR = '''export function urlEhSegura(returnUrl: string | null | undefined, hostsPermitidos: string[] = []): string {
  if (!returnUrl) return "/";
  try {
    if (returnUrl.startsWith("/") && !returnUrl.startsWith("//")) return returnUrl;
    const u = new URL(returnUrl);
    if (hostsPermitidos.includes(u.host)) return returnUrl;
  } catch { /* invalid url */ }
  return "/";
}

export function sanitizarHtmlSeguro(html: string): string {
  // Stub: instale DOMPurify para sanitizacao real
  // import DOMPurify from "isomorphic-dompurify";
  // return DOMPurify.sanitize(html);
  return html.replace(/<script[^>]*>[\\s\\S]*?<\\/script>/gi, "")
             .replace(/on\\w+="[^"]*"/gi, "")
             .replace(/javascript:/gi, "");
}
'''

def patch_next_config(raiz: Path, api_host: str) -> bool:
    for nome in ["next.config.mjs", "next.config.js", "next.config.ts"]:
        p = raiz / nome
        if not p.exists(): continue
        txt = p.read_text(encoding="utf-8")
        if "securityHeaders" in txt and "Strict-Transport-Security" in txt:
            print(f"  = {nome} ja tem security headers")
            return False
        # backup
        backup = p.with_suffix(p.suffix + ".bak")
        if not backup.exists(): backup.write_text(txt, encoding="utf-8")
        # sobrescreve com template novo
        novo = NEXT_CONFIG_TEMPLATE.format(api_host=api_host)
        p.write_text(novo, encoding="utf-8")
        print(f"+ {nome} atualizado (backup em {backup.name})")
        return True
    print("  AVISO: next.config nao encontrado")
    return False

def criar_url_validator(raiz: Path) -> bool:
    p = raiz / "src/compartilhados/lib/url-validator.ts"
    if p.exists():
        print(f"  = {p.relative_to(raiz)} ja existe")
        return False
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(URL_VALIDATOR, encoding="utf-8")
    print(f"+ src/compartilhados/lib/url-validator.ts (urlEhSegura, sanitizarHtmlSeguro)")
    return True

def auditar_env_publico(raiz: Path):
    sensiveis = ["SECRET", "TOKEN", "PASSWORD", "API_KEY", "PRIVATE", "JWT"]
    for nome in [".env", ".env.local", ".env.production", ".env.development"]:
        p = raiz / nome
        if not p.exists(): continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        for ln_num, ln in enumerate(txt.splitlines(), 1):
            if ln.startswith("#") or not ln.strip(): continue
            if "NEXT_PUBLIC_" in ln:
                up = ln.upper()
                for s in sensiveis:
                    if s in up:
                        print(f"  ALERTA {nome}:{ln_num} — NEXT_PUBLIC_*{s}* expoe ao cliente!")
                        break

def instalar_dompurify(raiz: Path):
    pkg = raiz / "package.json"
    if not pkg.exists(): return
    data = json.loads(pkg.read_text(encoding="utf-8"))
    if "isomorphic-dompurify" in data.get("dependencies", {}):
        print("  = isomorphic-dompurify ja instalado")
        return
    try:
        subprocess.run(["npm", "install", "isomorphic-dompurify"], cwd=raiz, check=True, timeout=180)
        print("  + isomorphic-dompurify instalado")
    except Exception as e:
        print(f"  AVISO: falha ao instalar isomorphic-dompurify ({e})")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--api-host", default="https://localhost:7219", help="connect-src do CSP")
    ap.add_argument("--instalar-dompurify", action="store_true")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()

    if not (raiz / "package.json").exists():
        print(f"ERRO: nao parece projeto Next.js em {raiz}"); sys.exit(2)

    print(f"Aplicando seguranca em {raiz}...\n")

    patch_next_config(raiz, args.api_host)
    criar_url_validator(raiz)

    print("\n--- Auditando NEXT_PUBLIC_* ---")
    auditar_env_publico(raiz)

    if args.instalar_dompurify:
        print("\n--- Instalando DOMPurify ---")
        instalar_dompurify(raiz)

    print("\nPROXIMOS PASSOS:")
    print(f"1. Ajustar CSP no next.config.mjs se usar fontes/imagens externas alem de Google Fonts")
    print(f"2. Adicionar dominios extras ao connect-src (api.com, analytics.com, etc)")
    print(f"3. Em paginas de redirect pos-login: importar urlEhSegura e validar returnUrl")
    print(f"4. Rodar: python .framework/scripts/verificar_seguranca.py --stack next")
    print(f"5. Testar headers em staging via securityheaders.com")
    print(f"6. npm run build && npm run start")

if __name__ == "__main__":
    main()
