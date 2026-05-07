---
name: csharp-novo-agregado
description: Cria agregado C# completo (9 arquivos), gera migration, atualiza banco e reindexa. Atalho one-shot. Triggers: "/agregado Nome", "novo agregado csharp", "scaffold C# Nome", "adiciona agregado X com campo Y".
---

# Skill: csharp-novo-agregado

## Entrada
- Nome singular do agregado (ex: "Veiculo")
- Plural opcional (default: singular + "s")
- Campos opcionais (default: so `Nome string obrigatorio`)

## Acao (fluxo completo, um comando so)

1. Detectar raiz do projeto C# (.sln/.slnx em cwd ou subir).
2. Rodar:
   ```
   python .framework/scripts/csharp_scaffold.py {Singular} --plural {Plural} --campos "..." --tudo
   ```
   `--tudo` faz: scaffold + `migrate.py` (migration add + database update) + `indexar.py`.

3. Se `migrate` falhar com "banco nao existe":
   - Rodar `python .framework/scripts/criar_banco.py --raiz {raiz}` (auto-detecta psql, le credenciais do appsettings)
   - Re-rodar `python .framework/scripts/migrate.py`
   - Se psql nao existir, reportar comando manual ao usuario

4. Reportar:
   - Arquivos criados (9)
   - Arquivos alterados (ContextoDB, DI)
   - Migration gerada (v{N})
   - Tabelas adicionadas no banco
   - Sugestao: restart da API se estiver rodando, depois testar via Swagger

## Saida
- 9 arquivos do padrao Portaria + 2 alterados (ContextoDB, DI)
- 1 migration nova em `repositorios/Repositorios/Migrations/`
- Banco atualizado
- `index.json` atualizado

## Restricoes
- Sempre PT-BR
- Sempre seguir blueprint `.framework/nucleo/csharp-portaria.md`
- NAO sobrescrever arquivos existentes (script protege)
- NAO inventar campos — so o que usuario disse
- Se usuario passar campos com `:`, mostrar sintaxe correta (`max=14` em vez de `max:14`)
- NAO rodar API automaticamente (use `/run` separado)

## Sintaxe de campos (importante)
```
nome:tipo[:flag1[:flag2...]]
```
- Tipos: `string`, `int`, `long`, `decimal`, `bool`, `guid`, `datetime`
- Flags:
  - `obrigatorio` (default)
  - `opcional`
  - `max=N` (tamanho maximo string)
  - `min=N`
- Separador entre campos: virgula

Exemplos:
```
"cnpj:string:obrigatorio:max=14,telefone:string:opcional"
"valor:decimal:obrigatorio,clienteId:guid:obrigatorio,observacao:string:opcional"
"dataNascimento:datetime:obrigatorio,ativo:bool"
```

## Quando usar `--migrate` vs `/agregado` direto
- `/agregado` (esta skill): caminho feliz — projeto C# rodando, banco acessivel
- `csharp_scaffold.py` puro (sem `--migrate`): quando nao quer mexer no banco agora (ex: gerando varios agregados em sequencia, migracao consolidada depois)
