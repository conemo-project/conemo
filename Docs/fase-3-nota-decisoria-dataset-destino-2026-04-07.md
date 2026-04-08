# Nota decisória formal — dataset de destino da Etapa 3.2 da Fase 3

**Data:** 07/04/2026  
**Projeto:** CONEMO  
**Fase:** Fase 3 — Etapa 3.2  
**Objeto:** definição do dataset de destino da camada curada compartilhada

---

## Decisão

Fica formalmente definido que:

1. o dataset oficial de destino da **Etapa 3.2 da Fase 3** será **`firestore_curated`**;
2. esse dataset deverá ser criado no **BigQuery do projeto `conemo-412202`**, com documentação, scripts e rastreabilidade correspondentes registrados no repositório GitHub institucional do projeto;
3. o dataset **`firestore_curated`** será a materialização da **camada curada compartilhada** da arquitetura de dados aprovada no projeto;
4. a ausência atual desse dataset indica que a arquitetura prevista **ainda não está operacionalmente completa no ambiente institucional**, razão pela qual a **Etapa 3.2 não deve ser liberada automaticamente** sem o devido preparo do destino e novo checkpoint formal.

---

## Justificativa

Esta decisão está alinhada:

* ao Plano de Implementação do Dashboard, que pressupõe camada analítica e marts derivadas para consumo por UBS e gestão;
* ao Plano Operacional de Pré-processamento de Dados, que define a camada curada compartilhada no BigQuery como componente formal da arquitetura de dados do projeto;
* às regras de reprodutibilidade, rastreabilidade, governança e continuidade estabelecidas em `Docs/RULES.md` e `Docs/Workflow-Projeto.md`.

---

## Implicação operacional

A continuidade da Etapa 3.2 fica condicionada a:

* criação ou confirmação formal do dataset `firestore_curated` no ambiente BigQuery do projeto `conemo-412202`;
* verificação de sua localização compatível com `firestore_export` (`southamerica-east1`);
* registro documental e técnico correspondente no repositório;
* novo checkpoint de prontidão antes do início da implementação SQL dos marts.

---

## Situação após esta nota

| Item | Status |
|------|--------|
| Dataset oficial de destino (`firestore_curated`) | **definido** |
| Arquitetura curada compartilhada | **confirmada** |
| Etapa 3.2 | **ainda não liberada** |
| Próxima ação | preparação formal do dataset de destino e checkpoint operacional |

---

## Referências documentais

| Documento | Papel nesta decisão |
|-----------|---------------------|
| `Docs/RULES.md` | Governança, rastreabilidade, segurança |
| `Docs/Workflow-Projeto.md` | Ciclo de fases e checkpoints obrigatórios |
| `Docs/Plano-implementacao-dashboard.md` | Arquitetura BigQuery-first e camada analítica |
| `Docs/fase-3-precheck-operacional-etapa-3-2.md` | Diagnóstico que identificou ausência do dataset e mismatch de localização |
| `Docs/fase-3-parecer-auditoria-2026-04-07.md` | Parecer que manteve Fase 3 em aberto após aprovação da Etapa 3.1 |

---

*Nota registrada em conformidade com `Docs/RULES.md` e `Docs/Workflow-Projeto.md`. Qualquer avanço além desta nota depende de novo checkpoint formal documentado e comprometido no repositório institucional.*
