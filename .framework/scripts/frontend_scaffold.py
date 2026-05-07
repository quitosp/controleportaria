#!/usr/bin/env python3
"""Scaffold de feature frontend (Next.js + TS + Tailwind + shadcn + TanStack Query + Zod).
Cria os 5 arquivos canonicos por feature, mapeando para endpoints C# Portaria.

Uso:
  python .framework/scripts/frontend_scaffold.py <feature> [--singular <Sing>] [--raiz <path>]
                                                  [--api <prefixo>] [--campos "nome:tipo,..."]

Exemplos:
  python .framework/scripts/frontend_scaffold.py empresas
  python .framework/scripts/frontend_scaffold.py empresas --singular Empresa --campos "nome:string,cnpj:string,telefone:string"
"""
from __future__ import annotations
import argparse, sys
from dataclasses import dataclass
from pathlib import Path

TIPOS_TS = {
    "string": ('z.string()', 'string'),
    "int": ('z.number().int()', 'number'),
    "long": ('z.number().int()', 'number'),
    "decimal": ('z.number()', 'number'),
    "bool": ('z.boolean()', 'boolean'),
    "guid": ('z.string().uuid()', 'string'),
    "datetime": ('z.string().datetime()', 'string'),
}

@dataclass
class Campo:
    nome: str
    tipo: str
    obrigatorio: bool = True

def parse_campos(spec: str) -> list[Campo]:
    if not spec: return [Campo("nome","string")]
    out = []
    for raw in spec.split(","):
        partes = raw.strip().split(":")
        if len(partes) < 2: continue
        nome, tipo = partes[0], partes[1].lower()
        if tipo not in TIPOS_TS: print(f"AVISO tipo {tipo} desconhecido"); continue
        c = Campo(nome=nome, tipo=tipo)
        if len(partes) > 2 and "opcional" in partes[2:]: c.obrigatorio = False
        out.append(c)
    if not any(c.nome == "nome" for c in out):
        out.insert(0, Campo("nome","string"))
    return out

def gerar_tipos(singular: str, campos: list[Campo]) -> str:
    schema_props = []
    for c in campos:
        zod, _ = TIPOS_TS[c.tipo]
        if c.tipo == "string" and c.obrigatorio:
            zod = 'z.string().min(1, "Obrigatorio")'
        if not c.obrigatorio: zod += ".optional()"
        schema_props.append(f"  {c.nome}: {zod},")
    schema_body = "\n".join(schema_props)
    return f"""import {{ z }} from "zod";

export const {singular.lower()}Schema = z.object({{
  {singular.lower()}Id: z.string().uuid(),
{schema_body}
}});

export const salvar{singular}Schema = {singular.lower()}Schema.omit({{ {singular.lower()}Id: true }});
export const alterar{singular}Schema = {singular.lower()}Schema;

export type {singular} = z.infer<typeof {singular.lower()}Schema>;
export type Salvar{singular} = z.infer<typeof salvar{singular}Schema>;
export type Alterar{singular} = z.infer<typeof alterar{singular}Schema>;

export type ResultadoPaginado<T> = {{
  list: T[];
  totalResults: number;
  pageIndex: number;
  pageSize: number;
  query?: string;
}};

export type ComandResult<T = unknown> = {{
  success: boolean;
  message: string;
  data: T;
  code: number;
}};

export type SalvarResultado = {{ id: string }};
"""

def gerar_api(feature: str, singular: str) -> str:
    api_lower = singular.lower()
    return f"""import {{ api }} from "@/compartilhados/servicos/api";
import type {{ {singular}, Salvar{singular}, Alterar{singular}, ResultadoPaginado, ComandResult, SalvarResultado }} from "./tipos";

const BASE = "/api/{api_lower}/v1";

export async function listar{singular}s(pageIndex = 1, pageSize = 20, filter?: string) {{
  const {{ data }} = await api.get<ResultadoPaginado<{singular}>>(`${{BASE}}/listar/${{pageIndex}}/${{pageSize}}`, {{
    params: filter ? {{ filter }} : undefined,
  }});
  return data;
}}

export async function salvar{singular}(payload: Salvar{singular}) {{
  const {{ data }} = await api.post<ComandResult<SalvarResultado>>(`${{BASE}}/salvar`, payload);
  return data;
}}

export async function alterar{singular}(payload: Alterar{singular}) {{
  const {{ data }} = await api.put<ComandResult<SalvarResultado>>(`${{BASE}}/alterar`, payload);
  return data;
}}
"""

def gerar_ganchos(feature: str, singular: str) -> str:
    return f"""import {{ useMutation, useQuery, useQueryClient }} from "@tanstack/react-query";
import {{ listar{singular}s, salvar{singular}, alterar{singular} }} from "./api";
import type {{ Salvar{singular}, Alterar{singular} }} from "./tipos";

const CHAVE = ["{feature}"] as const;

export function useListar{singular}s(pageIndex = 1, pageSize = 20, filter?: string) {{
  return useQuery({{
    queryKey: [...CHAVE, pageIndex, pageSize, filter],
    queryFn: () => listar{singular}s(pageIndex, pageSize, filter),
  }});
}}

export function useSalvar{singular}() {{
  const qc = useQueryClient();
  return useMutation({{
    mutationFn: (data: Salvar{singular}) => salvar{singular}(data),
    onSuccess: () => qc.invalidateQueries({{ queryKey: CHAVE }}),
  }});
}}

export function useAlterar{singular}() {{
  const qc = useQueryClient();
  return useMutation({{
    mutationFn: (data: Alterar{singular}) => alterar{singular}(data),
    onSuccess: () => qc.invalidateQueries({{ queryKey: CHAVE }}),
  }});
}}
"""

def _detectar_fk(c: "Campo", singular_atual: str) -> tuple[str, str] | None:
    """Detecta FK Guid pelo nome (ex: contaId, categoriaId).
    Retorna (entidadeSingular, featurePlural) ou None.
    Ignora a PK do proprio agregado (e.g. movimentoId em Movimento)."""
    if c.tipo != "guid": return None
    if not c.nome.endswith("Id"): return None
    base = c.nome[:-2]  # contaId -> conta
    if not base: return None
    if base.lower() == singular_atual.lower(): return None  # PK do proprio agregado
    entidade = base[0].upper() + base[1:]  # conta -> Conta
    # heuristica de plural PT-BR (suficiente para feature folder)
    plural = base + "s"
    if base.endswith("ao"): plural = base[:-2] + "oes"
    elif base.endswith("m"): plural = base[:-1] + "ns"
    elif base.endswith("l") or base.endswith("r") or base.endswith("z"): plural = base + "es"
    return entidade, plural


def gerar_formulario(feature: str, singular: str, campos: list[Campo]) -> str:
    inputs = []
    fk_imports: list[tuple[str, str]] = []  # (entidadeSingular, featurePlural)
    fks_no_form: list[tuple[str, str, str]] = []  # (campo, entidade, plural)
    usa_controller = False

    for c in campos:
        fk = _detectar_fk(c, singular)
        if fk:
            entidade, plural = fk
            fks_no_form.append((c.nome, entidade, plural))
            if (entidade, plural) not in fk_imports:
                fk_imports.append((entidade, plural))
            usa_controller = True
            label = entidade  # campo "contaId" vira label "Conta"
            inputs.append(
                f'      <div className="space-y-2">\n'
                f'        <Label>{label}</Label>\n'
                f'        <Controller\n'
                f'          control={{control}}\n'
                f'          name="{c.nome}"\n'
                f'          render={{({{ field }}) => (\n'
                f'            <Select value={{field.value ?? ""}} onValueChange={{field.onChange}}>\n'
                f'              <SelectTrigger>\n'
                f'                <SelectValue placeholder={{lista{entidade}s.isLoading ? "Carregando..." : "Selecione {label.lower()}"}} />\n'
                f'              </SelectTrigger>\n'
                f'              <SelectContent>\n'
                f'                {{lista{entidade}s.data?.list.map(o => (\n'
                f'                  <SelectItem key={{o.{entidade.lower()}Id}} value={{o.{entidade.lower()}Id}}>{{o.nome ?? o.{entidade.lower()}Id}}</SelectItem>\n'
                f'                ))}}\n'
                f'              </SelectContent>\n'
                f'            </Select>\n'
                f'          )}}\n'
                f'        />\n'
                f'        {{errors.{c.nome} && <p className="text-sm text-destructive">{{errors.{c.nome}.message}}</p>}}\n'
                f'      </div>'
            )
            continue

        ts_input_type = "text"
        register_opts = ""
        if c.tipo in ("int","long","decimal"):
            ts_input_type = "number"
            register_opts = ", { valueAsNumber: true }"
        if c.tipo == "datetime":
            ts_input_type = "datetime-local"
            register_opts = ", { valueAsDate: true }"
        if c.tipo == "bool":
            ts_input_type = "checkbox"
        label = c.nome[0].upper() + c.nome[1:]
        step = ' step="0.01"' if c.tipo == "decimal" else ""
        inputs.append(
            f'      <div className="space-y-2">\n'
            f'        <Label htmlFor="{c.nome}">{label}</Label>\n'
            f'        <Input id="{c.nome}" type="{ts_input_type}"{step} {{...register("{c.nome}"{register_opts})}} />\n'
            f'        {{errors.{c.nome} && <p className="text-sm text-destructive">{{errors.{c.nome}.message}}</p>}}\n'
            f'      </div>'
        )
    inputs_str = "\n".join(inputs)

    rhf_imports = "useForm, Controller" if usa_controller else "useForm"
    select_imports = ""
    if fk_imports:
        select_imports = '\nimport { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/compartilhados/componentes/ui/select";'
    fk_hook_imports = ""
    fk_hook_calls = ""
    for ent, plu in fk_imports:
        fk_hook_imports += f'\nimport {{ useListar{ent}s }} from "@/funcionalidades/{plu}/ganchos";'
        fk_hook_calls += f"\n  const lista{ent}s = useListar{ent}s(1, 100);"

    destruct = "register, handleSubmit, reset, control, formState: { errors }" if usa_controller else "register, handleSubmit, reset, formState: { errors }"

    return f""""use client";
import {{ {rhf_imports} }} from "react-hook-form";
import {{ zodResolver }} from "@hookform/resolvers/zod";
import {{ toast }} from "sonner";
import {{ Button }} from "@/compartilhados/componentes/ui/button";
import {{ Input }} from "@/compartilhados/componentes/ui/input";
import {{ Label }} from "@/compartilhados/componentes/ui/label";{select_imports}
import {{ salvar{singular}Schema, type Salvar{singular} }} from "../tipos";
import {{ useSalvar{singular} }} from "../ganchos";{fk_hook_imports}

export function Formulario{singular}({{ aoSalvar }}: {{ aoSalvar?: () => void }} = {{}}) {{
  const {{ {destruct} }} = useForm<Salvar{singular}>({{
    resolver: zodResolver(salvar{singular}Schema),
  }});
  const mutation = useSalvar{singular}();{fk_hook_calls}

  return (
    <form
      onSubmit={{handleSubmit(d =>
        mutation.mutate(d, {{
          onSuccess: (resp) => {{
            if (!resp.success) {{ toast.error(resp.message); return; }}
            toast.success(resp.message);
            reset();
            aoSalvar?.();
          }},
          onError: () => toast.error("Erro ao salvar"),
        }})
      )}}
      className="space-y-4"
    >
{inputs_str}
      <Button type="submit" disabled={{mutation.isPending}} className="w-full">
        {{mutation.isPending ? "Salvando..." : "Salvar"}}
      </Button>
    </form>
  );
}}
"""

def feature_pascal(feature: str) -> str:
    """animais -> Animais; tipo-veiculos -> TipoVeiculos"""
    return "".join(p.capitalize() for p in feature.replace("_", "-").split("-"))

def gerar_pagina(feature: str, singular: str) -> str:
    pascal = feature_pascal(feature)
    s_lower = singular.lower()
    return f""""use client";
import {{ useState }} from "react";
import {{ Plus, Search, FileText }} from "lucide-react";
import {{ Button }} from "@/compartilhados/componentes/ui/button";
import {{ Input }} from "@/compartilhados/componentes/ui/input";
import {{ Skeleton }} from "@/compartilhados/componentes/ui/skeleton";
import {{ Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger }} from "@/compartilhados/componentes/ui/dialog";
import {{ useListar{singular}s }} from "./ganchos";
import {{ Formulario{singular} }} from "./componentes/Formulario{singular}";

export function Pagina{pascal}() {{
  const [pagina, setPagina] = useState(1);
  const [filter, setFilter] = useState("");
  const [dialogAberto, setDialogAberto] = useState(false);
  const {{ data, isLoading, isError, error }} = useListar{singular}s(pagina, 20, filter || undefined);

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground">Cadastros</p>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight">{pascal}</h1>
          <p className="text-muted-foreground">Gerencie {s_lower}s do sistema.</p>
        </div>
        <Dialog open={{dialogAberto}} onOpenChange={{setDialogAberto}}>
          <DialogTrigger asChild>
            <Button className="shadow-lg shadow-primary/25 h-11 gap-2">
              <Plus size={{16}} /> Novo {singular}
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Novo {singular}</DialogTitle>
              <DialogDescription>Preencha os campos abaixo</DialogDescription>
            </DialogHeader>
            <Formulario{singular} aoSalvar={{() => setDialogAberto(false)}} />
          </DialogContent>
        </Dialog>
      </header>

      <div className="glass rounded-2xl overflow-hidden">
        <div className="flex items-center gap-3 p-4 border-b border-foreground/5">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar..."
              value={{filter}}
              onChange={{(e) => {{ setFilter(e.target.value); setPagina(1); }}}}
              className="pl-9 h-10 bg-background/60"
            />
          </div>
          {{data && <span className="text-sm text-muted-foreground tabular-nums">{{data.totalResults}} {{data.totalResults === 1 ? "resultado" : "resultados"}}</span>}}
        </div>

        {{isLoading && (
          <div className="p-4 space-y-3">
            {{Array.from({{ length: 4 }}).map((_, i) => <Skeleton key={{i}} className="h-14 rounded-lg" />)}}
          </div>
        )}}
        {{isError && (
          <div className="p-6 text-sm text-destructive">Erro: {{(error as Error).message}}</div>
        )}}
        {{!isLoading && !isError && data && data.list.length === 0 && (
          <div className="text-center py-16 space-y-3">
            <div className="mx-auto h-12 w-12 rounded-full bg-muted grid place-items-center">
              <FileText size={{20}} className="text-muted-foreground" />
            </div>
            <p className="text-muted-foreground">{{filter ? `Nenhum resultado para "${{filter}}"` : `Nenhum {s_lower} cadastrado ainda`}}</p>
          </div>
        )}}
        {{!isLoading && !isError && data && data.list.length > 0 && (
          <div className="divide-y divide-foreground/5">
            {{data.list.map((item) => (
              <div key={{item.{s_lower}Id}} className="flex items-center gap-4 p-4 hover:bg-foreground/[0.02] transition-colors">
                <div className="h-10 w-10 rounded-xl bg-primary/10 text-primary grid place-items-center shrink-0">
                  <FileText size={{18}} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{{item.nome}}</div>
                </div>
              </div>
            ))}}
          </div>
        )}}
      </div>

      {{data && data.totalResults > 0 && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>Total: {{data.totalResults}}</span>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={{() => setPagina((p) => Math.max(1, p - 1))}} disabled={{pagina === 1}}>
              Anterior
            </Button>
            <span className="px-2">{{pagina}}</span>
            <Button variant="outline" size="sm" onClick={{() => setPagina((p) => p + 1)}} disabled={{pagina * 20 >= data.totalResults}}>
              Proxima
            </Button>
          </div>
        </div>
      )}}
    </div>
  );
}}
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("feature")
    ap.add_argument("--singular", default=None)
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--api", default=None)
    ap.add_argument("--campos", default="")
    ap.add_argument("--tudo", action="store_true", help="apos scaffold: roda pos_implementacao (review + seguranca + reindex)")
    ap.add_argument("--forcar", action="store_true", help="sobrescreve api.ts/ganchos.ts/pagina.tsx (preserva tipos.ts e Formulario)")
    args = ap.parse_args()

    feature = args.feature
    singular = args.singular or (feature.rstrip("s").capitalize() if feature.endswith("s") else feature.capitalize())
    raiz = Path(args.raiz).resolve()
    campos = parse_campos(args.campos)

    base = raiz / "src/funcionalidades" / feature
    REGENERAVEIS = {"api.ts", "ganchos.ts", "pagina.tsx"}  # com --forcar
    arquivos = [
        (base / "tipos.ts", lambda: gerar_tipos(singular, campos), "tipos.ts"),
        (base / "api.ts", lambda: gerar_api(feature, singular), "api.ts"),
        (base / "ganchos.ts", lambda: gerar_ganchos(feature, singular), "ganchos.ts"),
        (base / f"componentes/Formulario{singular}.tsx", lambda: gerar_formulario(feature, singular, campos), "Formulario.tsx"),
        (base / "pagina.tsx", lambda: gerar_pagina(feature, singular), "pagina.tsx"),
    ]

    criados, regenerados, existentes = [], [], []
    for caminho, fn, tipo in arquivos:
        if caminho.exists():
            if args.forcar and tipo in REGENERAVEIS:
                caminho.write_text(fn(), encoding="utf-8")
                regenerados.append(str(caminho.relative_to(raiz))); continue
            existentes.append(str(caminho.relative_to(raiz))); continue
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(fn(), encoding="utf-8")
        criados.append(str(caminho.relative_to(raiz)))

    print(f"Feature {feature} (singular: {singular}, campos: {len(campos)}):")
    for c in criados: print(f"  + {c}")
    for r in regenerados: print(f"  ~ {r} (regenerado)")
    for e in existentes: print(f"  = {e} (ja existia)")

    if args.tudo:
        import subprocess as _sp
        scripts_dir = Path(__file__).parent
        print("\n-> Rodando pos_implementacao.py (review + seguranca + reindex)")
        _sp.run([sys.executable, str(scripts_dir / "pos_implementacao.py"),
                 "--raiz", str(raiz), "--stack", "next",
                 "--apenas", feature, "--sem-bloqueio"])
    else:
        print(f"\nProximo: criar app/(privado)/{feature}/page.tsx que importa Pagina{feature.capitalize()} de funcionalidades/{feature}/pagina")

if __name__ == "__main__":
    main()
