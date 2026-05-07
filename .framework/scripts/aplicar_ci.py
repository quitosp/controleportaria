#!/usr/bin/env python3
"""Aplica GitHub Actions CI em projeto.
Detecta stack via prd.yaml ou estrutura e gera workflows apropriados.

Uso: python .framework/scripts/aplicar_ci.py --raiz <projeto> [--stack csharp|next|flutter|all]
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path

CI_CSHARP = '''name: CI - C# API

on:
  push: { branches: [main, develop] }
  pull_request: { branches: [main, develop] }

jobs:
  build-test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env: { POSTGRES_USER: postgres, POSTGRES_PASSWORD: postgres, POSTGRES_DB: ci }
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 5s --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: "9.0.x" }
      - name: Restore
        run: dotnet restore
      - name: Build
        run: dotnet build --no-restore --configuration Release
      - name: Test
        run: dotnet test --no-build --configuration Release --logger "console;verbosity=normal"
        env:
          ConnectionStrings__DefaultConnection: "Host=localhost;Port=5432;Database=ci;Username=postgres;Password=postgres"

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: "9.0.x" }
      - name: Vulnerable packages
        run: dotnet list package --vulnerable --include-transitive | tee /tmp/vuln.txt
      - name: Fail if Critical/High
        run: |
          if grep -E "Critical|High" /tmp/vuln.txt; then
            echo "::error::Pacotes com vulnerabilidades Critical/High encontrados"
            exit 1
          fi
'''

CI_NEXT = '''name: CI - Frontend Next

on:
  push: { branches: [main, develop] }
  pull_request: { branches: [main, develop] }

jobs:
  build-lint:
    runs-on: ubuntu-latest
    defaults: { run: { working-directory: ./pet-shop-web } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20", cache: "npm", cache-dependency-path: "**/package-lock.json" }
      - run: npm ci
      - run: npx tsc --noEmit
      - run: npm run build
        env: { NEXT_TELEMETRY_DISABLED: "1" }

  security:
    runs-on: ubuntu-latest
    defaults: { run: { working-directory: ./pet-shop-web } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: npm ci
      - name: npm audit
        run: npm audit --omit=dev --audit-level=high
'''

CI_FLUTTER = '''name: CI - Flutter

on:
  push: { branches: [main, develop] }
  pull_request: { branches: [main, develop] }

jobs:
  analyze-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with: { channel: "stable" }
      - run: flutter pub get
      - run: dart analyze
      - run: flutter test
'''

CODEQL = '''name: CodeQL

on:
  push: { branches: [main] }
  pull_request: { branches: [main] }
  schedule: [{ cron: "0 6 * * 1" }]

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions: { security-events: write }
    strategy:
      matrix:
        language: [csharp, javascript-typescript]
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with: { languages: ${{ matrix.language }} }
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3
'''

DEPENDABOT = '''version: 2
updates:
  - package-ecosystem: nuget
    directory: "/"
    schedule: { interval: weekly }
    open-pull-requests-limit: 5
  - package-ecosystem: npm
    directory: "/"
    schedule: { interval: weekly }
    open-pull-requests-limit: 5
  - package-ecosystem: github-actions
    directory: "/"
    schedule: { interval: monthly }
'''

def detectar_stacks(raiz: Path) -> list[str]:
    stacks = []
    if list(raiz.glob("**/*.sln")) or list(raiz.glob("**/*.slnx")):
        stacks.append("csharp")
    for sib in [raiz] + list(raiz.parent.glob("*-web")) + list(raiz.parent.glob("*Web*")):
        if (sib / "package.json").exists() and (sib / "next.config.mjs").exists():
            stacks.append("next"); break
    for sib in [raiz] + list(raiz.parent.glob("*-mobile")) + list(raiz.parent.glob("*Mobile*")):
        if (sib / "pubspec.yaml").exists():
            stacks.append("flutter"); break
    return stacks

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--stack", choices=["csharp", "next", "flutter", "all"], default="all")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()

    workflows = raiz / ".github/workflows"
    workflows.mkdir(parents=True, exist_ok=True)

    if args.stack == "all":
        stacks = detectar_stacks(raiz)
        if not stacks:
            print("AVISO: nenhuma stack detectada. Use --stack csharp|next|flutter"); sys.exit(2)
    else:
        stacks = [args.stack]

    print(f"Stacks detectadas: {', '.join(stacks)}")

    mapa = {"csharp": ("ci-csharp.yml", CI_CSHARP),
            "next": ("ci-next.yml", CI_NEXT),
            "flutter": ("ci-flutter.yml", CI_FLUTTER)}

    for stack in stacks:
        nome, conteudo = mapa[stack]
        p = workflows / nome
        if p.exists(): print(f"  = {nome} (ja existe)")
        else: p.write_text(conteudo, encoding="utf-8"); print(f"  + .github/workflows/{nome}")

    # CodeQL e Dependabot sempre
    codeql = workflows / "codeql.yml"
    if not codeql.exists():
        codeql.write_text(CODEQL, encoding="utf-8")
        print(f"  + .github/workflows/codeql.yml (analise estatica)")

    deps = raiz / ".github/dependabot.yml"
    if not deps.exists():
        deps.parent.mkdir(parents=True, exist_ok=True)
        deps.write_text(DEPENDABOT, encoding="utf-8")
        print(f"  + .github/dependabot.yml (atualizacoes semanais)")

    print("\nOK CI/CD aplicado.")
    print("Workflows rodam em push/PR para main e develop.")
    print("CodeQL: analise estatica semanal (segunda 6h).")
    print("Dependabot: PRs automaticos para deps desatualizadas.")

if __name__ == "__main__":
    main()
