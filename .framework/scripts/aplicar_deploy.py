"""
Gera Dockerfile + docker-compose + K8s manifests.
Uso: python aplicar_deploy.py [--raiz .]
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

DOCKERFILE_API = """# Multi-stage .NET 9
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY . .
RUN dotnet restore servicos/api/Api/Api.csproj
RUN dotnet publish servicos/api/Api/Api.csproj -c Release -o /app /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
WORKDIR /app
COPY --from=build /app .
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
ENV ASPNETCORE_ENVIRONMENT=Production
ENTRYPOINT ["dotnet", "Api.dll"]
"""

DOCKERFILE_WEB = """# Multi-stage Next.js standalone
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/package.json ./
COPY --from=deps /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
"""

DOCKERIGNORE_API = """**/bin
**/obj
**/temp-build
.framework
documentacao
.git
.vs
.vscode
node_modules
*.tgz
"""

DOCKERIGNORE_WEB = """node_modules
.next
.git
.framework
documentacao
*.tgz
.env*
"""

DOCKER_COMPOSE = """services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: {nome_db}
    ports: ["5432:5432"]
    volumes: ["pg_data:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build: ./api
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      ConnectionStrings__DefaultConnection: "Host=postgres;Port=5432;Database={nome_db};Username=postgres;Password=postgres"
      AppSettings__AutenticacaoJwksUrl: "http://api:8080/jwks"
    ports: ["8080:8080"]

  web:
    build: ./web
    depends_on: [api]
    environment:
      NEXT_PUBLIC_API_URL: "http://localhost:8080"
    ports: ["3000:3000"]

volumes:
  pg_data:
"""

K8S_NAMESPACE = """apiVersion: v1
kind: Namespace
metadata:
  name: {nome}
"""

K8S_POSTGRES = """apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: {nome}
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
  clusterIP: None
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: {nome}
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: POSTGRES_DB
          value: {nome_db}
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources: { requests: { storage: 10Gi } }
"""

K8S_API = """# AJUSTE antes de aplicar:
#   1. Crie o Secret 'api-secret' com a connection string real:
#      kubectl -n {nome} create secret generic api-secret \\
#        --from-literal=connection-string='Host=postgres;...;Password=...'
#   2. Os healthchecks /health/live e /health/ready exigem que /observabilidade tenha rodado.
#      Se nao rodou, REMOVA livenessProbe/readinessProbe ou aplique-os.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: {nome}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: {registry}/{nome}-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: ASPNETCORE_ENVIRONMENT
          value: Production
        - name: ConnectionStrings__DefaultConnection
          valueFrom:
            secretKeyRef:
              name: api-secret
              key: connection-string
        resources:
          requests: { cpu: "100m", memory: "256Mi" }
          limits:   { cpu: "500m", memory: "512Mi" }
        # Descomente se /observabilidade rodou (gerou /health/live e /health/ready):
        # livenessProbe:
        #   httpGet: { path: /health/live, port: 8080 }
        #   initialDelaySeconds: 20
        # readinessProbe:
        #   httpGet: { path: /health/ready, port: 8080 }
---
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: {nome}
spec:
  selector:
    app: api
  ports:
  - port: 80
    targetPort: 8080
"""

K8S_WEB = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: {nome}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: {registry}/{nome}-web:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.{nome}.exemplo.com"
        resources:
          requests: { cpu: "50m",  memory: "128Mi" }
          limits:   { cpu: "300m", memory: "384Mi" }
---
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: {nome}
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 3000
"""

K8S_INGRESS = """apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress
  namespace: {nome}
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts: ["api.{nome}.exemplo.com", "{nome}.exemplo.com"]
    secretName: tls-cert
  rules:
  - host: api.{nome}.exemplo.com
    http: { paths: [ { path: /, pathType: Prefix, backend: { service: { name: api, port: { number: 80 } } } } ] }
  - host: {nome}.exemplo.com
    http: { paths: [ { path: /, pathType: Prefix, backend: { service: { name: web, port: { number: 80 } } } } ] }
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--registry", default="ghcr.io/USER")
    args = ap.parse_args()
    raiz = Path(args.raiz).resolve()

    # nome do projeto: pega de prd.yaml > projeto.nome ou do dirname
    nome = raiz.name.lower()
    nome_db = nome.replace("-", "_")

    api = raiz / "api"
    web = raiz / "web"

    if api.exists() and not (api / "Dockerfile").exists():
        (api / "Dockerfile").write_text(DOCKERFILE_API, encoding="utf-8")
        (api / ".dockerignore").write_text(DOCKERIGNORE_API, encoding="utf-8")
        print("OK api/Dockerfile + .dockerignore")
    elif api.exists():
        print("-- api/Dockerfile ja existe (preservado)")

    if web.exists() and not (web / "Dockerfile").exists():
        (web / "Dockerfile").write_text(DOCKERFILE_WEB, encoding="utf-8")
        (web / ".dockerignore").write_text(DOCKERIGNORE_WEB, encoding="utf-8")
        print("OK web/Dockerfile + .dockerignore")
    elif web.exists():
        print("-- web/Dockerfile ja existe (preservado)")

    compose = raiz / "docker-compose.yml"
    if not compose.exists():
        compose.write_text(DOCKER_COMPOSE.format(nome_db=nome_db), encoding="utf-8")
        print("OK docker-compose.yml")
    else:
        print("-- docker-compose.yml ja existe (preservado)")

    k8s = raiz / "k8s"
    k8s.mkdir(exist_ok=True)
    arquivos_k8s = [
        ("namespace.yaml", K8S_NAMESPACE),
        ("postgres.yaml", K8S_POSTGRES),
        ("api.yaml", K8S_API),
        ("web.yaml", K8S_WEB),
        ("ingress.yaml", K8S_INGRESS),
    ]
    for fname, tpl in arquivos_k8s:
        p = k8s / fname
        if not p.exists():
            p.write_text(tpl.format(nome=nome, nome_db=nome_db, registry=args.registry), encoding="utf-8")
            print(f"OK k8s/{fname}")
        else:
            print(f"-- k8s/{fname} ja existe (preservado)")

    print("\nProximo: docker compose up --build  (testar local)")
    print("       : kubectl apply -f k8s/         (deploy K8s, ajuste secrets antes)")


if __name__ == "__main__":
    main()
