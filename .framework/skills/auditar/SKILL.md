---
name: auditar
description: Auditoria de seguranca e LGPD sobre o codigo gerado. Detecta dados sensiveis em logs, endpoints sem [Authorize], leak entre tenants, secrets hardcoded, CORS aberto. Triggers: "/auditar", "audit", "auditoria de seguranca", "LGPD check".
---

# Skill: auditar

## Quando aplicar
- Antes de subir pra producao
- Antes de demonstracao com cliente
- Apos revisao manual de seguranca
- Apos `/seguranca` (vai mais fundo)

## Acao

Rodar `python .framework/scripts/auditar.py --raiz <projeto>`. Esse script faz:

### 1. LGPD / Privacidade
- Procura logs (`_log.LogInformation`, `Console.WriteLine`, `console.log`) que mencionam `cpf`, `email`, `telefone`, `senha`, `token`, `apiKey` sem mascaramento
- Detecta retorno de campos sensiveis em DTOs publicos (Saida class) sem `[JsonIgnore]` ou similar
- Lista controllers que retornam `Usuario` direto em vez de `UsuarioSaida`

### 2. Auth / Authz
- Endpoints sem `[Authorize]` que NAO sao `[AllowAnonymous]` (exceto AuthController/health)
- `[AllowAnonymous]` em endpoints com mutacao (POST/PUT/DELETE)
- Falta de `IAspNetUser` injetado em handlers que precisam saber quem fez a acao

### 3. Multi-tenant / Isolation
- Queries em repositorio sem `Where(x => x.UsuarioId == ...)` quando o domain tem agregado-por-usuario
- Endpoints que aceitam `usuarioId` como parametro mutavel (deve vir do token, nao do body)

### 4. Secrets / Configuracao
- Strings hardcoded com padrao de connection string, JWT secret, API key
- `appsettings.json` commitado com senha real
- `.env` commitado

### 5. CORS / Surface
- `AllowAnyOrigin()` em ApiConfig (deve ser SetIsOriginAllowed em prod)
- `RequireHttpsMetadata = false` em prod

### 6. Inputs
- Strings sem validacao de tamanho (FluentValidation `MaximumLength`)
- Parametros de URL sem `[FromRoute]` constraint
- Falta de rate limiting em endpoints publicos

## Saida

Tabela com criticidade (CRITICO/ALTO/MEDIO/BAIXO/INFO) + arquivo:linha + descricao + sugestao de fix.

Exemplo:
```
CRITICO  servicos/api/Api/Controllers/PedidoController.cs:42  Endpoint POST sem [Authorize]
ALTO     dominios/Dominios/Pedidos/Comandos/Saidas/PedidoSaida.cs:18  Saida expoe campo Senha
MEDIO    repositorios/Repositorios/Repositorio/PedidoRepositorio.cs:55  Listar() sem filtro por UsuarioId — risco de leak entre tenants
BAIXO    appsettings.json:5  ConnectionString com senha em texto claro (use User Secrets)
```

## Restricoes
- NAO modifica codigo — so reporta
- Para corrigir, usuario decide caso-a-caso (alguns positivos sao falsos)
- Falha o gate de commit se houver CRITICO

## Comportamento
- Se houver >=1 CRITICO: aborta com exit 1
- Se houver >=1 ALTO: aviso forte, exit 0
- Sem desvios: exit 0 com "OK"
