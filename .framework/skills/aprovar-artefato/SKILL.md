---
name: aprovar-artefato
description: Marca mockup ou contrato como aprovado, liberando /impl HIST-NNN. Gate de qualidade pre-implementacao. Triggers: "/aprovar HIST-NNN", "aprovar mockup", "aprovar contrato".
---

# Skill: aprovar-artefato

## Acao
1. Carregar `estado/historias/HIST-NNN.yaml`
2. Validar:
   - `tipo` != `crud` (CRUD nao precisa aprovacao)
   - `artefato.caminho` existe e arquivo presente
   - `estado` == `aguardando_aprovacao`
3. Mostrar artefato (Read do arquivo) e perguntar ao usuario:
   - "Aprovar artefato HIST-NNN? (sim/nao)"
   - Se usuario apontar mudancas: pedir esclarecimento e atualizar artefato (NAO marcar aprovado)
   - Se aprovar: prosseguir
4. Atualizar historia.yaml:
   ```yaml
   estado: pendente              # libera para /impl
   artefato:
     aprovado: true
     aprovado_em: "ISO-date-now"
   ```
5. Reportar:
   ```
   HIST-NNN aprovada. Pronto para /impl HIST-NNN.
   ```

## Restricoes
- NAO aprovar automaticamente — sempre confirmar com usuario
- NAO modificar conteudo do artefato (so o `aprovado: true`)
- Se usuario quer mudar artefato apos aprovacao: rodar `/artefato HIST-NNN` de novo (volta para aguardando_aprovacao)
- NUNCA pular este gate em historias tipo != crud sem `--sem-bloqueio`

## Por que isso existe
Cada token gasto codando algo que nao bate com a expectativa do usuario e desperdicio. Aprovar mockup/contrato em texto e ~50x mais barato que ajustar codigo.
