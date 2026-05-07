#!/usr/bin/env python3
"""Configura E2E tests com Playwright em projeto Next.js.
Adiciona pacote, gera config, gera testes basicos (login + rota privada).

Uso: python .framework/scripts/aplicar_e2e.py --raiz <projeto-web> [--base-url http://localhost:3000]
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

PLAYWRIGHT_CONFIG = '''import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: process.env.BASE_URL ?? "{BASE_URL}",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
  webServer: process.env.CI ? undefined : {
    command: "npm run dev",
    url: "{BASE_URL}",
    reuseExistingServer: true,
    timeout: 120 * 1000,
  },
});
'''

AUTH_SPEC = '''import { test, expect } from "@playwright/test";

test.describe("Autenticacao", () => {
  test("login com credenciais default redireciona para /clientes", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/email/i).fill("admin@local");
    await page.getByLabel(/senha/i).fill("Admin@123");
    await page.getByRole("button", { name: /entrar/i }).click();
    await expect(page).toHaveURL(/clientes/, { timeout: 10000 });
  });

  test("rota privada sem token redireciona para /login", async ({ page, context }) => {
    await context.clearCookies();
    await page.evaluate(() => localStorage.clear());
    await page.goto("/clientes");
    await expect(page).toHaveURL(/login/);
  });

  test("logout limpa token e volta para login", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/email/i).fill("admin@local");
    await page.getByLabel(/senha/i).fill("Admin@123");
    await page.getByRole("button", { name: /entrar/i }).click();
    await expect(page).toHaveURL(/clientes/);
    await page.getByRole("button", { name: /sair/i }).click();
    await expect(page).toHaveURL(/login/);
  });
});
'''

NAVEGACAO_SPEC = '''import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel(/email/i).fill("admin@local");
  await page.getByLabel(/senha/i).fill("Admin@123");
  await page.getByRole("button", { name: /entrar/i }).click();
  await expect(page).toHaveURL(/clientes/);
});

test("sidebar navega entre paginas privadas", async ({ page }) => {
  await page.getByRole("link", { name: /animais/i }).click();
  await expect(page).toHaveURL(/animais/);
  await page.getByRole("link", { name: /servicos/i }).click();
  await expect(page).toHaveURL(/servicos/);
  await page.getByRole("link", { name: /clientes/i }).click();
  await expect(page).toHaveURL(/clientes/);
});

test("toggle de tema alterna claro/escuro", async ({ page }) => {
  const html = page.locator("html");
  const inicial = await html.getAttribute("class");
  await page.getByRole("button", { name: /alternar tema/i }).click();
  await page.waitForTimeout(200);
  const novo = await html.getAttribute("class");
  expect(novo).not.toBe(inicial);
});
'''

WORKFLOW_E2E = '''name: E2E Playwright

on:
  pull_request: { branches: [main, develop] }

jobs:
  e2e:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    services:
      postgres:
        image: postgres:16-alpine
        env: { POSTGRES_USER: postgres, POSTGRES_PASSWORD: postgres, POSTGRES_DB: e2e }
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 5s --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: "9.0.x" }
      - uses: actions/setup-node@v4
        with: { node-version: "20", cache: "npm", cache-dependency-path: "**/package-lock.json" }

      - name: Setup API
        env:
          ConnectionStrings__DefaultConnection: "Host=localhost;Port=5432;Database=e2e;Username=postgres;Password=postgres"
        run: |
          dotnet tool install --global dotnet-ef --version 9.0.0
          dotnet ef database update --project repositorios/Repositorios --startup-project servicos/api/Api
          nohup dotnet run --project servicos/api/Api --no-launch-profile --urls=https://localhost:7219 &
          sleep 15

      - name: Run E2E
        working-directory: ./pet-shop-web
        env:
          BASE_URL: http://localhost:3000
          NEXT_PUBLIC_API_URL: https://localhost:7219
        run: |
          npm ci
          npx playwright install --with-deps chromium
          npx playwright test

      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: pet-shop-web/playwright-report/
'''

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default="pet-shop-web")
    ap.add_argument("--base-url", default="http://localhost:3000")
    ap.add_argument("--instalar", action="store_true", help="roda npm install + playwright install")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()
    if not (raiz / "package.json").exists():
        print(f"ERRO: nao parece projeto Next em {raiz}"); sys.exit(2)

    e2e_dir = raiz / "e2e"
    e2e_dir.mkdir(exist_ok=True)

    cfg = raiz / "playwright.config.ts"
    if not cfg.exists():
        cfg.write_text(PLAYWRIGHT_CONFIG.replace("{BASE_URL}", args.base_url), encoding="utf-8")
        print(f"  + playwright.config.ts")
    auth = e2e_dir / "auth.spec.ts"
    if not auth.exists():
        auth.write_text(AUTH_SPEC, encoding="utf-8")
        print(f"  + e2e/auth.spec.ts")
    nav = e2e_dir / "navegacao.spec.ts"
    if not nav.exists():
        nav.write_text(NAVEGACAO_SPEC, encoding="utf-8")
        print(f"  + e2e/navegacao.spec.ts")

    # Workflow CI
    workflows = raiz.parent / ".github/workflows"
    if workflows.parent.parent.name == raiz.parent.name or (raiz.parent / ".github").exists():
        workflows.mkdir(parents=True, exist_ok=True)
        wf = workflows / "e2e.yml"
        if not wf.exists():
            wf.write_text(WORKFLOW_E2E, encoding="utf-8")
            print(f"  + .github/workflows/e2e.yml")

    # Patch package.json
    pkg = raiz / "package.json"
    pkg_data = json.loads(pkg.read_text(encoding="utf-8"))
    pkg_data.setdefault("devDependencies", {})
    if "@playwright/test" not in pkg_data["devDependencies"]:
        pkg_data["devDependencies"]["@playwright/test"] = "^1.48.0"
        pkg_data.setdefault("scripts", {})
        pkg_data["scripts"]["e2e"] = "playwright test"
        pkg_data["scripts"]["e2e:ui"] = "playwright test --ui"
        pkg.write_text(json.dumps(pkg_data, indent=2) + "\n", encoding="utf-8")
        print(f"  package.json: @playwright/test + scripts adicionados")

    if args.instalar:
        print("\n-> npm install")
        subprocess.run(["npm", "install"], cwd=raiz, check=False)
        print("\n-> npx playwright install --with-deps chromium")
        subprocess.run(["npx", "playwright", "install", "--with-deps", "chromium"], cwd=raiz, check=False)

    print("\nOK E2E configurado.")
    print("\nProximos passos:")
    print(f"  cd {raiz}")
    print(f"  npm install                                   # se nao usou --instalar")
    print(f"  npx playwright install --with-deps chromium")
    print(f"  npm run e2e                                    # roda em modo headless")
    print(f"  npm run e2e:ui                                 # abre Playwright UI")

if __name__ == "__main__":
    main()
