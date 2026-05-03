# Fase 4 — Nota de aderência ao núcleo do SGBD

**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-08  
**Projeto:** CONEMO  
**Branch:** `fase-4-alinhamento-explicito-modelo-sgbd`

---

## 1) Escopo desta nota

Esta nota consolida a classificação de cobertura da camada compartilhada atual em relação ao núcleo do SGBD, diferenciando:

1. base já sólida;
2. cobertura parcial;
3. pendências reais.

Não há reimplementação técnica nesta fase.

### Eixos centrais do núcleo do SGBD

Os eixos centrais considerados nesta Fase 4, sempre na mesma ordem, são:

1. participante
2. unidade de saúde
3. triagem/elegibilidade
4. avaliação longitudinal
5. escore derivado
6. uso do app

### Relação com os demais artefatos da Fase 4

- A matriz de aderência faz o mapeamento estrutural entre objetos implementados e eixos do núcleo do SGBD.
- Esta nota consolida o julgamento de aderência e cobertura da camada atual.
- O backlog técnico traduz as lacunas identificadas em pendências técnicas e decisórias.

---

## 2) Base sólida já aderente ao núcleo

### 2.1 Participante (coberta)

- Base: `cur_participant_current_v1`.
- Estado: entidade central implementada, usada como pivô das demais entidades.
- Limites: D1 (`respondent_id` ausente) não impede operação da camada mínima, mas limita reconciliação avançada; ver backlog 3.2.1.

### 2.2 Unidade de saúde (coberta)

- Base: `cur_health_unit_v1`.
- Estado: dimensão padronizada com `health_unit_key`, `ubs_name`, `ubs_city`.
- Evidência de uso: agregações nas três marts mínimas.

---

## 3) Cobertura parcial (aderência existente, mas incompleta)

### 3.1 Triagem/elegibilidade (parcialmente coberta)

- Base atual: escores de triagem em `cur_score_current_v1` (`PHQ`, `GAD`, `FORM_INITIAL`).
- Lacuna: falta entidade explícita de decisão de elegibilidade (`eligibility_status`, `eligibility_reason`, `rule_version`) no modelo implementado; ver backlog 3.1.1.
- Conclusão: há suporte analítico indireto, sem materialização plena do eixo.

### 3.2 Avaliação longitudinal (parcialmente coberta)

- Base atual: `cur_journey_current_v1` e `cur_session_current_v1`.
- Lacunas:
  - `event_timestamp` não implementado de forma robusta (N7; ver backlog 3.2.4);
  - ausência de linha clínica longitudinal completa por instrumento/reavaliação (ver backlog 3.1.2).
- Conclusão: há trilha operacional de progresso, mas não cobertura longitudinal plena do núcleo SGBD.

### 3.3 Escore derivado (parcialmente coberta)

- Base atual: escores de formulário e agregados de jornada em `cur_score_current_v1`.
- Lacunas:
  - ausência de IGI observável na camada atual (ver backlog 3.2.2);
  - distinção de natureza entre score clínico inicial e score operacional de jornada exige governança analítica contínua (ver backlog 3.1.3).
- Conclusão: eixo funcional, porém não completo.

### 3.4 Uso do app (parcialmente coberta)

- Base atual: status de jornada/sessão e métricas de progresso nas marts.
- Lacunas:
  - ausência de eventos operacionais completos (notificações/chatbot/help requests; ver backlog 3.2.3);
  - ausência de trilha de interação fina com timestamp de eventos críticos.
- Conclusão: uso do app está representado em nível mínimo, não em núcleo pleno.

### 3.5 Integração externa de consumo (ativo derivável, não eixo nuclear)

- Base atual: `mart_dashboard_export_v1`.
- Esclarecimento: esta mart é uma visão externa derivável da camada atual.
- Delimitação: ela não corresponde a um eixo central do núcleo do SGBD.
- Conclusão: por isso aparece como ativo de integração externa, e não como entidade nuclear do modelo.

---

## 4) Quadro resumido final

| Eixo SGBD | Classificação | Situação prática |
|---|---|---|
| participante | coberta | Base operacional já utilizável |
| unidade de saúde | coberta | Base territorial consistente |
| triagem/elegibilidade | parcialmente coberta | Triagem indireta por escore, sem decisão explícita |
| avaliação longitudinal | parcialmente coberta | Progresso operacional sem longitudinal clínico pleno |
| escore derivado | parcialmente coberta | Escores disponíveis com lacunas relevantes |
| uso do app | parcialmente coberta | Indicadores mínimos, sem eventos completos |

---

## 5) Conclusão técnica da aderência atual

A camada compartilhada atual apresenta **aderência estrutural mínima consistente** ao núcleo do SGBD para os eixos de participante e unidade de saúde, classificados como **coberta**, e **aderência parcial** para triagem/elegibilidade, avaliação longitudinal, escore derivado e uso do app, classificados como **parcialmente coberta**.

Portanto, a camada está pronta para uso controlado como base comum dashboard/SGBD, mas **ainda não atinge núcleo pleno do SGBD** sem evolução orientada por backlog técnico.

---

## 6) Confirmação de escopo

- Fase 4 executada apenas em modelagem + auditoria/reconciliação + documentação/handoff.
- Sem alteração de `cur_*`.
- Sem alteração de marts.
- Sem abertura de Fase 5.

---

## 7) Status após auditoria

- Situação da Fase 4: aprovada.
- Parecer formal registrado em `Docs/fase-4-parecer-auditoria-2026-04-08.md`.
