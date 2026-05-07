---
name: instalar-projeto
description: Setup completo de projeto existente apos clone. Detecta stack, instala deps, cria banco, roda migrations, configura .env. Triggers: "/instalar", "setup", "configurar projeto", "primeiro setup".
---

# Skill: instalar-projeto

## Quando aplicar
- Acabou de clonar um repo Framework
- Maquina nova / novo dev no time
- Trocou de OS

## Acao

### Passo 0 — Verificar ambiente (OBRIGATORIO)
Antes de qualquer instalacao, rodar:
```
python .framework/scripts/verificar_ambiente.py
```
Esse script checa: Node>=20, Python>=3.10, dotnet>=9 (se C#), psql>=14 (opcional), git, docker (opcional). E lista portas em uso (3000, 5001, 5432, etc) que podem atrapalhar o `/run`.

**Se sair com FALTA**: parar e dizer ao usuario o que instalar. NAO seguir os passos abaixo.

### Passo 1 — Detectar stacks via `prd.yaml > plataformas` (ou estrutura de pastas se PRD ausente) e executar em sequencia:

### Backend C#
```bash
# 1. Restore packages
dotnet restore

# 2. Criar banco se nao existe
python .framework/scripts/criar_banco.py --raiz <projeto-csharp>

# 3. Aplicar migrations
python .framework/scripts/migrate.py --raiz <projeto-csharp> --so-update

# 4. Build
dotnet build
```

### Frontend Next
```bash
cd <projeto-web>
npm install
# .env.local ja existe? se nao, criar com NEXT_PUBLIC_API_URL
[ -f .env.local ] || cp .env.local.example .env.local
```

### Flutter
```bash
cd <projeto-mobile>
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
# .env existe?
[ -f .env ] || cp .env.example .env
```

### Indexar
```bash
python .framework/scripts/indexar.py <raiz>
```

### Docker (alternativa unificada)
Se houver `docker-compose.yml`:
```bash
docker compose up -d postgres
# espera healthy
docker compose run api dotnet ef database update
docker compose up -d
```

## Saida
Lista do que foi instalado + URLs disponiveis:
- API: https://localhost:7219/swagger
- Frontend: http://localhost:3000
- Postgres: localhost:5432

## Restricoes
- NAO sobrescrever `.env.local` ou `appsettings.Development.json` se existirem
- Se `dotnet`, `node`, ou `flutter` faltarem, reportar e abortar
- Se Postgres nao acessivel, oferecer rodar via docker compose
- NAO rodar `git pull` automaticamente (pode haver mudancas locais)

## Pre-requisitos do host
- .NET SDK 9
- Node 20+
- Flutter 3.24+ (so se mobile)
- Postgres 16 (ou Docker)
- Python 3.10+ (para os scripts Framework)
