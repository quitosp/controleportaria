---
name: rodar-projeto
description: Detecta stack e roda comando de execucao apropriado em background. Triggers: "/run", "rodar projeto", "iniciar API", "iniciar dev".
---

# Skill: rodar-projeto

## Entrada
- `estado/projeto.yaml > stack` ou auto-deteccao

## Auto-deteccao (se projeto.yaml nao existe)
- `*.sln` na raiz → csharp-portaria
- `next.config.*` ou `package.json` com `next` → frontend-react
- `pyproject.toml` ou `main.py` em servicos/api → python-fastapi

## Acao
1. Detectar stack.
2. Antes de rodar, validar pre-requisitos:
   - C#: `dotnet --version` retorna >= 9
   - Frontend: `node --version` retorna >= 20, `npm install` ja foi rodado (existe node_modules)
   - Python: `.venv/` existe ou `uv` instalado
3. Se C#: rodar `python .framework/scripts/sincronizar_api_url.py` para garantir que o frontend par (`<projeto>-web`) aponta para a URL real da API (extrai de `Api/Properties/launchSettings.json`).
4. Rodar comando apropriado em **background** (nao bloquear conversa):
   - C#: `dotnet run --project servicos/api/Api`
   - Frontend: `npm run dev`
   - Python: `uvicorn servicos.api.main:app --reload --host 0.0.0.0 --port 8000`
5. Aguardar 5-10s, ler primeiras linhas de output.
6. Reportar:
   - URL acessivel (`https://localhost:7XXX` para C#, `http://localhost:3000` para Next, etc)
   - PID/handle do processo background
   - Como parar (`KillShell` ou Ctrl+C no terminal)

## Saida
- Processo rodando em background
- URL de acesso
- Linhas iniciais de log

## Restricoes
- SEMPRE em background (run_in_background=true) — nao trava conversa
- Se ja ha processo rodando na mesma porta, perguntar se mata antes
- NAO instalar dependencias automaticamente — reportar e pedir
- Se falhar, capturar primeiras 20 linhas de erro, NAO o build inteiro
- Para C#, usar `parse_dotnet_errors.py` se houver erro de build
