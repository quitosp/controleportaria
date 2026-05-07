---
name: criar-rbac
description: Aplica controle de roles em controllers C#, middleware Next.js e guards Flutter. Triggers: "/rbac", "criar rbac", "adicionar roles", "proteger rotas com role".
---

# Skill: criar-rbac

## Pre-requisito
- `prd.yaml > rbac.ativo: true` com `roles[]` definidas
- `prd.yaml > autenticacao.ativa: true`

## Acao

### 1. C# (sempre, se API ativa)
- Garantir que admin seed (`SeedAdmin.Executar`) cria todas as `roles` do PRD
- Para cada controller de agregado: aplicar `[Authorize(Roles = "...")]` segundo `prd.yaml > rbac.rotas_protegidas`
- Se `rotas_protegidas` vazio: aplicar `[Authorize]` simples (auth obrigatoria sem RBAC)
- AuthController fica com `[AllowAnonymous]` em registrar/entrar/refresh

Exemplos:
```csharp
[Route("api/[controller]")]
[Authorize(Roles = "admin,atendente")]
public class ClienteController : MainController { ... }

[HttpPost("v1/salvar")]
[Authorize(Roles = "admin")]                 // sobrescreve, so admin pode criar
public async Task<IComandResult> Salvar(...) { ... }
```

### 2. Frontend Next.js (se web ativa)
- Criar `src/middleware.ts` que checa JWT e role:
```ts
import { NextResponse } from "next/server";
import { jwtDecode } from "jwt-decode";

const ROTAS_POR_ROLE: Record<string, string[]> = {
  admin: ["/clientes", "/animais", "/servicos", "/admin"],
  atendente: ["/clientes", "/animais"],
};

export function middleware(req: NextRequest) {
  const token = req.cookies.get("token")?.value;
  if (!token) return NextResponse.redirect(new URL("/login", req.url));

  const claims = jwtDecode<{ role?: string | string[] }>(token);
  const roles = Array.isArray(claims.role) ? claims.role : [claims.role].filter(Boolean);
  const rotaPermitida = roles.some(r => ROTAS_POR_ROLE[r as string]?.some(p => req.nextUrl.pathname.startsWith(p)));

  if (!rotaPermitida) return NextResponse.redirect(new URL("/sem-permissao", req.url));
  return NextResponse.next();
}

export const config = { matcher: ["/((?!login|sem-permissao|api|_next).*)"] };
```
- Criar `src/compartilhados/ganchos/useUsuarioAtual.ts` com hook que decodifica JWT e expoe `roles`, `temRole(r)`, `temQualquerRole(...r)`
- Criar `<RestritoA roles={["admin"]}>` componente que renderiza children so se user tem role

### 3. Flutter (se mobile.tipo=flutter-nativo)
- Em `lib/compartilhados/auth/sessao.dart`: `Sessao` (singleton) decodifica JWT e expoe `temRole(String)`
- `lib/compartilhados/auth/guard.dart`: `RoleGuard` para `go_router` que redireciona pra `/login` ou `/sem-permissao`

## Saida
- Controllers C# anotados
- `middleware.ts` no Next
- Hook `useUsuarioAtual` + componente `<RestritoA>`
- Guard Flutter (se aplicavel)
- Reportar arquivos tocados

## Restricoes
- NAO duplicar checagem de role no front e no back de forma divergente — back e a verdade, front e UX
- NAO usar `localStorage` para token em produção sem HttpOnly cookie. Para demo: `localStorage` aceitavel
- Nome da claim: `role` (lowercase, padrao Identity quando usa `claims.Add(new Claim("role", userRole))`)
- Sempre fallback gracioso: se token expirado, redirect login (nao tela branca)
