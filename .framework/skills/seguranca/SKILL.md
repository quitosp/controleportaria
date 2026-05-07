---
name: seguranca
description: Skill de seguranca para backend (.NET API) e frontend (Next.js + Flutter). Cobre OWASP Top 10, auth/JWT, validacao input, secrets, headers, CORS, rate limiting, deps vulneraveis, XSS, CSRF, token storage, CSP. Comandos: auditoria automatica + scripts que aplicam configuracoes seguras. Triggers: "/seguranca", "auditar seguranca", "checklist seguranca", "aplicar headers de seguranca", "rate limit", "csp", "owasp".
---

# Skill: seguranca

Auditoria + aplicacao de boas praticas de seguranca em projetos do framework. Cobre as 3 stacks: API .NET (csharp-portaria), frontend Next.js (frontend-react), mobile Flutter (flutter-mobile).

## Quando aplicar

**Sempre antes de:**
- Deploy em producao
- Expor API publicamente
- Adicionar feature que lida com dados sensiveis (auth, pagamento, saude, PII)
- Aceitar uploads de arquivo
- Integrar com terceiros (webhooks, OAuth)

**Recomendado:**
- Quinzenalmente em projetos ativos (rodar auditoria)
- Ao adicionar nova dependencia
- Antes de merge de PR critico
- Apos incidente / alert de CVE

**Pule:**
- POC local sem dados reais
- Documentacao
- Refatoracao puramente cosmetica

## Categorias por prioridade (OWASP-aligned)

| # | Categoria | Impacto | Stacks afetadas | Acao |
|---|-----------|---------|------------------|------|
| 1 | Broken Authentication | CRITICO | backend + frontend | Identity policies, JWT seguro, refresh rotation |
| 2 | Injecao (SQL, command, log) | CRITICO | backend | EF parametrizado, validar input, sanitizar logs |
| 3 | Cryptographic Failures | CRITICO | backend + frontend | HTTPS only, JWT secret >=32 chars, hash de senha (Identity ja faz) |
| 4 | Broken Access Control | CRITICO | backend | `[Authorize]` + RBAC roles, IDOR check |
| 5 | Security Misconfiguration | ALTO | todas | Headers, CORS, dotnet user-secrets, env vars |
| 6 | Vulnerable Dependencies | ALTO | todas | `dotnet list package --vulnerable`, `npm audit` |
| 7 | XSS / CSP | ALTO | frontend | React escapa por default, CSP no next.config, evitar dangerouslySetInnerHTML |
| 8 | Sensitive Data Exposure | ALTO | todas | Nao logar tokens/senhas, nao expor stack trace em prod |
| 9 | Security Logging | MEDIO | backend | Audit trail de login, mudanca de role, exclusao |
| 10 | SSRF / Server-Side Forgery | MEDIO | backend | Validar URLs externas antes de fetch |

## Comandos disponiveis

### Auditoria automatica (passive — so reporta)
```bash
python .framework/scripts/verificar_seguranca.py [--raiz .] [--stack csharp|next|all]
```
Roda:
- `dotnet list package --vulnerable --include-transitive`
- `npm audit --omit=dev` (se Next)
- Grep por padroes inseguros (raw SQL, dangerouslySetInnerHTML, AllowAnyOrigin com credentials, secret hardcoded)
- Verifica appsettings tem secret >=32 chars
- Verifica next.config tem security headers
- Verifica CORS especifico (nao AllowAny em producao)

Saida: relatorio com criticos / altos / medios / sugestoes.

### Aplicar configuracoes seguras (active — modifica codigo)
```bash
# Backend C#: rate limiting, HSTS, security headers, audit logging
python .framework/scripts/aplicar_seguranca_csharp.py --raiz <projeto>

# Frontend Next.js: CSP, HSTS, headers, env check, CSRF helper
python .framework/scripts/aplicar_seguranca_next.py --raiz <projeto>
```

## Backend (.NET API) — checklist

### Authentication & Tokens
- [ ] `IdentityOptions.Password.RequiredLength >= 8` (mudar de 1 default em prod)
- [ ] `Password.RequireDigit/Lowercase/Uppercase/NonAlphanumeric = true` em prod
- [ ] `Lockout.MaxFailedAccessAttempts <= 5`, `Lockout.DefaultLockoutTimeSpan = 15min`
- [ ] JWT secret >=32 chars, em variavel de ambiente, NUNCA no repo
- [ ] JWT expira em <=8h
- [ ] Refresh token rotation (revogar antigo ao usar)
- [ ] Refresh token armazenado em HttpOnly cookie (preferivel) ou storage seguro
- [ ] `EmailConfirmed = true` so via flow valido (nao auto-true em registro publico)

### Authorization
- [ ] `[Authorize]` em todos controllers de dominio (ou em base controller)
- [ ] `[AllowAnonymous]` explicito apenas em login/registro
- [ ] RBAC: `[Authorize(Roles = "...")]` quando aplicavel
- [ ] IDOR: usuario A nao pode ler/editar recurso de usuario B (validar ownership no handler)

### Input Validation
- [ ] FluentValidation em TODOS commands (`EhValido()`)
- [ ] Tamanhos maximos em strings (varchar com limite)
- [ ] Email valido, telefone formato, regex em campos com formato fixo
- [ ] Nao aceitar deserializacao de tipos arbitrarios

### SQL & EF
- [ ] Usar so EF LINQ (parametriza automaticamente)
- [ ] Se usar `FromSqlRaw`, sempre com parametros (`{0}`, `@p`)
- [ ] `Migrations/` versionadas, nunca aplicar migrations automaticamente em prod sem aprovacao

### Configuration
- [ ] `appsettings.Production.json` NAO commitado se tem secrets
- [ ] `dotnet user-secrets` em dev
- [ ] Env vars / Key Vault em prod
- [ ] Connection string sem `Trust Server Certificate=true` em prod

### CORS
- [ ] Substituir `AllowAnyOrigin()` por `WithOrigins("https://meudominio.com")` em prod
- [ ] Nao usar `AllowAnyOrigin() + AllowCredentials()` (browser bloqueia)

### Headers (HSTS, X-Frame, X-Content-Type)
- [ ] `app.UseHsts()` em prod
- [ ] `app.UseHttpsRedirection()`
- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY
- [ ] Referrer-Policy: strict-origin-when-cross-origin
- [ ] Permissions-Policy: minimo necessario

### Rate Limiting
- [ ] AspNetCore RateLimiter no /entrar (5 tentativas / 15min por IP)
- [ ] Limite global: 100 req/min por IP
- [ ] Aplicar limite separado em endpoints caros

### Logging seguro
- [ ] NUNCA logar senha, JWT, refresh token, CPF/CNPJ completo
- [ ] Audit log: login, logout, mudanca de role, exclusoes
- [ ] Stack trace nao exposto em prod (`UseDeveloperExceptionPage` so em dev)

### Dependencias
- [ ] Rodar `dotnet list package --vulnerable --include-transitive` periodicamente
- [ ] Atualizar pacotes Identity / Npgsql / NetDevPack quando houver CVE

## Frontend (Next.js) — checklist

### Security Headers (next.config.mjs)
```js
const securityHeaders = [
  { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
  { key: "Content-Security-Policy", value: "default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; connect-src 'self' https://localhost:7219;" },
];
```
- [ ] HSTS ativo em producao
- [ ] CSP minima funcional (ajustar para fontes/imagens externas usadas)
- [ ] X-Frame-Options DENY (evita clickjacking)

### Token Storage
- [ ] Decidir conscientemente: localStorage (XSS risk) OU httpOnly cookie (CSRF risk)
- [ ] **Recomendado**: refresh token em httpOnly cookie, access token em memoria (Zustand/React state)
- [ ] Se usar localStorage: garantir CSP forte e zero `dangerouslySetInnerHTML`

### XSS Prevention
- [ ] React escapa por default — NUNCA usar `dangerouslySetInnerHTML` com input do usuario
- [ ] Se precisar render HTML do usuario: sanitizar com DOMPurify
- [ ] Validar URLs antes de `<a href>` (evitar `javascript:`)

### CSRF (so se usar cookies httpOnly)
- [ ] Token CSRF anti-forgery sincronizado em forms
- [ ] SameSite=Lax ou Strict no cookie

### Input Validation
- [ ] Zod em todo formulario (ja gerado pelo `frontend_scaffold.py`)
- [ ] Validacao client = UX, validacao server = seguranca (ambas obrigatorias)

### Env Vars
- [ ] **NUNCA** colocar secret em `NEXT_PUBLIC_*` (vai pro bundle do cliente)
- [ ] Vars com `NEXT_PUBLIC_` so para urls publicas / IDs nao-secretos
- [ ] Secrets reais sempre em server actions / API routes (sem prefix)

### Dependencias
- [ ] `npm audit --omit=dev` periodicamente
- [ ] Atualizar Next.js, React, axios quando houver CVE

### Open Redirects
- [ ] Apos login, validar `returnUrl` esta no mesmo dominio antes de redirect
- [ ] Whitelist de hosts permitidos

### Auth flow
- [ ] Logout: limpar token (localStorage + cookie + redirect)
- [ ] Token expirado: interceptor redireciona pra /login (ja implementado em api.ts)
- [ ] Rotas privadas: middleware checa token (ja implementado)

## Mobile (Flutter) — checklist

### Token Storage
- [ ] `flutter_secure_storage` (Keychain iOS / Keystore Android) — NUNCA SharedPreferences
- [ ] Refresh token + access token ambos no secure storage

### HTTPS
- [ ] Todas requisicoes via HTTPS
- [ ] Certificate pinning em apps com dados sensiveis (financeiro, saude)
- [ ] Aceitar so TLS 1.2+

### Build
- [ ] `flutter build apk --release --obfuscate --split-debug-info=...` (ofuscar codigo)
- [ ] Disable debug logs em release
- [ ] ProGuard / R8 ativo (Android)

### Permissions
- [ ] Pedir permissoes minimas necessarias
- [ ] Justificar uso (especialmente camera, localizacao, contatos)
- [ ] iOS: Info.plist com NSCameraUsageDescription etc
- [ ] Android: declarar so as permissoes usadas

### Deep links
- [ ] Validar deep link parameters antes de usar
- [ ] iOS: Universal Links com associated domains
- [ ] Android: App Links com signed manifest

### Secrets
- [ ] Nao hardcodar API keys no codigo Dart
- [ ] Usar `--dart-define` ou env files (envied package)

### Dependencias
- [ ] `flutter pub outdated` periodicamente
- [ ] Atualizar quando houver CVE

## Pre-deploy checklist

Antes de cada deploy producao:

**Backend**
- [ ] Auditoria: `python .framework/scripts/verificar_seguranca.py --stack csharp` sem criticos
- [ ] Connection string em env var (nao no appsettings.json commitado)
- [ ] JWT secret unica por ambiente (rotaciona se vazou)
- [ ] CORS limitado aos dominios reais
- [ ] HSTS ativo
- [ ] Rate limiting no /entrar
- [ ] `UseDeveloperExceptionPage` so em IsDevelopment
- [ ] Logs nao contem dados sensiveis (revisar amostra)
- [ ] Dependencias auditadas

**Frontend**
- [ ] `npm audit --omit=dev` sem high/critical
- [ ] `next build` sem erros
- [ ] Security headers no next.config (testar via securityheaders.com em staging)
- [ ] CSP funcional (sem 'unsafe-eval' em prod)
- [ ] NEXT_PUBLIC_* nao expoe nada secreto
- [ ] localStorage nao guarda dados sensiveis alem de tokens (que ainda assim vulneraveis a XSS)

## Integracao com outras skills

- `criar-prd` ja tem perguntas sobre auth + roles que afetam seguranca
- `csharp-novo-agregado` gera handlers com FluentValidation embutido (preventivo)
- `frontend_scaffold.py` gera form com Zod (preventivo)
- `criar-rbac` aplica policies que esta skill verifica
- `auth_scaffold.py` gera auth com Identity (defaults seguros, mas Production exige reforco)

## Restricoes
- NAO aplicar `aplicar_seguranca_*.py` sem revisar diff (modifica config sensivel)
- NAO desabilitar HSTS em prod
- NAO usar `AllowAnyOrigin` + `AllowCredentials` (browser bloqueia)
- SEMPRE usar `dotnet user-secrets` em dev, env vars em prod
- SEMPRE rodar auditoria antes de deploy
- NAO logar nada sensivel — quando em duvida, redact

## Recursos
- OWASP Top 10: https://owasp.org/Top10/
- ASP.NET Core security best practices: https://learn.microsoft.com/en-us/aspnet/core/security/
- Next.js security headers: https://nextjs.org/docs/app/api-reference/next-config-js/headers
- Flutter security: https://docs.flutter.dev/security
