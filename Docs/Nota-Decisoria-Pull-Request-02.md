# Nota decisória curta — encaminhamento após revisão institucional do PR #2

**Data:** 08/04/2026
**Projeto:** CONEMO
**Objeto:** decisão de encaminhamento após a revisão institucional do PR `conemo-project/conemo#2`

## Situação de partida

O **PR #2** consolida o encerramento da rodada do Plano Operacional de Pré-processamento de Dados, incluindo:

* artefatos documentais finais;
* scripts SQL centrais da camada curada e das marts;
* pareceres e registros de encerramento da Fase 6 e da rodada.

A rodada encontra-se **formalmente encerrada** e o PR está **aberto para revisão institucional**.

## Decisão de encaminhamento

Após a revisão institucional do **PR #2**, o encaminhamento deverá seguir apenas uma das três saídas abaixo:

### 1. PR aprovado sem ressalvas

Se a revisão institucional concluir que:

* o escopo está correto;
* os arquivos e commits estão adequados;
* não há lacunas documentais ou técnicas materiais,

então o próximo passo será:

* **autorizar o merge do PR #2 na `main`**;
* registrar o merge como fechamento institucional da rodada;
* não abrir nova fase automaticamente.

### 2. PR aprovado com ajustes pontuais

Se a revisão identificar apenas:

* pequenos ajustes documentais;
* correções editoriais;
* complementos mínimos de rastreabilidade;

então o próximo passo será:

* executar **uma etapa curta e cirúrgica de correção**;
* atualizar a branch do PR;
* submeter novamente o PR à revisão;
* só então decidir sobre o merge.

### 3. PR não aprovado por pendência material

Se a revisão identificar:

* ausência de artefato essencial;
* conflito de rastreabilidade;
* lacuna técnica ou documental relevante;
* inclusão indevida de arquivos fora do escopo;

então o próximo passo será:

* **não realizar o merge**;
* registrar formalmente a pendência;
* abrir uma correção específica, com escopo estrito;
* reapresentar o PR após saneamento.

## Regra de governança

Em qualquer cenário:

* **não realizar merge sem revisão institucional concluída**;
* **não abrir nova rodada ou nova fase técnica automaticamente**;
* tratar o PR #2 como checkpoint formal de encerramento da rodada, e não como autorização implícita para continuidade.

## Conclusão

Fica registrado que, **após a revisão institucional do PR #2**, o projeto deverá seguir exclusivamente por uma destas vias:

1. merge autorizado;
2. correção pontual e nova revisão;
3. bloqueio por pendência material, sem merge.

Não há autorização automática para nova fase após a revisão do PR.
