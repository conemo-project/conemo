# Fase 3.3 — Validação cruzada dos marts

**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-08  
**Projeto:** CONEMO  
**Repositório:** `conemo-project/conemo` (clone institucional)  
**Branch desta execução:** `fase-3-3-validacao-cruzada-marts-minimos`
**Status após auditoria:** **aprovada e encerrada** — ver `Docs/fase-3-3-parecer-auditoria-2026-04-08.md`

---

## 1) Objetivo

Executar validação cruzada mínima dos 3 marts da Fase 3.2 contra a camada curada (`cur_*`), confirmando consistência estrutural, reconciliação de totais e aderência aos limites/regras já aprovados.

---

## 2) Escopo executado

Marts validadas:
1. `mart_ubs_monitoring_v1`
2. `mart_project_management_v1`
3. `mart_dashboard_export_v1`

Critérios aplicados:
- reconciliação de cardinalidade esperada vs. entregue;
- reconciliação de totais globais;
- checagens de plausibilidade de métricas (limites e proporções);
- verificação explícita de métricas indisponíveis sinalizadas.

---

## 3) Resultados da validação cruzada

## 3.1 `mart_ubs_monitoring_v1`

- `expected_rows` (por `health_unit_key` curado com bucket nulo): **10**
- `mart_rows`: **10**
- `rowcount_mismatch`: **0**
- violações `baseline_completed_count_ubs > participant_count_ubs`: **0**
- violações `active_participants_ubs > participant_count_ubs`: **0**
- violações `abandoned_participants_count_ubs > participant_count_ubs`: **0**
- violações `phq9_score_avg_ubs` fora de [0, 27]: **0**
- violações `gad7_score_avg_ubs` fora de [0, 21]: **0**

**Classificação:** sem ressalvas.

## 3.2 `mart_project_management_v1`

- `city_rows_expected` (com `COALESCE(ubs_city, '')`): **3**
- `city_rows_mart`: **3**
- `city_rowcount_mismatch`: **0**
- `participants_global_expected`: **458**
- `participants_global_mart`: **458**
- `global_participant_mismatch`: **0**
- `city_participant_sum`: **458**
- `city_sum_vs_global_mismatch`: **0**
- violações `active_in_journey_count > participant_count`: **0**
- violações `abandoned_participants_count > participant_count`: **0**
- violações `data_quality_ok_percent` fora de [0, 100]: **0**
- violações `participants_with_score_percent` fora de [0, 100]: **0**

Observação técnica: a linha CITY com chave vazia representa bucket de cidade nula na origem curada; após reconciliar com bucket explícito (`COALESCE`), não há discrepância material.

**Classificação:** sem ressalvas.

## 3.3 `mart_dashboard_export_v1`

- `ubs_count_expected`: **10**
- `city_count_expected` (com bucket nulo): **3**
- `total_rows_expected = 5*ubs + city + 6`: **59**
- `total_rows_mart`: **59**
- `rowcount_mismatch`: **0**
- `participant_count_global_mismatch_count`: **0**
- linhas `metric_status = 'INDISPONIVEL'`: **4** (esperado: 4)

**Classificação:** sem ressalvas.

---

## 4) Consolidação de achados

- Não foi identificado erro material.
- Não foi identificada divergência impeditiva entre marts e camada curada.
- Limitações herdadas (D1, N7, IGI/notificações/chatbot/help indisponíveis) permanecem transparentes e coerentes com a documentação da Fase 3.

---

## 5) Veredito formal da fase

> **Fase 3.3: VALIDADA (sem ressalvas materiais).**

Critérios para avanço técnico atendidos para o escopo mínimo aprovado desta fase.

Situação documental após auditoria formal: **Fase 3.3 aprovada e encerrada**, conforme `Docs/fase-3-3-parecer-auditoria-2026-04-08.md`.

---

## 6) Fora de escopo (não executado)

- Não houve alteração de regra de negócio nos SQLs.
- Não houve início da Fase 4.
- Não houve reabertura de Fase 2/3.2 por ausência de bloqueador material.
