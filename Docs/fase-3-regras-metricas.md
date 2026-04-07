# Fase 3 — Regras de cálculo de métricas dos marts

**Data:** 2026-04-07  
**Status:** Definições formais de cada métrica — referência para SQL  
**Autor:** Ricardo Ceneviva

---

## 1) Objetivo

Documento de referência que define **formalmente** cada métrica dos marts com:
- Numerador (definição precisa)
- Denominador (população de referência)
- Filtros (condições de elegibilidade)
- Período (janela temporal padrão)
- Notas de interpretação

Este documento é a "receita" que guia a implementação SQL. Não é código; é especificação de negócio.

---

## 2) Métricas de `mart_ubs_monitoring_v1`

Granularidade: **1 linha por (health_unit_key, period)**

### 2.1 `participant_count_ubs`

**Definição:** Número total de participantes cadastrados na UBS no período.

**Numerador:** 
```
COUNT(DISTINCT participant_master_id) 
WHERE health_unit_key IS NOT NULL 
  AND is_test_record = FALSE
```

**Denominador:** —

**Período:** Configurável (padrão: acumulado desde início de coleta)

**Aggregação:** GROUP BY health_unit_key

**Nota:** Contagem simples, sem restrição de status de participante (todos os inscritos contam).

---

### 2.2 `baseline_completed_count_ubs`

**Definição:** Número de participantes que completaram o baseline no aplicativo.

**Numerador:**
```
COUNT(DISTINCT participant_master_id)
WHERE health_unit_key IS NOT NULL
  AND is_test_record = FALSE
  AND EXISTS (
    SELECT 1 FROM cur_session_current_v1 
    WHERE session_number >= 1 
      AND participant_master_id = cur_participant.participant_master_id
  )
```

**Denominador:** `participant_count_ubs` (opcional, para taxa)

**Período:** Configurável

**Agregação:** GROUP BY health_unit_key

**Nota:** Proxy: presença de sessão número ≥ 1. Indica que participante entrou no aplicativo.

---

### 2.3 `active_participants_ubs`

**Definição:** Participantes com jornada ativa nesta semana.

**Numerador:**
```
COUNT(DISTINCT participant_master_id)
WHERE health_unit_key IS NOT NULL
  AND is_test_record = FALSE
  AND EXISTS (
    SELECT 1 FROM cur_journey_current_v1
    WHERE journey_status = 'ACTIVE'
      AND journey_updated_at >= CURRENT_DATE() - 7
      AND participant_master_id = cur_participant.participant_master_id
  )
```

**Denominador:** `baseline_completed_count_ubs` (opcional, para taxa)

**Período:** Última 7 dias rolling

**Agregação:** GROUP BY health_unit_key

**Nota:** Indicador de engajamento recente.

---

### 2.4 `overdue_sessions_count_ubs`

**Definição:** Número de sessões em atraso (devidas mas não completadas).

**Numerador:**
```
COUNT(DISTINCT session_id)  -- ou tupla (participant_master_id, journey_id, session_number)
WHERE health_unit_key IS NOT NULL
  AND is_test_record = FALSE
  AND session_status = 'OVERDUE'
```

**Período:** Período de referência (padrão: últimas 30 dias)

**Agregação:** GROUP BY health_unit_key

**Nota:** Sessão "em atraso" é aquela com `session_status = 'OVERDUE'`, derivada em `cur_session_current_v1`.

---

### 2.5 `abandoned_journeys_count_ubs`

**Definição:** Número de participantes que abandonaram jornada (não mais ativos após iniciar).

**Numerador:**
```
COUNT(DISTINCT participant_master_id)
WHERE health_unit_key IS NOT NULL
  AND is_test_record = FALSE
  AND EXISTS (
    SELECT 1 FROM cur_journey_current_v1
    WHERE journey_status = 'INACTIVE'
      AND participant_master_id = cur_participant.participant_master_id
  )
```

**Período:** Configurável

**Agregação:** GROUP BY health_unit_key

**Nota:** Proxy para abandono: jornada com status INACTIVE. Não diferencia abandono porque fez progresso vs abandono precoce.

---

### 2.6 `phq9_score_avg_ubs`

**Definição:** Média aritmética de escores PHQ-9 iniciais por UBS.

**Numerador:**
```
AVG(score_value)
WHERE health_unit_key IS NOT NULL
  AND is_test_record = FALSE
  AND score_type = 'PHQ'
  AND score_source = 'FORM_INITIAL'
  AND score_value IS NOT NULL
```

**Denominador:** —

**Período:** Período de coleta (padrão: últimos 30 dias de coletas)

**Agregação:** GROUP BY health_unit_key

**Nota:** Score de triagem inicial apenas. Não inclui reavaliações.

---

### 2.7 `phq9_distribution_ubs`

**Definição:** Distribuição de escores PHQ-9 por faixa de gravidade.

**Categorização:**
- Mínimo: 0–4
- Leve: 5–9
- Moderado: 10–14
- Moderadamente severo: 15–19
- Severo: 20–27

**Numerador (por categoria):**
```
COUNT(DISTINCT participant_master_id)
WHERE health_unit_key IS NOT NULL
  AND is_test_record = FALSE
  AND score_type = 'PHQ'
  AND score_source = 'FORM_INITIAL'
  AND score_value BETWEEN [intervalo da categoria]
```

**Período:** Período de coleta

**Agregação:** GROUP BY health_unit_key, phq9_severity_category

**Nota:** Produz 5 linhas por UBS (uma por categoria de gravidade).

---

### 2.8 `gad7_score_avg_ubs`

**Definição:** Média aritmética de escores GAD-7 iniciais por UBS.

**Numerador:**
```
AVG(score_value)
WHERE health_unit_key IS NOT NULL
  AND is_test_record = FALSE
  AND score_type = 'GAD'
  AND score_source = 'FORM_INITIAL'
  AND score_value IS NOT NULL
```

**Período:** Período de coleta

**Agregação:** GROUP BY health_unit_key

**Nota:** Idem PHQ-9.

---

### 2.9 `gad7_distribution_ubs`

**Definição:** Distribuição de escores GAD-7 por faixa de gravidade.

**Categorização:**
- Mínimo: 0–4
- Leve: 5–9
- Moderado: 10–14
- Severo: 15–20

**Implementação:** Idem PHQ-9, adaptar intervalos.

---

## 3) Métricas de `mart_project_management_v1`

Granularidade: **1 linha por (period)** ou **1 linha per (city)** ou **1 linha per (period, city)** — a definir por requisito.

### 3.1 `web_initiated_count_global`

**Definição:** Total de participantes que iniciaram rastreio web (registro de participante).

**Numerador:**
```
COUNT(DISTINCT participant_master_id)
WHERE is_test_record = FALSE
```

**Período:** Período de coleta (padrão: acumulado desde início)

**Agregação:** Global (sem GROUP BY) ou GROUP BY city se variante por cidade

**Nota:** Inclui todos os participantes únicos no sistema, independentemente de status.

---

### 3.2 `baseline_completed_count_global`

**Definição:** Total de participantes com baseline completado no app.

**Numerador:**
```
COUNT(DISTINCT participant_master_id)
WHERE is_test_record = FALSE
  AND EXISTS (
    SELECT 1 FROM cur_session_current_v1 
    WHERE session_number >= 1
  )
```

**Período:** Período de coleta

**Agregação:** Global

**Taxa (opcional):** `baseline_completed_count_global / web_initiated_count_global`

---

### 3.3 `active_in_journey_count_global`

**Definição:** Participantes ativos em jornada nesta semana, globalmente.

**Numerador:**
```
COUNT(DISTINCT participant_master_id)
WHERE is_test_record = FALSE
  AND EXISTS (
    SELECT 1 FROM cur_journey_current_v1
    WHERE journey_status = 'ACTIVE'
      AND journey_updated_at >= CURRENT_DATE() - 7
  )
```

**Período:** Última 7 dias rolling

**Agregação:** Global

---

### 3.4 `abandoned_journeys_count_global`

**Definição:** Participantes que abandonaram jornada (total global).

**Numerador:**
```
COUNT(DISTINCT participant_master_id)
WHERE is_test_record = FALSE
  AND EXISTS (
    SELECT 1 FROM cur_journey_current_v1
    WHERE journey_status = 'INACTIVE'
  )
```

**Período:** Período de coleta

**Agregação:** Global

**Taxa (opcional):** `abandoned_journeys_count_global / baseline_completed_count_global`

---

### 3.5 `avg_days_web_to_app`

**Definição:** Tempo médio (em dias) entre registro web e primeira sessão no app.

**Numerador:**
```
AVG(DATE_DIFF(FIRST session_number=1 .date, participant.created_at, DAY))
WHERE is_test_record = FALSE
  AND EXISTS (sessão nível 1 ou maior)
```

**Período:** Período de coleta

**Agregação:** Global

**Nota de limite:** Implementação depende de timestamps disponíveis em `cur_session_current_v1`. Se `event_timestamp` for NULL (N7), usar `journey_updated_at` como proxy.

---

### 3.6 `active_ubs_count_global`

**Definição:** Número de UBS com pelo menos um participante ativo nesta semana.

**Numerador:**
```
COUNT(DISTINCT health_unit_key)
WHERE EXISTS (
  SELECT 1 FROM cur_participant_current_v1 p
  WHERE p.health_unit_key = health_unit.health_unit_key
    AND p.is_test_record = FALSE
    AND EXISTS (
      SELECT 1 FROM cur_journey_current_v1 j
      WHERE j.journey_status = 'ACTIVE'
        AND j.journey_updated_at >= CURRENT_DATE() - 7
        AND j.participant_master_id = p.participant_master_id
    )
)
```

**Período:** Última 7 dias rolling

**Agregação:** Global

---

### 3.7 `data_quality_ok_percent_global`

**Definição:** Proporção de registros de participante sem avisos de qualidade.

**Numerador:**
```
COUNT(DISTINCT participant_master_id)
WHERE record_quality_flag = 'OK'
  AND is_test_record = FALSE
```

**Denominador:**
```
COUNT(DISTINCT participant_master_id)
WHERE is_test_record = FALSE
```

**Período:** Período de coleta

**Agregação:** Global

**Taxa:**
```
Numerador / Denominador
```

---

## 4) Métricas de `mart_dashboard_export_v1`

Granularidade: **1 linha por combinação relevante** (ex.: participante + UBS + período + tipo_métrica)

Esta mart é de "exportação", serve para alimentar CSV ou Streamlit sem transformação adicional.

### 4.1 Estrutura base

Cada linha contém:

| Campo | Tipo | Definição |
|---|---|---|
| `period` | DATE | Data ou período (início de semana/mês) |
| `health_unit_key` | STRING | Chave de UBS |
| `ubs_name` | STRING | Nome padronizado da UBS |
| `ubs_city` | STRING | Cidade da UBS |
| `journey_type` | STRING | Tipo de jornada (DEPRESSION, ANXIETY, BOTH, UNKNOWN) |
| `metric_name` | STRING | Nome da métrica (ex: "participant_count", "phq9_avg") |
| `metric_value` | NUMERIC | Valor da métrica |
| `metric_denominator` | NUMERIC | Denominador (se aplicável para taxa) |
| `metric_rate_percent` | NUMERIC | Taxa calculada (se aplicável) |
| `data_quality_flag` | STRING | OK / WARN / FAIL |
| `timestamp_load` | TIMESTAMP | Timestamp de carga da vista |

### 4.2 Exemplo de linha

```
period: 2026-04-07
health_unit_key: UBS_CENTRAL_01
ubs_name: UBS Central da Zona Norte
ubs_city: SAO PAULO
journey_type: DEPRESSION
metric_name: active_participants_count
metric_value: 42
metric_denominator: 150
metric_rate_percent: 28.0
data_quality_flag: OK
timestamp_load: 2026-04-07T09:30:00Z
```

---

## 5) Notas operacionais

### 5.1 Período padrão

- Métricas de adesão/atividade: últimos 7 dias (rolling)
- Métricas de escores: últimos 30 dias de coletas
- Métricas de funil: acumulado desde início de projeto
- Métricas de gestão: período semanal ou mensal (configurável)

### 5.2 Tratamento de nulos

- Scores NULL são **excluídos** de AVG (não como 0)
- Contagens com zero valores apresentam resultado 0 (não NULL)
- Taxa = NULL se denominador = 0

### 5.3 Pressuposição zero de produção

Toda métrica que dependa de timestamps ou de campo não implementado em Fase 2 será marcada com:
```
-- AVISO: Depende de N7 (event_timestamp) não implementado em Fase 2.
--        Valores provisórios até validação.
```

---

## 6) Validação de cada métrica em Etapa 3.3

Cada métrica terá **query de validação cruzada** que:

1. Conta registros esperados
2. Verifica faixa de valores (ex: scores entre 0–27 para PHQ)
3. Compara contra view de origem (ex.: soma em mart_ubs_monitoring ≤ soma em cur_participant)
4. Valida sem NULLs onde esperado

---

**Data de aprovação destas regras:** [a preencher]  
**Aprovador:** [Professor/Revisor]

