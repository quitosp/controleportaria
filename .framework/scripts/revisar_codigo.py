#!/usr/bin/env python3
"""Lint estrutural automatico contra blueprints do framework.
Detecta desvios do padrao Portaria/Frontend/Flutter.

Uso:
  python .framework/scripts/revisar_codigo.py [--raiz .] [--stack csharp|next|flutter|all]
  python .framework/scripts/revisar_codigo.py --raiz <projeto> --apenas <agregado>
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

class Desvio:
    def __init__(self, sev: str, regra: str, msg: str, arq: str = "", linha: int = 0):
        self.sev = sev; self.regra = regra; self.msg = msg; self.arq = arq; self.linha = linha

    def __repr__(self):
        loc = f" ({self.arq}{':'+str(self.linha) if self.linha else ''})" if self.arq else ""
        return f"[{self.sev}] {self.regra}: {self.msg}{loc}"

CRITICO, ALTO, MEDIO, INFO = "CRITICO", "ALTO", "MEDIO", "INFO"

def grep(arq: Path, pattern: str) -> list[tuple[int, str]]:
    if not arq.exists() or not arq.is_file(): return []
    try: txt = arq.read_text(encoding="utf-8", errors="replace")
    except Exception: return []
    return [(i, ln.strip()) for i, ln in enumerate(txt.splitlines(), 1) if re.search(pattern, ln)]

def conta_comentarios_dominio(arq: Path) -> int:
    """Conta comentarios // ou /* em arquivos de dominio (entidade/comando/handler/repo)."""
    try: txt = arq.read_text(encoding="utf-8", errors="replace")
    except Exception: return 0
    count = 0
    for ln in txt.splitlines():
        s = ln.strip()
        if s.startswith("//") or s.startswith("/*") or s.startswith("*"):
            # ignora using e XML doc
            if not s.startswith("///"):
                count += 1
    return count

# ============================ C# REVIEW ============================

def revisar_csharp(raiz: Path, apenas_agregado: str | None = None) -> list[Desvio]:
    desvios = []
    if not (raiz / "servicos/api/Api/Api.csproj").exists():
        return [Desvio(INFO, "stack", "nao parece projeto C#-portaria")]

    dom_dir = raiz / "dominios/Dominios"
    if not dom_dir.exists(): return desvios

    IGNORAR = {"bin", "obj", "Properties", "Migrations"}
    for agreg_dir in dom_dir.iterdir():
        if not agreg_dir.is_dir(): continue
        if agreg_dir.name in IGNORAR: continue
        if apenas_agregado and apenas_agregado.lower() not in agreg_dir.name.lower(): continue

        plural = agreg_dir.name
        # Detectar singular pelo nome do arquivo de entidade
        ent_dir = agreg_dir / "Entidades"
        if not ent_dir.exists():
            desvios.append(Desvio(ALTO, "estrutura-faltando", f"Pasta Entidades/ ausente em {plural}"))
            continue
        entidades = list(ent_dir.glob("*.cs"))
        if not entidades:
            desvios.append(Desvio(ALTO, "entidade-faltando", f"Nenhum arquivo .cs em {plural}/Entidades/"))
            continue
        singular = entidades[0].stem

        # 9 arquivos esperados
        esperados = [
            f"Entidades/{singular}.cs",
            f"Comandos/Entradas/Salvar{singular}Entrada.cs",
            f"Comandos/Entradas/Alterar{singular}Entrada.cs",
            f"Comandos/Saidas/{singular}Saida.cs",
            f"Comandos/Handlers/{singular}CommandHandler.cs",
            f"IRepositorios/I{singular}Repositorio.cs",
        ]
        for rel in esperados:
            if not (agreg_dir / rel).exists():
                desvios.append(Desvio(MEDIO, "arquivo-faltando", f"{plural}/{rel}"))

        # Repositorio + Maps + Controller
        for rel in [
            f"repositorios/Repositorios/Mapeamentos/{singular}Maps.cs",
            f"repositorios/Repositorios/Repositorio/{singular}Repositorio.cs",
            f"servicos/api/Api/Controllers/{singular}Controller.cs",
        ]:
            if not (raiz / rel).exists():
                desvios.append(Desvio(MEDIO, "arquivo-faltando", rel))

        # === Verificacoes na entidade ===
        ent = agreg_dir / f"Entidades/{singular}.cs"
        if ent.exists():
            txt = ent.read_text(encoding="utf-8", errors="replace")
            if "public " + singular + "()" in txt:
                desvios.append(Desvio(ALTO, "construtor-publico-vazio",
                    f"{singular} tem construtor publico vazio. Deve ser protected (EF Core).",
                    str(ent.relative_to(raiz))))
            if "protected " + singular + "()" not in txt and ": Entity" in txt:
                desvios.append(Desvio(ALTO, "construtor-protegido-faltando",
                    f"{singular} : Entity precisa de construtor protected vazio para EF",
                    str(ent.relative_to(raiz))))
            # private set em propriedades
            for ln_num, ln in grep(ent, r"public\s+\w+\??\s+\w+\s*\{\s*get;\s*set;\s*\}"):
                desvios.append(Desvio(MEDIO, "setter-publico-em-entidade",
                    "Entidade deve ter private set (encapsulamento). Use 'get; private set;'",
                    str(ent.relative_to(raiz)), ln_num))

            coms = conta_comentarios_dominio(ent)
            if coms > 0:
                desvios.append(Desvio(INFO, "comentarios-em-dominio",
                    f"{coms} comentario(s) na entidade. Padrao: zero comentarios em dominio.",
                    str(ent.relative_to(raiz))))

        # === Verificacoes no Handler ===
        handler = agreg_dir / f"Comandos/Handlers/{singular}CommandHandler.cs"
        if handler.exists():
            txt = handler.read_text(encoding="utf-8", errors="replace")
            if "PersistirDados" not in txt:
                desvios.append(Desvio(ALTO, "handler-sem-persistir",
                    f"{singular}CommandHandler nao usa PersistirDados (padrao do CommandHandler base)",
                    str(handler.relative_to(raiz))))
            if "EhValido()" not in txt:
                desvios.append(Desvio(ALTO, "handler-sem-validacao",
                    f"{singular}CommandHandler nao chama EhValido() no comando",
                    str(handler.relative_to(raiz))))
            # comentarios
            coms = conta_comentarios_dominio(handler)
            if coms > 2:
                desvios.append(Desvio(INFO, "comentarios-em-dominio",
                    f"{coms} comentarios no Handler. Considere remover (codigo deve falar por si).",
                    str(handler.relative_to(raiz))))

        # === Verificacoes na Entrada ===
        for entrada_nome in ["Salvar", "Alterar"]:
            entrada = agreg_dir / f"Comandos/Entradas/{entrada_nome}{singular}Entrada.cs"
            if entrada.exists():
                txt = entrada.read_text(encoding="utf-8", errors="replace")
                if "FluentValidation" not in txt:
                    desvios.append(Desvio(ALTO, "fluent-validation-ausente",
                        f"{entrada_nome}{singular}Entrada nao tem FluentValidation embutida",
                        str(entrada.relative_to(raiz))))
                if "AbstractValidator<" not in txt:
                    desvios.append(Desvio(ALTO, "validator-ausente",
                        f"{entrada_nome}{singular}Entrada nao tem class Validation aninhada",
                        str(entrada.relative_to(raiz))))

        # === Verificacoes no Repositorio ===
        repo = raiz / f"repositorios/Repositorios/Repositorio/{singular}Repositorio.cs"
        if repo.exists():
            txt = repo.read_text(encoding="utf-8", errors="replace")
            if "ChangeTracker.Clear()" not in txt:
                desvios.append(Desvio(MEDIO, "no-tracking-faltando",
                    f"{singular}Repositorio.Salvar/Alterar nao limpa ChangeTracker",
                    str(repo.relative_to(raiz))))

        # === Verificacoes no Controller ===
        ctrl = raiz / f"servicos/api/Api/Controllers/{singular}Controller.cs"
        if ctrl.exists():
            txt = ctrl.read_text(encoding="utf-8", errors="replace")
            if ": MainController" not in txt:
                desvios.append(Desvio(MEDIO, "base-controller-incorreto",
                    f"{singular}Controller deve herdar de MainController, nao ControllerBase",
                    str(ctrl.relative_to(raiz))))
            if "[Route(\"api/[controller]\")]" not in txt:
                desvios.append(Desvio(MEDIO, "route-padrao",
                    "Controller sem [Route('api/[controller]')]",
                    str(ctrl.relative_to(raiz))))

        # === Verificacoes no DI ===
        di = raiz / "servicos/api/Api/Configuration/DependencyInjectionConfig.cs"
        if di.exists():
            di_txt = di.read_text(encoding="utf-8", errors="replace")
            if f"I{singular}Repositorio, {singular}Repositorio" not in di_txt:
                desvios.append(Desvio(ALTO, "di-nao-registra-repo",
                    f"DependencyInjectionConfig nao registra I{singular}Repositorio",
                    "servicos/api/Api/Configuration/DependencyInjectionConfig.cs"))
            if f"{singular}CommandHandler" not in di_txt:
                desvios.append(Desvio(ALTO, "di-nao-registra-handler",
                    f"DependencyInjectionConfig nao registra {singular}CommandHandler",
                    "servicos/api/Api/Configuration/DependencyInjectionConfig.cs"))

        # === Verificacoes no ContextoDB ===
        ctx = raiz / "repositorios/Repositorios/Contexto/ContextoDB.cs"
        if ctx.exists():
            ctx_txt = ctx.read_text(encoding="utf-8", errors="replace")
            if f"DbSet<{singular}>" not in ctx_txt:
                desvios.append(Desvio(ALTO, "ctx-sem-dbset",
                    f"ContextoDB nao tem DbSet<{singular}>",
                    "repositorios/Repositorios/Contexto/ContextoDB.cs"))
            if f"{singular}Maps()" not in ctx_txt:
                desvios.append(Desvio(MEDIO, "ctx-sem-maps",
                    f"ContextoDB nao tem ApplyConfiguration(new {singular}Maps())",
                    "repositorios/Repositorios/Contexto/ContextoDB.cs"))

    # === Verificacoes globais de Controllers (thin) ===
    ctrls_dir = raiz / "servicos/api/Api/Controllers"
    if ctrls_dir.exists():
        for ctrl_file in ctrls_dir.glob("*.cs"):
            txt = ctrl_file.read_text(encoding="utf-8", errors="replace")
            if "AuthController" in ctrl_file.name:
                continue  # AuthController tem logica especifica de Identity
            for ln_num, linha in grep(ctrl_file, r"\btry\s*\{|\bcatch\s*\("):
                desvios.append(Desvio(MEDIO, "controller-com-try-catch",
                    f"{ctrl_file.name} contem try/catch — mover excecao para Service/Handler e deixar ExceptionMiddleware tratar",
                    str(ctrl_file.relative_to(raiz)), ln_num))
                break

    # ExceptionMiddleware deve estar registrado
    api_cfg = raiz / "servicos/api/Api/Configuration/ApiConfig.cs"
    if api_cfg.exists():
        cfg_txt = api_cfg.read_text(encoding="utf-8", errors="replace")
        if "UseTratamentoErros" not in cfg_txt and "ExceptionMiddleware" not in cfg_txt:
            desvios.append(Desvio(ALTO, "sem-exception-middleware",
                "ApiConfig nao registra ExceptionMiddleware (app.UseTratamentoErros())",
                "servicos/api/Api/Configuration/ApiConfig.cs"))

    # FluentValidation: versoes em Core e WebApi.Core devem bater (NU1605)
    import re as _re
    pares = [
        ("compartilhados/core/Core/Core.csproj", "Core"),
        ("compartilhados/webApi.core/WebApi.Core/WebApi.Core.csproj", "WebApi.Core"),
    ]
    versoes_fv = {}
    for rel, nome in pares:
        p = raiz / rel
        if p.exists():
            t = p.read_text(encoding="utf-8", errors="replace")
            m = _re.search(r'PackageReference\s+Include="FluentValidation"\s+Version="([^"]+)"', t)
            if m: versoes_fv[nome] = (m.group(1), rel)
    if len(versoes_fv) == 2 and versoes_fv["Core"][0] != versoes_fv["WebApi.Core"][0]:
        desvios.append(Desvio(ALTO, "fluentvalidation-version-mismatch",
            f"Core usa FluentValidation {versoes_fv['Core'][0]} mas WebApi.Core usa {versoes_fv['WebApi.Core'][0]} — causa NU1605 (Aviso como Erro). Alinhe as duas versoes.",
            versoes_fv["WebApi.Core"][1]))

    # === Validar regras de negocio (RN-NNN) ===
    # Para cada historia concluida com regras_negocio[], cada RN deve ter comentario "// RN-NNN" no codigo C#.
    desvios.extend(_validar_regras_negocio(raiz))

    return desvios


def _validar_regras_negocio(raiz: Path) -> list[Desvio]:
    """Para cada HIST concluida com regras_negocio[], verifica que cada RN-NNN
    aparece como comentario no codigo do projeto."""
    out: list[Desvio] = []
    historias_dir = raiz / ".framework/estado/historias"
    if not historias_dir.exists(): return out

    try:
        import yaml
    except ImportError:
        return out

    # Coletar todos os comentarios "// RN-NNN" do codigo C#
    rns_no_codigo: dict[str, list[tuple[str, int]]] = {}
    for cs in raiz.rglob("*.cs"):
        if any(p in cs.parts for p in ("bin", "obj", "Migrations", "node_modules")): continue
        try: txt = cs.read_text(encoding="utf-8", errors="replace")
        except Exception: continue
        for i, ln in enumerate(txt.splitlines(), 1):
            for m in re.finditer(r'//\s*(RN-\d+)\b', ln):
                rns_no_codigo.setdefault(m.group(1), []).append((str(cs.relative_to(raiz)), i))

    # Para cada historia, conferir
    for hist_path in sorted(historias_dir.glob("HIST-*.yaml")):
        try:
            hist = yaml.safe_load(hist_path.read_text(encoding="utf-8")) or {}
        except Exception: continue
        if hist.get("estado") != "concluida": continue
        rns = hist.get("regras_negocio") or []
        if not rns: continue
        for rn in rns:
            if rn not in rns_no_codigo:
                out.append(Desvio(ALTO, "regra-negocio-sem-implementacao",
                    f"{hist.get('id')} declara {rn} mas nao ha comentario '// {rn}' no codigo. "
                    f"Adicione na linha que implementa a validacao da regra.",
                    str(hist_path.relative_to(raiz))))
    return out

# ============================ NEXT REVIEW ============================

def revisar_next(raiz: Path) -> list[Desvio]:
    desvios = []
    if not (raiz / "package.json").exists() or not (raiz / "src").exists():
        return [Desvio(INFO, "stack", "nao parece projeto Next.js")]

    func = raiz / "src/funcionalidades"
    if not func.exists():
        return [Desvio(INFO, "stack", "sem src/funcionalidades, pulando review")]

    for feat_dir in func.iterdir():
        if not feat_dir.is_dir(): continue
        feat = feat_dir.name

        # 5 arquivos canonicos
        esperados = ["tipos.ts", "api.ts", "ganchos.ts", "pagina.tsx"]
        for nome in esperados:
            if not (feat_dir / nome).exists():
                desvios.append(Desvio(MEDIO, "arquivo-faltando", f"funcionalidades/{feat}/{nome}"))

        # tipos.ts deve ter Zod
        tipos = feat_dir / "tipos.ts"
        if tipos.exists():
            txt = tipos.read_text(encoding="utf-8", errors="replace")
            if "z.object" not in txt and "z.infer" not in txt:
                desvios.append(Desvio(ALTO, "sem-zod",
                    f"funcionalidades/{feat}/tipos.ts nao usa Zod",
                    f"src/funcionalidades/{feat}/tipos.ts"))

        # api.ts deve usar instance api
        api_ts = feat_dir / "api.ts"
        if api_ts.exists():
            txt = api_ts.read_text(encoding="utf-8", errors="replace")
            if "fetch(" in txt:
                desvios.append(Desvio(MEDIO, "fetch-direto",
                    f"funcionalidades/{feat}/api.ts usa fetch() direto. Use a instance api do compartilhados/servicos/api.ts",
                    f"src/funcionalidades/{feat}/api.ts"))
            if 'from "@/compartilhados/servicos/api"' not in txt and "import { api }" not in txt:
                desvios.append(Desvio(ALTO, "api-instance-faltando",
                    f"funcionalidades/{feat}/api.ts nao importa a instance api",
                    f"src/funcionalidades/{feat}/api.ts"))

        # ganchos.ts deve usar TanStack Query
        ganchos = feat_dir / "ganchos.ts"
        if ganchos.exists():
            txt = ganchos.read_text(encoding="utf-8", errors="replace")
            if "useQuery" not in txt and "useMutation" not in txt:
                desvios.append(Desvio(MEDIO, "sem-tanstack",
                    f"funcionalidades/{feat}/ganchos.ts nao usa TanStack Query",
                    f"src/funcionalidades/{feat}/ganchos.ts"))

        # formularios: input type=number precisa de valueAsNumber (senao Zod number recebe string)
        comp_dir = feat_dir / "componentes"
        if comp_dir.exists():
            for tsx in comp_dir.glob("Formulario*.tsx"):
                ftxt = tsx.read_text(encoding="utf-8", errors="replace")
                import re as _re
                # acha <Input type="number" ... register("X") sem valueAsNumber>
                for m in _re.finditer(r'type="number"[^>]*register\("([^"]+)"\s*\)', ftxt):
                    desvios.append(Desvio(ALTO, "input-number-sem-valueAsNumber",
                        f'{tsx.name}: campo "{m.group(1)}" e type="number" mas register sem {{ valueAsNumber: true }} — Zod vai falhar com "Expected number, received string"',
                        str(tsx.relative_to(raiz))))
                for m in _re.finditer(r'type="datetime-local"[^>]*register\("([^"]+)"\s*\)', ftxt):
                    desvios.append(Desvio(MEDIO, "input-date-sem-valueAsDate",
                        f'{tsx.name}: campo "{m.group(1)}" e type="datetime-local" mas register sem {{ valueAsDate: true }}',
                        str(tsx.relative_to(raiz))))
                # FK Guid (campo *Id) jamais deve ser <Input type="text"> — usar <Select> com lista
                # Heuristica: campo termina em Id, schema usa z.string().uuid() E aparece como <Input> no form
                tipos_path = feat_dir / "tipos.ts"
                campos_uuid: set[str] = set()
                if tipos_path.exists():
                    ttxt = tipos_path.read_text(encoding="utf-8", errors="replace")
                    for m in _re.finditer(r'(\w+):\s*z\.string\(\)\.uuid\(\)', ttxt):
                        campos_uuid.add(m.group(1))
                for m in _re.finditer(r'<Input[^>]+register\("([^"]+)"\s*\)', ftxt):
                    nome = m.group(1)
                    if nome.endswith("Id") and nome in campos_uuid and nome[:-2].lower() != feat.lower().rstrip("s"):
                        desvios.append(Desvio(ALTO, "fk-como-input-text",
                            f'{tsx.name}: FK "{nome}" esta como <Input> — UUID nao deve ser pedido ao usuario. Use <Select> populado por useListar{nome[:-2].capitalize()}s',
                            str(tsx.relative_to(raiz))))

    # Padroes globais
    src = raiz / "src"
    for tsx in list(src.rglob("*.tsx")) + list(src.rglob("*.ts")):
        if "/node_modules/" in str(tsx) or "/.next/" in str(tsx): continue
        for ln_num, _ in grep(tsx, r"dangerouslySetInnerHTML"):
            desvios.append(Desvio(ALTO, "xss-risk",
                "dangerouslySetInnerHTML detectado (risco XSS — sanitize ou evite)",
                str(tsx.relative_to(raiz)), ln_num))
        for ln_num, _ in grep(tsx, r'console\.(log|warn|error)\('):
            # so report em arquivos /funcionalidades ou /app
            if "/funcionalidades/" in str(tsx) or "/app/" in str(tsx):
                desvios.append(Desvio(INFO, "console-log",
                    "console.log em codigo de producao (remover antes de deploy)",
                    str(tsx.relative_to(raiz)), ln_num))

    return desvios

# ============================ FLUTTER REVIEW ============================

def revisar_flutter(raiz: Path) -> list[Desvio]:
    desvios = []
    if not (raiz / "pubspec.yaml").exists():
        return [Desvio(INFO, "stack", "nao parece projeto Flutter")]

    lib = raiz / "lib"
    dom = lib / "dominios"
    if not dom.exists(): return desvios

    for feat_dir in dom.iterdir():
        if not feat_dir.is_dir(): continue
        feat = feat_dir.name
        # Esperados: modelos, repositorios, notifiers
        for sub in ["modelos", "repositorios", "notifiers"]:
            if not (feat_dir / sub).exists():
                desvios.append(Desvio(MEDIO, "estrutura-faltando", f"dominios/{feat}/{sub}/"))

    # console-logs em prod
    for dart in lib.rglob("*.dart"):
        for ln_num, _ in grep(dart, r"\bprint\("):
            desvios.append(Desvio(INFO, "print-em-prod",
                "print() em codigo Flutter (use logger ou debugPrint para desenvolvimento)",
                str(dart.relative_to(raiz)), ln_num))

    return desvios

# ============================ MAIN ============================

def imprimir(desvios: list[Desvio], titulo: str):
    if not desvios:
        print(f"\n[{titulo}] OK: nenhum desvio.")
        return
    grupos = {CRITICO: [], ALTO: [], MEDIO: [], INFO: []}
    for d in desvios: grupos.setdefault(d.sev, []).append(d)
    print(f"\n=== [{titulo}] {len(desvios)} desvios ===")
    for sev in [CRITICO, ALTO, MEDIO, INFO]:
        if not grupos[sev]: continue
        print(f"\n--- {sev} ({len(grupos[sev])}) ---")
        for d in grupos[sev]:
            loc = f"  ({d.arq}{':'+str(d.linha) if d.linha else ''})" if d.arq else ""
            print(f"  [{d.regra}] {d.msg}{loc}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--stack", choices=["csharp", "next", "flutter", "all"], default="all")
    ap.add_argument("--apenas", default=None, help="filtra agregado/feature especifico")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()

    print(f"Review estrutural em {raiz}")
    total = 0; criticos_altos = 0

    if args.stack in ("csharp", "all"):
        d = revisar_csharp(raiz, args.apenas)
        imprimir(d, "C#")
        total += len([x for x in d if x.sev != INFO])
        criticos_altos += len([x for x in d if x.sev in (CRITICO, ALTO)])

    if args.stack in ("next", "all"):
        next_root = raiz
        if not (raiz / "package.json").exists():
            for sib in raiz.parent.glob("*-web"):
                if (sib / "package.json").exists(): next_root = sib; break
        d = revisar_next(next_root)
        imprimir(d, "Next")
        total += len([x for x in d if x.sev != INFO])
        criticos_altos += len([x for x in d if x.sev in (CRITICO, ALTO)])

    if args.stack in ("flutter", "all"):
        flutter_root = raiz
        if not (raiz / "pubspec.yaml").exists():
            for sib in raiz.parent.glob("*-mobile"):
                if (sib / "pubspec.yaml").exists(): flutter_root = sib; break
        d = revisar_flutter(flutter_root)
        imprimir(d, "Flutter")
        total += len([x for x in d if x.sev != INFO])
        criticos_altos += len([x for x in d if x.sev in (CRITICO, ALTO)])

    print(f"\n=== RESUMO REVIEW: {total} desvios ({criticos_altos} CRITICO+ALTO) ===")
    sys.exit(1 if criticos_altos > 0 else 0)

if __name__ == "__main__":
    main()
