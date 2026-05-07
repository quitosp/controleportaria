# Fluxo de criação de projeto

```
[ideia]
  ↓ skill: criar-prd
[estado/prd.yaml]
  ↓ skill: criar-ux  (apenas se stack inclui frontend)
[estado/ux.yaml]
  ↓ skill: criar-arquitetura
[estado/arquitetura.yaml]
  ↓ skill: criar-historias
[estado/historias/HIST-NNN.yaml]
  ↓ skill: implementar-historia (uma de cada vez)
[código gerado]
  ↓ skill: indexar-projeto (após cada implementação)
[estado/index.json atualizado]
  ↓ skill: revisar-codigo (opcional)
[próxima história]
```

UX é opcional para APIs puras. Para projetos com frontend, entra entre PRD e Arquitetura: o PRD define O QUÊ existe, o UX define COMO o usuário interage, e a Arquitetura traduz ambos em estrutura técnica.

## Estados do projeto

`estado/projeto.yaml` rastreia onde está:
```yaml
fase: prd | arquitetura | historias | implementacao
stack: csharp-portaria | frontend-react | python-fastapi
historias_total: 12
historias_concluidas: 5
historia_atual: HIST-006
```

## Regras de transição

1. **Só avançar fase com artefato anterior validado**
   - PRD precisa ter todos campos obrigatórios → checa via `validar-prd`
   - Arquitetura precisa referenciar stack do blueprint
   - História precisa apontar para epic do PRD

2. **Sem retrabalho silencioso**
   - Se mudar PRD, marcar arquitetura/histórias afetadas como `revisao_necessaria: true`

3. **Implementação 1:1 com história**
   - Cada `HIST-NNN.yaml` vira commit lógico (ou PR se git)
   - História menciona arquivos a criar/editar via consulta a `index.json`

## Como o Claude se comporta em cada fase

### Fase PRD
- Pergunta mínima: nome, problema, usuários, MVP. Outros campos derivam.
- Output: YAML estruturado, não markdown narrativo
- Sem perguntas de "discovery profundo" — usuário é solo, sabe o que quer

### Fase Arquitetura
- Lê `prd.yaml` + `nucleo/{stack}.md`
- Output: lista de agregados/features, dependências, ADRs curtos
- Sem trade-off discussion — stack está travada por blueprint

### Fase Histórias
- Quebra cada agregado/feature em histórias atômicas
- Cada história referencia: epic, agregado, arquivos esperados, critério de aceite
- Output: 1 YAML por história em `estado/historias/`

### Fase Implementação
- Para C# agregado novo: chama `scripts/csharp_scaffold.py` primeiro, depois ajusta
- Para outros: gera arquivos seguindo blueprint
- Após criar/editar arquivo, atualiza `index.json` via `scripts/indexar.py`
- Reporta arquivos tocados, não conteúdo

## Comandos curtos (skills)

| Comando | Skill |
|---------|-------|
| `/prd` | criar-prd |
| `/ux` | criar-ux (so projetos com frontend) |
| `/arq` | criar-arquitetura |
| `/historias` | criar-historias |
| `/impl HIST-NNN` | implementar-historia |
| `/agregado Nome` | csharp-novo-agregado (atalho do impl para C#) |
| `/editar-prd` | editar-prd (propaga revisao_necessaria) |
| `/editar-ux` | editar-ux (propaga revisao_necessaria) |
| `/commit HIST-NNN` | commitar-historia |
| `/idx` | indexar-projeto |
| `/buscar X` | buscar-codigo |
| `/rev` | revisar-codigo |
| `/doc` | documentar-projeto (gera README) |
| `/run` | rodar-projeto (background) |
| `/testar X` | criar-testes |
