# Fase C — Integração BigQuery → Dashboard

## Introdução
Esta fase documenta a transição do dashboard CONEMO para o BigQuery como fonte de dados canônica, eliminando a dependência do arquivo Parquet local desatualizado.

---

## Fase C.2 — Implementação controlada

### Objetivo
Substituir a leitura do Parquet por leitura direta via BigQuery (dataset `firestore_curated`), preservando o contrato do DataFrame e o comportamento funcional do Dashboard.

### Fontes usadas
- **Canônica:** `conemo-412202.firestore_curated.cur_participant_current_v1`
- **Suporte:**
    - `conemo-412202.firestore_curated.cur_health_unit_v1`
    - `conemo-412202.firestore_curated.cur_session_current_v1`
    - `conemo-412202.firestore_curated.cur_score_current_v1`
- **Raw (Campos de Perfil):** `conemo-412202.firestore_export.users_raw_latest`

### Arquivos modificados
- `Code/PY/dashboard_conemo.py`

### Query BigQuery usada
```sql
WITH phq AS (
  SELECT participant_master_id, score_value as phq_score
  FROM `conemo-412202.firestore_curated.cur_score_current_v1`
  WHERE score_type = 'PHQ'
),
gad AS (
  SELECT participant_master_id, score_value as gad_score
  FROM `conemo-412202.firestore_curated.cur_score_current_v1`
  WHERE score_type = 'GAD'
),
raw_perfil AS (
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
  phq.phq_score,
  gad.gad_score,
  p.created_at,
  UNIX_SECONDS(p.created_at) as created_at_seconds,
  p.is_test_record
FROM `conemo-412202.firestore_curated.cur_participant_current_v1` p
LEFT JOIN `conemo-412202.firestore_curated.cur_session_current_v1` s ON p.participant_master_id = s.participant_master_id
LEFT JOIN `conemo-412202.firestore_curated.cur_health_unit_v1` u ON p.health_unit_key = u.health_unit_key
LEFT JOIN phq ON p.participant_master_id = phq.participant_master_id
LEFT JOIN gad ON p.participant_master_id = gad.participant_master_id
LEFT JOIN raw_perfil r ON p.source_user_id = r.source_user_id
WHERE p.created_at >= TIMESTAMP('2026-01-25 00:00:00 UTC')
  AND p.is_test_record = false
```

### Campos preservados no DataFrame
O contrato de dados foi preservado integralmente, garantindo compatibilidade com os componentes visuais Plotly e as métricas Streamlit.

### Campos PII mantidos por decisão do professor
Por decisão do professor, nesta etapa técnica as PII necessárias ao contrato atual do dashboard foram mantidas para garantir a continuidade funcional.
- `user_name`: Nome do participante (Fonte: `users_raw_latest`).
- `email`: E-mail (Fonte: `users_raw_latest`), mascarado em Python para exibição.
- `age`: Calculada a partir de `birthDate._seconds` (Fonte: `users_raw_latest`).

### Filtro temporal aplicado
`created_at >= TIMESTAMP('2026-01-25 00:00:00 UTC')`

### Flags aplicadas
- `is_test_record = false` (Filtro nativo da camada curada).
- Flags legadas (`is_test`, etc.) foram inicializadas como `False` no DataFrame resultante para evitar quebra de filtros visuais antigos.

### Tratamento de missing
Campos `null` no BigQuery são convertidos para "N/A" (UBS, Cidade, Nome) ou "N/D" (Email) para garantir legibilidade no Dashboard.

### Cache e TTL
`@st.cache_data(ttl=900)` — Cache de 15 minutos aplicado à função `load_data()`.

### Comportamento do botão 🔄
O botão `🔄 Atualizar dados` executa `st.cache_data.clear()`, forçando uma nova consulta ao BigQuery.

### Timestamp
O timestamp exibido na sidebar reflete o momento da última consulta bem-sucedida ao BigQuery (armazenado em `st.session_state`).

### Fallback Parquet
Implementado fallback técnico automático: caso a conexão com o BigQuery falhe, o dashboard tenta carregar o arquivo Parquet local e exibe um aviso (`st.warning`) ao usuário.

### Testes realizados
- Teste de execução técnica (Bare mode): Sucesso.
- Teste de contrato de dados: Colunas e tipos confirmados.
- Teste de filtro temporal: Confirmado corte em 2026-01-25.

### Limitações
- A dependência da camada Raw para o cálculo de idade introduz um custo de parsing de JSON.
- A anonimização de PII ainda não foi implementada.

### Pendências para C.3
- Validação formal pela diretoria do CONEMO.
- Remoção definitiva da lógica de fallback Parquet (após estabilidade).

---

## Decisões Vinculantes da Coordenação
- **Canonicidade:** O BigQuery é a fonte canônica vigente. O Parquet está desatualizado e não deve ser usado como critério de verdade analítica.
- **PII:** Nesta etapa técnica as PII necessárias ao contrato atual do dashboard serão mantidas. A anonimização será tratada em fase posterior.
- **Operacionalidade:** O dashboard integrado ao BigQuery não está autorizado para uso operacional antes da validação formal da diretoria do CONEMO.

---
**Executor:** Gemini CLI Agent  
**Data:** 2026-04-24
