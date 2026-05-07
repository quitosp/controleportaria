---
name: pacote-deploy
description: Gera Dockerfile multi-stage + docker-compose.yml + manifestos K8s basicos para o projeto. Triggers: "/pacote-deploy", "deploy", "docker", "kubernetes", "containerizar".
---

# Skill: pacote-deploy

## Quando aplicar
- Apos MVP funcionando local (`/run`)
- Antes de subir pra cloud (AWS/Azure/GCP)
- Antes de demonstracao em servidor proprio

## Acao

Rodar:
```
python .framework/scripts/aplicar_deploy.py --raiz . [--registry <docker-registry>]
```

Gera:

### 1. `api/Dockerfile` — multi-stage para .NET 9
```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY . .
RUN dotnet restore servicos/api/Api/Api.csproj
RUN dotnet publish servicos/api/Api/Api.csproj -c Release -o /app

FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
WORKDIR /app
COPY --from=build /app .
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
ENTRYPOINT ["dotnet", "Api.dll"]
```

### 2. `web/Dockerfile` — Next.js standalone
```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:20-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/package.json ./
COPY --from=build /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
```

### 3. `docker-compose.yml` — stack completa local
- Postgres 16 (com volume)
- API (build do api/)
- Web (build do web/)
- Network compartilhada
- Healthchecks

### 4. `k8s/` — manifestos basicos
- `namespace.yaml`
- `postgres.yaml` (StatefulSet + Service + PVC)
- `api.yaml` (Deployment + Service + ConfigMap)
- `web.yaml` (Deployment + Service)
- `ingress.yaml` (NGINX, com TLS via cert-manager)

### 5. `.dockerignore` em api/ e web/
Evita copiar `bin/`, `obj/`, `node_modules/`, `.next/` para a imagem.

## Saida ao usuario

```
arquivos gerados:
  api/Dockerfile               (multi-stage .NET 9)
  api/.dockerignore
  web/Dockerfile               (Next.js standalone)
  web/.dockerignore
  docker-compose.yml           (postgres + api + web)
  k8s/namespace.yaml
  k8s/postgres.yaml
  k8s/api.yaml
  k8s/web.yaml
  k8s/ingress.yaml

testar local:
  docker compose up --build

deploy K8s:
  kubectl apply -f k8s/
```

## Restricoes
- NAO sobrescreve Dockerfile existente — abortar e avisar
- Detecta porta da API a partir do `launchSettings.json` (default 8080 em container)
- Para DB em prod, NUNCA usa o postgres do compose — manifesta como "use Postgres gerenciado"
- Manifestos K8s sao TEMPLATES — usuario ajusta replicas, recursos, secrets
