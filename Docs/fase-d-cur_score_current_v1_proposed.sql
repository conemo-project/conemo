-- Autor: Ricardo Ceneviva
-- Data: 2026-04-26
-- Projeto: CONEMO

WITH user_form_scores AS (
  -- Extração de scores de triagem (Baseline) da users_raw_latest
  SELECT
    document_id                                                AS participant_id,
    'users_raw_latest'                                         AS score_source,
    'PHQ'                                                      AS instrument,
    SAFE_CAST(
      (SELECT JSON_VALUE(s, '$.score')
       FROM UNNEST(JSON_EXTRACT_ARRAY(DATA, '$.forms[0].scores')) AS s
       WHERE JSON_VALUE(s, '$.type') = 'PHQ'
       LIMIT 1)
      AS FLOAT64
    )                                                          AS score_total,
    TIMESTAMP_SECONDS(
      SAFE_CAST(JSON_VALUE(DATA, '$.forms[0].date._seconds') AS INT64)
    )                                                          AS score_timestamp,
    document_id                                                AS source_document_id,
    document_name                                              AS source_document_name,
    'd2_v1'                                                    AS score_rule_version
  FROM `conemo-412202.firestore_export.users_raw_latest`
  WHERE document_id IS NOT NULL
    AND JSON_EXTRACT_ARRAY(DATA, '$.forms[0].scores') IS NOT NULL

  UNION ALL

  SELECT
    document_id                                                AS participant_id,
    'users_raw_latest'                                         AS score_source,
    'GAD'                                                      AS instrument,
    SAFE_CAST(
      (SELECT JSON_VALUE(s, '$.score')
       FROM UNNEST(JSON_EXTRACT_ARRAY(DATA, '$.forms[0].scores')) AS s
       WHERE JSON_VALUE(s, '$.type') = 'GAD'
       LIMIT 1)
      AS FLOAT64
    )                                                          AS score_total,
    TIMESTAMP_SECONDS(
      SAFE_CAST(JSON_VALUE(DATA, '$.forms[0].date._seconds') AS INT64)
    )                                                          AS score_timestamp,
    document_id,
    document_name,
    'd2_v1'
  FROM `conemo-412202.firestore_export.users_raw_latest`
  WHERE document_id IS NOT NULL
    AND JSON_EXTRACT_ARRAY(DATA, '$.forms[0].scores') IS NOT NULL
),

journey_scores AS (
  -- Extração de scores de progresso da journeys_raw_latest
  -- Correção D.2: Uso de REGEXP_EXTRACT em document_name para obter participant_id
  SELECT
    REGEXP_EXTRACT(document_name, r'documents/users/([^/]+)')  AS participant_id,
    'journeys_raw_latest'                                      AS score_source,
    CASE
      WHEN UPPER(JSON_VALUE(DATA, '$.type')) IN ('GAD', 'ANXIETY') THEN 'GAD_JOURNEY'
      WHEN UPPER(JSON_VALUE(DATA, '$.type')) IN ('PHQ', 'DEPRESSION', 'DEPRESSAO', 'DEPRESSÃO') THEN 'PHQ_JOURNEY'
      ELSE 'OTHER_JOURNEY'
    END                                                        AS instrument,
    SAFE_CAST(JSON_VALUE(DATA, '$.score') AS FLOAT64)          AS score_total,
    TIMESTAMP_SECONDS(
      SAFE_CAST(JSON_VALUE(DATA, '$.lastAccess._seconds') AS INT64)
    )                                                          AS score_timestamp,
    document_id                                                AS source_document_id,
    document_name                                              AS source_document_name,
    'd2_v1'                                                    AS score_rule_version
  FROM `conemo-412202.firestore_export.journeys_raw_latest`
  WHERE JSON_VALUE(DATA, '$.score') IS NOT NULL
)

SELECT * FROM user_form_scores
UNION ALL
SELECT * FROM journey_scores
WHERE participant_id IS NOT NULL
