# Blueprint: frontend-vue (preview)

Stack alternativa ao Next.js. Use quando o time prefere Vue ou ja tem componentes Vue.

## Stack travada

- **Vue 3** (Composition API + `<script setup>`)
- **Nuxt 3** (SSR/SSG/SPA, file-based routing, Nitro)
- **TypeScript** (strict)
- **Tailwind CSS** + **shadcn-vue** (variant do shadcn/ui)
- **Pinia** (state)
- **vee-validate** + **zod** (formularios + validacao)
- **@tanstack/vue-query** (data fetching)
- **vueuse** (helpers)

## Estrutura padrao

```
web/
├── nuxt.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
├── app.vue
├── pages/                          # rotas file-based
│   ├── login.vue
│   └── (privado)/
│       ├── dashboard.vue
│       └── [...].vue
├── compartilhados/
│   ├── componentes/ui/             # button, input, label, card, table, dialog, select
│   ├── ganchos/
│   │   ├── useAuth.ts
│   │   └── useApi.ts
│   ├── lib/cn.ts
│   └── servicos/api.ts
└── funcionalidades/
    └── <feature>/
        ├── tipos.ts                # Zod schemas
        ├── api.ts                  # axios calls
        ├── ganchos.ts              # vue-query composables
        ├── pagina.vue              # tela principal
        └── componentes/
            └── Formulario<X>.vue
```

## Convencoes

- Nomes de componente: `PascalCase.vue` (`FormularioCliente.vue`)
- Composables: `use<Algo>.ts` (`useClientes`, `useAuth`)
- Stores Pinia: `useStore<X>` (`useStoreAuth`)
- Mesma feature-based organization do `frontend-react`

## Status

⚠️ **PREVIEW** — scaffolds ainda nao gerados automaticamente. Use o `frontend-react` se quer scaffold automatico.

Para usar Vue:
1. `npx nuxi@latest init web`
2. Adicione manualmente: `tailwindcss`, `shadcn-vue`, `pinia`, `@tanstack/vue-query`, `vee-validate`, `zod`, `axios`, `jwt-decode`
3. Estrutura como acima
4. Para auth: porte manualmente o `useAuth` do React (mesma logica, sintaxe Vue Composition API)

Roadmap:
- v8.1: scaffold automatico (`frontend_vue_scaffold.py`)
- v8.2: setup_ui_vue.py (shadcn-vue + tema)
- v8.3: paridade total com `frontend-react`
