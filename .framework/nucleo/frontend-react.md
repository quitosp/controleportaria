# Blueprint Frontend — React/Next.js

Stack: Next.js 15 (App Router) + TypeScript + Tailwind + shadcn/ui + TanStack Query + Zod + React Hook Form.

## Estrutura por feature (não por tipo)

```
{projeto}/
├── src/
│   ├── app/                          # rotas Next.js
│   │   ├── (publico)/login/page.tsx
│   │   ├── (privado)/
│   │   │   ├── layout.tsx
│   │   │   └── {feature}/page.tsx
│   │   ├── api/                      # route handlers (BFF, opcional)
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── funcionalidades/              # uma pasta por feature
│   │   └── {feature}/                # ex: empresas, veiculos
│   │       ├── componentes/          # UI específico da feature
│   │       ├── ganchos/              # hooks (use{Algo})
│   │       ├── api.ts                # chamadas fetch tipadas
│   │       ├── tipos.ts              # tipos TS + Zod schemas
│   │       └── pagina.tsx            # composição da página
│   ├── compartilhados/
│   │   ├── componentes/ui/           # shadcn/ui base
│   │   ├── componentes/              # botões, inputs custom, layouts
│   │   ├── ganchos/                  # hooks globais (useDebounce, etc)
│   │   ├── lib/                      # utils, cn(), formatters
│   │   ├── servicos/api.ts           # axios/fetch instance + interceptors
│   │   └── tipos/                    # tipos globais
│   └── nucleo/
│       ├── config.ts                 # env, urls
│       ├── constantes.ts
│       └── prover.tsx                # QueryClient, Theme, Auth providers
├── public/
├── tailwind.config.ts
├── tsconfig.json                     # strict: true, paths "@/*"
└── next.config.mjs
```

## Padrão por Feature

Cada feature tem 5 arquivos canônicos. Para feature `empresas`:

### 1. `funcionalidades/empresas/tipos.ts`
```ts
import { z } from "zod";

export const empresaSchema = z.object({
  empresaId: z.string().uuid(),
  nome: z.string().min(1, "Nome obrigatório"),
  cnpj: z.string().length(14),
});

export const salvarEmpresaSchema = empresaSchema.omit({ empresaId: true });
export type Empresa = z.infer<typeof empresaSchema>;
export type SalvarEmpresa = z.infer<typeof salvarEmpresaSchema>;

export type ResultadoPaginado<T> = {
  list: T[];
  totalResults: number;
  pageIndex: number;
  pageSize: number;
  query?: string;
};
```

### 2. `funcionalidades/empresas/api.ts`
```ts
import { api } from "@/compartilhados/servicos/api";
import type { Empresa, SalvarEmpresa, ResultadoPaginado } from "./tipos";

export async function listarEmpresas(pageIndex = 1, pageSize = 20, filter?: string) {
  const path = `/empresa/v1/listar/${pageIndex}/${pageSize}${filter ? `/${filter}` : ""}`;
  const { data } = await api.get<ResultadoPaginado<Empresa>>(path);
  return data;
}

export async function salvarEmpresa(payload: SalvarEmpresa) {
  const { data } = await api.post("/empresa/v1/salvar", payload);
  return data;
}
```

### 3. `funcionalidades/empresas/ganchos.ts`
```ts
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listarEmpresas, salvarEmpresa } from "./api";
import type { SalvarEmpresa } from "./tipos";

export function useListarEmpresas(pageIndex = 1, pageSize = 20, filter?: string) {
  return useQuery({
    queryKey: ["empresas", pageIndex, pageSize, filter],
    queryFn: () => listarEmpresas(pageIndex, pageSize, filter),
  });
}

export function useSalvarEmpresa() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SalvarEmpresa) => salvarEmpresa(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["empresas"] }),
  });
}
```

### 4. `funcionalidades/empresas/componentes/FormularioEmpresa.tsx`
```tsx
"use client";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { salvarEmpresaSchema, type SalvarEmpresa } from "../tipos";
import { useSalvarEmpresa } from "../ganchos";

export function FormularioEmpresa() {
  const { register, handleSubmit, formState: { errors } } = useForm<SalvarEmpresa>({
    resolver: zodResolver(salvarEmpresaSchema),
  });
  const mutation = useSalvarEmpresa();

  return (
    <form onSubmit={handleSubmit(d => mutation.mutate(d))}>
      <input {...register("nome")} />
      {errors.nome && <span>{errors.nome.message}</span>}
      <button disabled={mutation.isPending}>Salvar</button>
    </form>
  );
}
```

### 5. `funcionalidades/empresas/pagina.tsx`
Compõe os componentes da feature. Página em `app/(privado)/empresas/page.tsx` só importa e renderiza essa.

## Convenções inegociáveis

| Item | Padrão |
|------|--------|
| Idioma | PT-BR em domínio, código TS em inglês onde for keyword |
| Pasta feature | singular ou plural conforme domínio (espelha API) |
| Componente | PascalCase, arquivo = nome do export |
| Hook | `use{Algo}` camelCase |
| Schema Zod | `{nome}Schema`, tipo via `z.infer` |
| Estado servidor | TanStack Query, sempre |
| Estado client local | useState; global = Zustand `compartilhados/loja/` |
| Validação | Zod + React Hook Form |
| Estilização | Tailwind utility-first; shadcn/ui base |
| Fetch | axios instance única em `compartilhados/servicos/api.ts` com interceptor JWT |
| Imports | absolutos `@/...` via paths tsconfig |
| Async | sempre async/await, nunca .then |
| Erros | `try/catch` no chamador da mutation, toast via sonner |

## Mapeamento API C# Portaria → Frontend

- C# `EmpresaController` `v1/salvar` → TS `salvarEmpresa()` em `funcionalidades/empresas/api.ts`
- C# `EmpresaSaida` → TS `Empresa` (camelCase: EmpresaId → empresaId)
- C# `PagedResult<T>` → TS `ResultadoPaginado<T>`
- C# `ComandResult` → TS `{ success: boolean, message: string, data: any, code: number }`

## Onde fica o quê
- **Rota** → `app/...`
- **Lógica feature** → `funcionalidades/{feature}/`
- **UI reutilizável** → `compartilhados/componentes/`
- **Chamada API** → `funcionalidades/{feature}/api.ts`
- **Estado servidor** → `funcionalidades/{feature}/ganchos.ts`
