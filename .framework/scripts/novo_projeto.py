#!/usr/bin/env python3
"""Inicializa novo projeto a partir de blueprint.
Uso: python .framework/scripts/novo_projeto.py <stack> <nome_projeto> [--destino <path>] [--portaria <path>] [--pwa] [--auth]

Stacks suportadas:
  csharp-portaria  -> cria solucao com 5 projetos + Core base copiado de Portaria-master
                      --auth      adiciona AuthController + seed admin (Identity + JWT)
  frontend-react   -> cria estrutura Next.js feature-based
                      --pwa       configura como PWA instalavel (next-pwa)
  flutter-mobile   -> cria projeto Flutter clean architecture espelhando Portaria
  python-fastapi   -> cria estrutura FastAPI camadas Portaria
"""
from __future__ import annotations
import argparse, shutil, subprocess, sys
from pathlib import Path

GITIGNORE_PATH = Path(__file__).parent.parent / "modelos/gitignore.template"

def copiar_gitignore(destino: Path):
    src = GITIGNORE_PATH
    if src.exists():
        shutil.copy2(src, destino / ".gitignore")
        print(f"  .gitignore copiado")

def csharp_portaria(destino: Path, nome: str, portaria_path: str | None = None, auth: bool = False):
    print(f"Criando solucao C# {nome} em {destino}")
    destino.mkdir(parents=True, exist_ok=True)
    sub = lambda cmd: subprocess.run(cmd, cwd=destino, check=True, shell=False)
    # tenta forcar formato sln antigo (.NET 10 default e slnx); se falhar, fallback
    try:
        sub(["dotnet", "new", "sln", "-n", nome, "--format", "sln"])
    except subprocess.CalledProcessError:
        sub(["dotnet", "new", "sln", "-n", nome])
    # detecta qual foi criado
    sln_files = list(destino.glob(f"{nome}.sln")) + list(destino.glob(f"{nome}.slnx"))
    if not sln_files:
        print(f"ERRO: solucao nao foi criada"); sys.exit(2)
    sln_path = sln_files[0].name

    projetos = [
        ("compartilhados/core/Core", "classlib"),
        ("compartilhados/webApi.core/WebApi.Core", "classlib"),
        ("dominios/Dominios", "classlib"),
        ("repositorios/Repositorios", "classlib"),
        ("servicos/api/Api", "webapi"),
    ]
    for caminho, tipo in projetos:
        nome_proj = caminho.split("/")[-1]
        sub(["dotnet", "new", tipo, "-n", nome_proj, "-o", caminho, "--framework", "net9.0"])
        sub(["dotnet", "sln", sln_path, "add", f"{caminho}/{nome_proj}.csproj"])

    refs = [
        ("compartilhados/webApi.core/WebApi.Core/WebApi.Core.csproj", "compartilhados/core/Core/Core.csproj"),
        ("dominios/Dominios/Dominios.csproj", "compartilhados/core/Core/Core.csproj"),
        ("repositorios/Repositorios/Repositorios.csproj", "compartilhados/core/Core/Core.csproj"),
        ("repositorios/Repositorios/Repositorios.csproj", "compartilhados/webApi.core/WebApi.Core/WebApi.Core.csproj"),
        ("repositorios/Repositorios/Repositorios.csproj", "dominios/Dominios/Dominios.csproj"),
        ("servicos/api/Api/Api.csproj", "compartilhados/core/Core/Core.csproj"),
        ("servicos/api/Api/Api.csproj", "compartilhados/webApi.core/WebApi.Core/WebApi.Core.csproj"),
        ("servicos/api/Api/Api.csproj", "dominios/Dominios/Dominios.csproj"),
        ("servicos/api/Api/Api.csproj", "repositorios/Repositorios/Repositorios.csproj"),
    ]
    for proj, ref in refs:
        sub(["dotnet", "add", proj, "reference", ref])

    # versoes compartilhadas — DEVEM ser identicas em Core e WebApi.Core para evitar NU1605 (downgrade)
    FV = "11.9.2"

    # pacotes Core
    core = "compartilhados/core/Core"
    for pkg, ver in [("FluentValidation", FV), ("MediatR","12.3.0"), ("Newtonsoft.Json","13.0.3")]:
        sub(["dotnet", "add", core, "package", pkg, "--version", ver])

    # pacotes WebApi.Core (FluentValidation precisa bater com Core)
    web = "compartilhados/webApi.core/WebApi.Core"
    for pkg, ver in [("Microsoft.AspNetCore.Authentication.JwtBearer","8.0.6"),
                     ("Microsoft.AspNetCore.Mvc.Core","2.2.5"),
                     ("NetDevPack.Security.JwtExtensions","5.0.1"),
                     ("FluentValidation", FV)]:
        sub(["dotnet", "add", web, "package", pkg, "--version", ver])

    # WebApi.Core precisa de FrameworkReference Microsoft.AspNetCore.App para IApplicationBuilder/HttpContext
    web_csproj = destino / "compartilhados/webApi.core/WebApi.Core/WebApi.Core.csproj"
    if web_csproj.exists():
        txt = web_csproj.read_text(encoding="utf-8")
        if "Microsoft.AspNetCore.App" not in txt:
            txt = txt.replace("</Project>",
                "  <ItemGroup>\n    <FrameworkReference Include=\"Microsoft.AspNetCore.App\" />\n  </ItemGroup>\n</Project>")
            web_csproj.write_text(txt, encoding="utf-8")

    # pacotes Repositorios (Postgres)
    repo = "repositorios/Repositorios"
    for pkg, ver in [("Microsoft.EntityFrameworkCore","9.0.0"),
                     ("Npgsql.EntityFrameworkCore.PostgreSQL","9.0.0"),
                     ("Microsoft.EntityFrameworkCore.Design","9.0.0"),
                     ("Microsoft.EntityFrameworkCore.Tools","9.0.0"),
                     ("Microsoft.AspNetCore.Identity.EntityFrameworkCore","9.0.0"),
                     ("NetDevPack.Security.Jwt.Store.EntityFrameworkCore","5.0.9")]:
        sub(["dotnet", "add", repo, "package", pkg, "--version", ver])

    # pacotes Api
    api = "servicos/api/Api"
    for pkg, ver in [("Swashbuckle.AspNetCore","6.4.0"),
                     ("Microsoft.AspNetCore.Identity.UI","9.0.0"),
                     ("Microsoft.EntityFrameworkCore.Design","9.0.0"),
                     ("NetDevPack.Security.Jwt.AspNetCore","5.0.9")]:
        sub(["dotnet", "add", api, "package", pkg, "--version", ver])

    # Detectar portas HTTP e HTTPS geradas pelo dotnet (launchSettings.json)
    launch_path = destino / "servicos/api/Api/Properties/launchSettings.json"
    porta_https = "7001"
    porta_http = "5001"
    if launch_path.exists():
        import re as _re
        ls_txt = launch_path.read_text(encoding="utf-8")
        m_https = _re.search(r"https://localhost:(\d+)", ls_txt)
        m_http = _re.search(r"http://localhost:(\d+)", ls_txt)
        if m_https: porta_https = m_https.group(1)
        if m_http: porta_http = m_http.group(1)

    # appsettings com Postgres + AppSettings.AutenticacaoJwksUrl (esperado por JwtConfig)
    # Usa HTTPS para producao
    appsettings = (destino / "servicos/api/Api/appsettings.json")
    appsettings.write_text(
        '{\n'
        '  "ConnectionStrings": {\n'
        f'    "DefaultConnection": "Host=localhost;Port=5432;Database={nome.lower()};Username=postgres;Password=postgres"\n'
        '  },\n'
        '  "AppSettings": {\n'
        f'    "AutenticacaoJwksUrl": "https://localhost:{porta_https}/jwks"\n'
        '  },\n'
        '  "Cors": {\n'
        '    "Origens": []\n'
        '  },\n'
        '  "Logging": { "LogLevel": { "Default": "Information", "Microsoft.AspNetCore": "Warning" } },\n'
        '  "AllowedHosts": "*"\n'
        '}\n', encoding="utf-8")

    # appsettings.Development.json — usa HTTP no JWKS (auto-loopback sem cert SSL self-signed).
    # Se voce subir a API com profile https, a porta HTTPS continua acessivel mas o JWKS
    # consulta a propria API via HTTP — evita erro de handshake SSL com cert dev nao confiavel.
    appdev = (destino / "servicos/api/Api/appsettings.Development.json")
    appdev.write_text(
        '{\n'
        '  "ConnectionStrings": {\n'
        f'    "DefaultConnection": "Host=localhost;Port=5432;Database={nome.lower()}_dev;Username=postgres;Password=postgres"\n'
        '  },\n'
        '  "AppSettings": {\n'
        f'    "AutenticacaoJwksUrl": "http://localhost:{porta_http}/jwks"\n'
        '  },\n'
        '  "Logging": { "LogLevel": { "Default": "Debug", "Microsoft.EntityFrameworkCore.Database.Command": "Information" } }\n'
        '}\n', encoding="utf-8")

    # Copiar Core base (default: template interno em .framework/templates/csharp-core)
    print(f"\nCopiando Core base...")
    copiar_script = Path(__file__).parent / "copiar_core_base.py"
    cmd = [sys.executable, str(copiar_script), "--destino", str(destino)]
    if portaria_path:
        cmd += ["--portaria", portaria_path]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    print(res.stdout)
    if res.returncode != 0: print(res.stderr)

    copiar_gitignore(destino)

    if auth:
        print(f"\n-> Aplicando auth (AuthController + seed admin)...")
        scripts_dir = Path(__file__).parent
        subprocess.run([sys.executable, str(scripts_dir / "auth_scaffold.py"),
                        "--raiz", str(destino)], check=False)

    # Docker Compose + Dockerfile
    modelos_dir = Path(__file__).parent.parent / "modelos"
    compose_template = modelos_dir / "docker-compose.template.yml"
    if compose_template.exists():
        compose_dest = destino / "docker-compose.yml"
        if not compose_dest.exists():
            compose_dest.write_text(
                compose_template.read_text(encoding="utf-8").replace("${PROJETO}", nome.lower()),
                encoding="utf-8")
            print(f"  + docker-compose.yml")

    docker_template = modelos_dir / "Dockerfile.csharp.template"
    if docker_template.exists():
        docker_dest = destino / "servicos/api/Api/Dockerfile"
        if not docker_dest.exists():
            docker_dest.write_text(docker_template.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"  + servicos/api/Api/Dockerfile")
        # .dockerignore
        dockerign = destino / ".dockerignore"
        if not dockerign.exists():
            dockerign.write_text("**/bin\n**/obj\n**/.vs\n**/.git\n**/logs\n.framework\nPortaria-master\n", encoding="utf-8")
            print(f"  + .dockerignore")

    print(f"\nOK projeto C# {nome} criado.")
    print(f"  appsettings.json: Database={nome.lower()}")
    print(f"  appsettings.Development.json: Database={nome.lower()}_dev")
    print(f"\nProximos passos:")
    print(f"  1. python .framework/scripts/criar_banco.py --raiz {destino}    (criar banco Postgres)")
    print(f"  2. cd {destino}")
    print(f"  3. python .framework/scripts/migrate.py    (gerar e aplicar migration v1)")
    print(f"  4. python .framework/scripts/csharp_scaffold.py <Agregado>    (criar primeiro agregado)")

def frontend_react(destino: Path, nome: str, pwa: bool = False):
    print(f"Criando frontend Next.js {nome} em {destino}")
    destino.mkdir(parents=True, exist_ok=True)
    for d in ["src/app/(publico)","src/app/(privado)","src/app/api",
              "src/funcionalidades","src/compartilhados/componentes/ui","src/compartilhados/componentes",
              "src/compartilhados/ganchos","src/compartilhados/lib","src/compartilhados/servicos","src/compartilhados/tipos",
              "src/nucleo","public"]:
        (destino / d).mkdir(parents=True, exist_ok=True)

    # api.ts base
    (destino / "src/compartilhados/servicos/api.ts").write_text(
        'import axios from "axios";\n\n'
        'export const api = axios.create({\n'
        '  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5000",\n'
        '  timeout: 10000,\n'
        '});\n\n'
        'api.interceptors.request.use((cfg) => {\n'
        '  if (typeof window !== "undefined") {\n'
        '    const token = localStorage.getItem("token");\n'
        '    if (token) cfg.headers.Authorization = `Bearer ${token}`;\n'
        '  }\n'
        '  return cfg;\n'
        '});\n', encoding="utf-8")

    # provider QueryClient
    (destino / "src/nucleo/provedores.tsx").write_text(
        '"use client";\n'
        'import { QueryClient, QueryClientProvider } from "@tanstack/react-query";\n'
        'import { useState } from "react";\n\n'
        'export function Provedores({ children }: { children: React.ReactNode }) {\n'
        '  const [qc] = useState(() => new QueryClient({ defaultOptions: { queries: { staleTime: 60_000 } } }));\n'
        '  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;\n'
        '}\n', encoding="utf-8")

    # .env.local
    (destino / ".env.local").write_text(
        'NEXT_PUBLIC_API_URL=https://localhost:7219\n', encoding="utf-8")

    # PWA
    if pwa:
        (destino / "public").mkdir(exist_ok=True)
        (destino / "public/manifest.json").write_text(
            '{\n'
            f'  "name": "{nome}",\n'
            f'  "short_name": "{nome}",\n'
            '  "description": "App PWA",\n'
            '  "start_url": "/",\n'
            '  "display": "standalone",\n'
            '  "background_color": "#ffffff",\n'
            '  "theme_color": "#2563eb",\n'
            '  "icons": [\n'
            '    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },\n'
            '    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }\n'
            '  ]\n'
            '}\n', encoding="utf-8")
        print("  manifest.json gerado (icones placeholder em /public/icon-{192,512}.png)")

    copiar_gitignore(destino)
    print("\nOK estrutura base criada.")
    print(f"\nApos rodar 'create-next-app', execute:")
    print(f"  python .framework/scripts/setup_ui.py --raiz {destino}     (UI shadcn + tema claro/escuro)")
    print(f"  npm install                                        (instala pacotes UI)")
    print(f"\nProximos passos manuais (precisam de stdin/prompts):")
    print(f"  cd {destino}")
    print(f"  npx create-next-app@latest . --typescript --tailwind --app --src-dir --use-npm")
    print(f"  npm install axios @tanstack/react-query react-hook-form @hookform/resolvers zod sonner lucide-react jwt-decode")
    if pwa: print(f"  npm install @ducanh2912/next-pwa")
    print(f"\nDepois pra cada feature: python .framework/scripts/frontend_scaffold.py <feature>")

def flutter_mobile(destino: Path, nome: str):
    print(f"Criando app Flutter {nome} em {destino}")
    destino.parent.mkdir(parents=True, exist_ok=True)
    nome_pkg = nome.lower().replace("-", "_")
    sub = lambda cmd, **kw: subprocess.run(cmd, check=True, shell=False, **kw)
    if not destino.exists():
        sub(["flutter", "create", "--org", "com.local", "--platforms", "android,ios,web",
             "-e", str(destino), "--project-name", nome_pkg])
    # estrutura padrao Portaria
    for d in ["lib/compartilhados/auth","lib/compartilhados/http","lib/compartilhados/modelos","lib/compartilhados/widgets",
              "lib/dominios","lib/apresentacao","lib/nucleo"]:
        (destino / d).mkdir(parents=True, exist_ok=True)

    # pacotes
    pacotes = ["flutter_riverpod","riverpod_annotation","dio","freezed_annotation",
               "json_annotation","go_router","flutter_secure_storage","jwt_decoder"]
    dev = ["build_runner","freezed","json_serializable","riverpod_generator"]
    for p in pacotes:
        try: sub(["flutter", "pub", "add", p], cwd=destino)
        except subprocess.CalledProcessError: print(f"  AVISO falha em adicionar {p}")
    for p in dev:
        try: sub(["flutter", "pub", "add", "--dev", p], cwd=destino)
        except subprocess.CalledProcessError: pass

    # .env
    (destino / ".env").write_text(
        f'API_URL=https://localhost:7219\n', encoding="utf-8")

    # base classes Core mirror
    (destino / "lib/compartilhados/http/comand_result.dart").write_text(
        '''import 'package:freezed_annotation/freezed_annotation.dart';
part 'comand_result.freezed.dart';
part 'comand_result.g.dart';

@freezed
class ComandResult with _$ComandResult {
  const factory ComandResult({
    required bool success,
    String? message,
    dynamic data,
    int? code,
  }) = _ComandResult;
  factory ComandResult.fromJson(Map<String, dynamic> json) => _$ComandResultFromJson(json);
}
''', encoding="utf-8")

    (destino / "lib/compartilhados/modelos/paged_result.dart").write_text(
        '''class PagedResult<T> {
  final List<T> list;
  final int totalResults;
  final int pageIndex;
  final int pageSize;
  final String? query;

  PagedResult({required this.list, required this.totalResults, required this.pageIndex, required this.pageSize, this.query});

  factory PagedResult.fromJson(Map<String, dynamic> json, T Function(Object?) fromT) {
    return PagedResult<T>(
      list: (json['list'] as List).map((e) => fromT(e)).toList(),
      totalResults: json['totalResults'] as int,
      pageIndex: json['pageIndex'] as int,
      pageSize: json['pageSize'] as int,
      query: json['query'] as String?,
    );
  }
}
''', encoding="utf-8")

    (destino / "lib/compartilhados/http/dio_client.dart").write_text(
        '''import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const _storage = FlutterSecureStorage();

final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(BaseOptions(baseUrl: const String.fromEnvironment('API_URL', defaultValue: 'http://localhost:5000')));
  dio.interceptors.add(InterceptorsWrapper(
    onRequest: (options, handler) async {
      final token = await _storage.read(key: 'token');
      if (token != null) options.headers['Authorization'] = 'Bearer $token';
      return handler.next(options);
    },
  ));
  return dio;
});
''', encoding="utf-8")

    copiar_gitignore(destino)
    print(f"\nOK app Flutter {nome} criado.")
    print(f"\nProximos passos:")
    print(f"  cd {destino}")
    print(f"  flutter pub run build_runner build --delete-conflicting-outputs")
    print(f"  python .framework/scripts/flutter_scaffold.py <feature>    (gerar features)")

def python_fastapi(destino: Path, nome: str):
    print(f"Criando projeto FastAPI {nome} em {destino}")
    destino.mkdir(parents=True, exist_ok=True)
    for d in ["compartilhados/util","dominios","repositorios/mapeamentos","repositorios/repositorio",
              "servicos/api/controladores","servicos/api/configuracao","servicos/api/identidade","alembic"]:
        (destino / d).mkdir(parents=True, exist_ok=True)
        (destino / d / "__init__.py").touch()

    (destino / "pyproject.toml").write_text(
        f'[project]\n'
        f'name = "{nome.lower()}"\n'
        f'version = "0.1.0"\n'
        f'requires-python = ">=3.12"\n'
        f'dependencies = [\n'
        f'  "fastapi>=0.115",\n'
        f'  "uvicorn[standard]>=0.32",\n'
        f'  "sqlalchemy>=2.0",\n'
        f'  "asyncpg>=0.29",\n'
        f'  "alembic>=1.13",\n'
        f'  "pydantic>=2.9",\n'
        f'  "pydantic-settings>=2.5",\n'
        f'  "python-jose[cryptography]>=3.3",\n'
        f'  "passlib[bcrypt]>=1.7",\n'
        f']\n', encoding="utf-8")

    (destino / ".env").write_text(
        f'DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/{nome.lower()}\n'
        f'JWT_SECRET=trocar-em-producao\n', encoding="utf-8")

    copiar_gitignore(destino)
    print("\nOK estrutura criada.")
    print(f"\nProximos passos:")
    print(f"  cd {destino}")
    print(f"  python -m venv .venv && source .venv/bin/activate (ou .venv\\Scripts\\activate)")
    print(f"  pip install -e .")
    print(f"  createdb {nome.lower()}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stack", choices=["csharp-portaria","frontend-react","flutter-mobile","python-fastapi"])
    ap.add_argument("nome")
    ap.add_argument("--destino", default=None)
    ap.add_argument("--portaria", default=None, help="opcional: usa Portaria-master local em vez do template interno")
    ap.add_argument("--pwa", action="store_true", help="frontend-react: configura PWA")
    ap.add_argument("--auth", action="store_true", help="csharp-portaria: adiciona AuthController + seed admin")
    args = ap.parse_args()
    destino = Path(args.destino or args.nome).resolve()
    if args.stack == "csharp-portaria":
        csharp_portaria(destino, args.nome, args.portaria, auth=args.auth)
    elif args.stack == "frontend-react":
        frontend_react(destino, args.nome, pwa=args.pwa)
    elif args.stack == "flutter-mobile":
        flutter_mobile(destino, args.nome)
    elif args.stack == "python-fastapi":
        python_fastapi(destino, args.nome)

if __name__ == "__main__":
    main()
