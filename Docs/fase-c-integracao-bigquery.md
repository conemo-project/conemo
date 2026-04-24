# Fase C — Integração BigQuery → Dashboard

## Introdução
Esta fase documenta a transição do dashboard CONEMO para o BigQuery como fonte de dados canônica, eliminando a dependência do arquivo Parquet local desatualizado.

---

## Fase C.2 — Implementação controlada (Revisada e Corrigida)

### Objetivo
Substituir a leitura do Parquet por leitura direta via BigQuery (dataset `firestore_curated`), preservando o contrato do DataFrame e o comportamento funcional do Dashboard. 

**Correção:** A query foi ajustada para degradar temporariamente os campos `phq_score` e `gad_score` para `NULL` devido a um erro de schema identificado na view `cur_score_current_v1` do BigQuery.

### Fontes usadas
- **Canônica:** `conemo-412202.firestore_curated.cur_participant_current_v1`
- **Suporte:**
    - `conemo-412202.firestore_curated.cur_health_unit_v1`
    - `conemo-412202.firestore_curated.cur_session_current_v1`
- **Raw (Campos de Perfil):** `conemo-412202.firestore_export.users_raw_latest`

### Arquivos modificados
- `Code/PY/dashboard_conemo.py`

### Query BigQuery corrigida
```sql
WITH raw_perfil AS (
  SELECT 
    document_id as source_user_id,
    JSON_EXTRACT_SCALAR(data, '$.name') as user_name,
    JSON_EXTRACT_SCALAR(data, '$.email') as email,
    JSON_EXTRACT_SCALAR(data, '$.birthDate._seconds') as birth_seconds
  FROM `conemo-412202.firestore_export.users_raw_latest`
)
SELECT 
  p.participant_master_id as user_id,
  s.session_number as sessionNumber,
  s.is_completed as isCompleted,
  CAST(s.event_timestamp AS STRING) as completedDate,
  u.ubs_name,
  u.ubs_city,
  p.gender,
  r.user_name,
  r.email,
  CAST(r.birth_seconds AS INT64) as birth_seconds,
  CAST(NULL AS FLOAT64) as phq_score, -- Degradado temporariamente por erro na view original
  CAST(NULL AS FLOAT64) as gad_score, -- Degradado temporariamente por erro na view original
  p.created_at,
  UNIX_SECONDS(p.created_at) as created_at_seconds,
  p.is_test_record
FROM `conemo-412202.firestore_curated.cur_participant_current_v1` p
LEFT JOIN `conemo-412202.firestore_curated.cur_session_current_v1` s ON p.participant_master_id = s.participant_master_id
LEFT JOIN `conemo-412202.firestore_curated.cur_health_unit_v1` u ON p.health_unit_key = u.health_unit_key
LEFT JOIN raw_perfil r ON p.source_user_id = r.source_user_id
WHERE p.created_at >= TIMESTAMP('2026-01-25 00:00:00 UTC')
  AND p.is_test_record = false
```

### Comprovação Técnica (Execução Real)
A integração foi validada em 2026-04-24 com os seguintes resultados:
- **Linhas retornadas:** 247
- **Participantes únicos:** 125
- **Filtro temporal:** Respeitado (Min CreatedAt: 2026-01-28)
- **Filtro flags:** Respeitado (is_test_record = False)

### Limitações e Bloqueios
- **Scores Clínicos:** Temporariamente indisponíveis (NULL) via BigQuery até saneamento da view `cur_score_current_v1`.
- **Dependência Raw:** O cálculo de idade ainda exige parsing de JSON da camada Raw.

---

## Decisões Vinculantes da Coordenação
- **Canonicidade:** O BigQuery é a fonte canônica vigente. O Parquet está desatualizado e não deve ser usado como critério de verdade analítica.
- **PII:** Nesta etapa técnica as PII necessárias ao contrato atual do dashboard serão mantidas. A anonimização será tratada em fase posterior.
- **Operacionalidade:** O dashboard integrado ao BigQuery não está autorizado para uso operacional antes da validação formal da diretoria do CONEMO.

---
**Executor:** Gemini CLI Agent  
**Data:** 2026-04-24
