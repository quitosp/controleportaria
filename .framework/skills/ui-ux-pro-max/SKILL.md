---
name: ui-ux-pro-max
description: Inteligencia de design UI/UX. 50+ estilos, 161 paletas, 57 font pairings, 161 tipos de produto, 99 UX guidelines, 25 chart types. Importado de https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (NextLevelBuilder). Triggers: "/uiux", "design system", "estilo de UI", "revisar UI", "checklist UI", "melhorar tela", "que paleta usar", "que fonte usar".
---

# Skill: ui-ux-pro-max

Importada do repo oficial [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill). Mantida 100% fiel — `scripts/` e `data/` (15 CSVs) sao copia direta do repo. SKILL.md adaptado para integrar com nosso framework.

## Estrutura
```
.framework/skills/ui-ux-pro-max/
├── SKILL.md                  # este arquivo (adaptado para Framework)
└── repo-original/            # clone completo de nextlevelbuilder/ui-ux-pro-max-skill
    ├── README.md             # documentacao oficial (28KB)
    ├── CLAUDE.md             # instrucoes Claude originais
    ├── LICENSE               # MIT
    ├── skill.json
    ├── cli/                  # CLI Node.js do projeto original (2 MB)
    ├── docs/
    ├── preview/
    ├── screenshots/          # screenshots de exemplos (1.1 MB)
    └── src/ui-ux-pro-max/
        ├── scripts/
        │   ├── search.py             # CLI principal
        │   ├── core.py               # busca + parsing CSV
        │   └── design_system.py      # logica de --design-system
        ├── data/                     # 16 CSVs (1.3 MB)
        │   ├── styles.csv            # 50+ estilos
        │   ├── colors.csv            # 161 paletas
        │   ├── typography.csv        # 57 font pairings
        │   ├── google-fonts.csv      # catalogo completo de fontes (745 KB)
        │   ├── products.csv          # 161 tipos de produto
        │   ├── ux-guidelines.csv     # 99 regras de UX
        │   ├── ui-reasoning.csv      # logica de matching
        │   ├── charts.csv            # 25 chart types
        │   ├── landing.csv           # estruturas de landing
        │   ├── design.csv            # design tokens
        │   ├── icons.csv             # icon libraries
        │   ├── app-interface.csv     # iOS/Android/RN guidelines
        │   ├── react-performance.csv # React/Next perf
        │   ├── draft.csv
        │   └── stacks/               # presets por stack
        └── templates/
            ├── base/                 # quick-reference + skill-content
            └── platforms/            # 18 configs (Claude, Cursor, Continue, Gemini, Windsurf, Copilot, ...)
```

**Wrapper curto**: `.framework/scripts/uiux.py` delega ao `search.py` original. Use o wrapper sempre.

## Comandos

### Design system completo (RECOMENDADO — comece sempre por aqui)
```bash
python .framework/scripts/uiux.py "<tipo_produto> <industria> <palavras-chave>" --design-system
```

Retorna em ASCII formatado: pattern + style + colors (hex completo) + typography (Google Fonts URL) + effects + anti-patterns + pre-delivery checklist.

Para output em markdown: `-f markdown`

### Persistir design system
```bash
python .framework/scripts/uiux.py "..." --design-system --persist -p "Nome Projeto"
```

Cria `design-system/MASTER.md` (regras globais) e opcionalmente `design-system/pages/<nome>.md` com `--page "nome"` para overrides por tela.

### Busca por dominio especifico
```bash
python .framework/scripts/uiux.py "<termo>" --domain <dominio> [-n <max>]
```

Dominios disponiveis:

| Dominio | Conteudo | Exemplo |
|---------|----------|---------|
| `product` | 161 tipos de produto + estilo recomendado | `--domain product "petshop"` |
| `style` | 50+ estilos UI | `--domain style "glassmorphism"` |
| `color` | 161 paletas por industria | `--domain color "wellness pink"` |
| `typography` | 57 font pairings | `--domain typography "elegant editorial"` |
| `google-fonts` | catalogo Google Fonts | `--domain google-fonts "variable popular sans"` |
| `landing` | estrutura de landing | `--domain landing "saas pricing"` |
| `chart` | 25 chart types | `--domain chart "trend timeline"` |
| `ux` | 99 guidelines de UX | `--domain ux "animation accessibility"` |
| `web` | iOS/Android/RN guidelines | `--domain web "safe areas dynamic type"` |
| `react` | React/Next performance | `--domain react "memo rerender bundle"` |
| `prompt` | CSS keywords / AI prompts | `--domain prompt "minimalism"` |

### Stack guidelines
```bash
python .framework/scripts/uiux.py "<termo>" --stack react-native
```

(Original e focado em React Native. Para Next.js, use `--domain react`. Para Flutter, mapeie principios a partir das guidelines de mobile UX.)

## Quando aplicar

**Sempre**:
- Desenhar nova pagina/tela (login, dashboard, admin, e-commerce, SaaS, app mobile)
- Criar/refatorar componente (button, modal, navbar, sidebar, card, table, form, chart)
- Escolher paleta, tipografia, escala de espacamento
- Revisar UI por UX/acessibilidade/consistencia
- Implementar nav, animacoes, comportamento responsivo
- Decisoes de estilo (glass, claymorphism, minimal, brutal, neumorphism, bento, dark, flat)

**Se**:
- UI esta "nao profissional" mas o motivo nao esta claro
- Recebeu feedback sobre usabilidade
- Otimizacao pre-launch
- Construir design system reutilizavel

**Pule**:
- Logica pura de backend / API / DB
- Performance nao relacionada a interface
- Infra / DevOps / scripts

## Workflow oficial (do repo)

### Step 1 — Analisar requisitos
Extrair do PRD ou pedido:
- **Tipo de produto**: SaaS, e-commerce, dashboard, portfolio, blog, mobile app, fintech, healthcare, beauty, marketplace, social, gaming, tool, productivity
- **Audiencia**: B2B / B2C, faixa etaria, contexto
- **Palavras-chave de estilo**: minimal, vibrant, dark, glassmorphism, brutal, neumorphism, bento, content-first
- **Stack**: vem do `prd.yaml > plataformas`

### Step 2 — Gerar design system (OBRIGATORIO)
```bash
python .framework/scripts/uiux.py "<tipo> <industria> <keywords>" --design-system -p "Nome Projeto"
```

A logica em `ui-reasoning.csv` aplica regras de matching para escolher o melhor estilo + paleta + fonte para o tipo de produto.

### Step 3 — Persistir (Master + Overrides)
```bash
python .framework/scripts/uiux.py "..." --design-system --persist -p "Nome"
```

Gera:
- `design-system/MASTER.md` — Single Source of Truth global
- `design-system/pages/` — pasta para overrides por pagina

Para gerar override de pagina:
```bash
python .framework/scripts/uiux.py "..." --design-system --persist -p "Nome" --page "checkout"
```

### Step 4 — Consulta detalhada (conforme necessario)
```bash
# Ja tenho design system, quero ver estilos similares ao recomendado
python .framework/scripts/uiux.py "claymorphism" --domain style

# Ja tenho paleta, quero ver outras opcoes
python .framework/scripts/uiux.py "fintech blue" --domain color -n 5

# Quero font alternativa
python .framework/scripts/uiux.py "modern geometric" --domain typography

# Tenho duvida de UX
python .framework/scripts/uiux.py "form validation error" --domain ux
```

### Step 5 — Implementacao no nosso framework
Apos escolher design system, integrar com nossos scripts:

**Web (Next.js + shadcn)**:
1. Garantir que `setup_ui.py` ja foi rodado (componentes UI base)
2. Aplicar paleta no `src/app/globals.css` — converter hex (`#EC4899`) para HSL (`330 81% 60%`) nas variaveis
3. Carregar fontes via `next/font/google` no `app/layout.tsx`
4. Usar `frontend_scaffold.py` para gerar features

**Mobile (Flutter)**:
1. Aplicar paleta em `lib/nucleo/tema.dart` via `ColorScheme.fromSeed(seedColor: Color(0xFFEC4899))`
2. Carregar fonts via `google_fonts` package em `lib/nucleo/tema.dart`
3. Usar `flutter_scaffold.py` para gerar features

## Quick Reference — 10 categorias por prioridade

| # | Categoria | Impacto | Checks obrigatorios |
|---|-----------|---------|----------------------|
| 1 | Acessibilidade | CRITICO | Contraste 4.5:1, alt text, navegacao teclado, aria-labels |
| 2 | Touch & Interacao | CRITICO | Tamanho min 44x44, gap 8px+, feedback de loading |
| 3 | Performance | ALTO | WebP/AVIF, lazy loading, reservar espaco (CLS<0.1) |
| 4 | Estilo / Selecao | ALTO | Combinar com tipo de produto, consistencia, SVG |
| 5 | Layout & Responsivo | ALTO | Mobile-first, viewport meta, sem scroll horizontal |
| 6 | Tipografia & Cor | MEDIO | Base 16px, line-height 1.5, tokens semanticos |
| 7 | Animacao | MEDIO | Duracao 150-300ms, motion com significado |
| 8 | Forms & Feedback | MEDIO | Labels visiveis, erro perto do campo, helper text |
| 9 | Navegacao | ALTO | Back previsivel, bottom nav <=5, deep linking |
| 10 | Charts & Dados | BAIXO | Legendas, tooltips, cores acessiveis |

Para detalhes de cada categoria, rodar:
```bash
python .framework/scripts/uiux.py "<categoria>" --domain ux
```

## Pre-delivery checklist

Antes de marcar UI como pronta:

**Visual**:
- [ ] Sem emoji como icone (so SVG via lucide-react ou Material Icons)
- [ ] Todos icones do mesmo set (stroke width consistente)
- [ ] Marcas oficiais com proporcoes corretas
- [ ] Pressed state nao desloca layout
- [ ] Tokens semanticos (CSS vars / ThemeData), nao hex cru por componente

**Interacao**:
- [ ] Todo tappable tem feedback visual em <100ms
- [ ] Touch targets >=44x44pt (iOS) / 48x48dp (Android) / >=44px (web)
- [ ] Animacoes 150-300ms com easing nativo
- [ ] Disabled state nao interativo + visivel
- [ ] Tab order = ordem visual
- [ ] Sem conflito de gestures

**Light/Dark**:
- [ ] Contraste primary >=4.5:1 nos dois modos
- [ ] Contraste secondary >=3:1 nos dois modos
- [ ] Borders/dividers visiveis nos dois modos
- [ ] Modal scrim 40-60% black
- [ ] Testado nos dois modos

**Layout**:
- [ ] Safe areas respeitadas
- [ ] Conteudo nao escondido atras de barras fixas
- [ ] Verificado em phone pequeno + tablet + landscape
- [ ] Insets/gutters adaptam por largura
- [ ] Ritmo 4/8dp consistente
- [ ] Texto longo nao edge-to-edge em tablet

**Acessibilidade**:
- [ ] Imagens/icones com alt/label
- [ ] Form fields com labels + helpers + erros claros
- [ ] Cor nao e o unico indicador
- [ ] Reduced-motion + dynamic-type suportados
- [ ] Roles/states (selected/disabled/expanded) anunciados

## Integracao com outras skills

- **`criar-ux`** chama esta skill antes de gerar `estado/ux.yaml` — usa o `--design-system` para fundamentar decisoes
- **`criar-prd`** ja captura a stack que define se Step 5 (web/mobile) se aplica
- **`frontend_scaffold.py`** / **`flutter_scaffold.py`** geram codigo seguindo as regras
- **`setup_ui.py`** aplica componentes shadcn + tema claro/escuro

## Restricoes
- NAO inventar regras — sempre rodar `--domain ux` para consultar as 99 guidelines
- NAO emoji como icone, sempre SVG (Lucide / Heroicons / Material Icons)
- NAO escrever cor hex em componente — sempre CSS variable / ThemeData token
- SEMPRE testar em pelo menos 2 breakpoints (mobile + desktop)
- SEMPRE rodar pre-delivery checklist antes de considerar pronto
- O repo original e focado em React Native — para Next.js usar `--domain react`, para Flutter mapear principios das guidelines mobile

## Subskills disponiveis (referencia)
O repo-original traz ainda 6 subskills em `repo-original/.claude/skills/` que NAO sao auto-discovered (estao "enterradas"). Se precisar consultar:
- `banner-design/SKILL.md` — design de banners e materiais promocionais
- `brand/SKILL.md` — identidade de marca (logo, cores, voz)
- `design/SKILL.md` — fundamentos gerais de design
- `design-system/SKILL.md` — criacao de design systems completos
- `slides/SKILL.md` — design de apresentacoes
- `ui-styling/SKILL.md` — micro-decisoes de styling

Pra consultar, le direto via `Read` em `.framework/skills/ui-ux-pro-max/repo-original/.claude/skills/<nome>/SKILL.md`.

## Manutencao
Para atualizar do upstream (preserva nosso SKILL.md, recopia `repo-original/`):
```bash
python .framework/scripts/atualizar_uiux.py          # aplica
python .framework/scripts/atualizar_uiux.py --dry    # so mostra diff
```

## Atribuicao
Skill original: [github.com/nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (autor: NextLevelBuilder, licenca MIT). Os arquivos `scripts/` e `data/` sao copia direta do repo (commit em main). Este SKILL.md e adaptacao com integracao no framework.
