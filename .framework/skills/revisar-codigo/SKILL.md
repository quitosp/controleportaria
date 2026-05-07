---
name: revisar-codigo
description: Revisa codigo gerado contra blueprint da stack. Detecta desvios de padrao, comentarios desnecessarios, naming fora do padrao. Triggers: "/rev", "revisar", "review".
---

# Skill: revisar-codigo

## Entrada
- `estado/projeto.yaml` (para saber stack)
- `estado/index.json`
- Opcionalmente: caminho/arquivo especifico ou agregado

## Acao
1. Carregar blueprint da stack (`nucleo/{stack}.md`).
2. Para cada arquivo do escopo (ou todos se nao especificado):
   - Verificar tipo detectado bate com pasta esperada
   - Para C#: classes tem construtor sem args protegido? properties com private set? FluentValidation embutida em Comand? Handler usa PersistirDados?
   - Verificar zero comentarios em codigo de dominio
   - Verificar nomes seguem convencoes PT-BR
   - Verificar nao usa cascade delete, NoTracking ativo
3. Para agregados C#: usar `buscar.py --agregado X` para checar 9 arquivos esperados.
4. Listar desvios encontrados como itens curtos: `arquivo:linha — desvio`.

## Saida
- Lista de desvios (vazia = OK)
- Sugestao de fix por desvio (curta)

## Restricoes
- NAO reescrever codigo automaticamente — so reportar
- NAO criticar estilo subjetivo — so blueprint
- Maximo 30 desvios por execucao (priorizar criticos)
