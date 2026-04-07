-- =============================================================================
-- cur_score_current_v1.sql
-- Entidade: Escores clínicos básicos no recorte atual por participante
-- Fontes:
--   (1) conemo-412202.firestore_export.users_raw_latest → forms[0].scores[]
--   (2) conemo-412202.firestore_export.journeys_raw_latest → $.score
-- Destino: conemo-412202.firestore_curated.cur_score_current_v1
-- Camada: B — curada compartilhada (BigQuery-first)
-- Versão: v1
-- Data: 2026-04-07
-- Fase: 2 — Implementação mínima da camada curada
-- Branch: fase-2-implementacao-camada-curada-minima
-- =============================================================================

-- ----------------------------------------------------------------------------
-- OBJETIVO DESTA VIEW
-- ----------------------------------------------------------------------------
-- Registrar os escores clínicos disponíveis para cada participante no recorte
-- atual. Granularidade: 1 linha por participant_master_id × score_type ×
-- score_reference_date.
--
-- Esta entidade suporta monitoramento clínico agregado por UBS, acompanhamento
-- de trajetória terapêutica e alertas de piora clínica (Fase futura).
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- FONTES DE ESCORE (N5 documentada na verificação técnica 2.1)
-- ----------------------------------------------------------------------------
-- Fonte 1 — Escores de formulário inicial (rastreio/baseline):
--   users_raw_latest.DATA.$.forms[0].scores[]
--   Contém: [{type: "PHQ", score: N}, {type: "GAD", score: N}]
--   Score_reference_date: forms[0].date._seconds (data do primeiro formulário)
--
-- Fonte 2 — Score agregado de jornada:
--   journeys_raw_latest.DATA.$.score
--   Tipo inferido: journeys_raw_latest.DATA.$.type (GAD ou DEPRESSION)
--   Este score é distinto dos escores de formulário — representa progresso
--   acumulado na jornada, não uma medida clínica padronizada.
--   score_reference_date: lastAccess._seconds (proxy temporal disponível)
--
-- NOTA DE INTERPRETAÇÃO:
--   PHQ/GAD de forms[0] são escores de triagem inicial (T0).
--   PHQ_JOURNEY/GAD_JOURNEY são scores operacionais de progresso de jornada.
--   Não devem ser comparados diretamente sem contextualização analítica.
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- NOTAS DE IMPLEMENTAÇÃO
-- ----------------------------------------------------------------------------
-- UNNEST + JSON_EXTRACT_ARRAY:
--   BigQuery não suporta JSON_VALUE diretamente em índices dinâmicos de array.
--   Usamos JSON_EXTRACT_ARRAY + UNNEST para expandir o array scores[] e
--   filtrar por type. Isso garante que múltiplos escores no mesmo formulário
--   sejam tratados corretamente.
--
-- score_quality_flag (DERIVADO):
--   FAIL  → score_value nulo (escore ausente ou inválido)
--   WARN  → score_value presente mas score_reference_date nulo
--   OK    → score_value e data de referência presentes
-- ----------------------------------------------------------------------------

CREATE OR REPLACE VIEW `conemo-412202.firestore_curated.cur_score_current_v1` AS

-- ============================================================================
-- FONTE 1: Escores de formulário inicial (users_raw_latest.forms[0].scores)
-- ============================================================================
-- Extração de PHQ e GAD de rastreio via UNNEST do array JSON.
-- Cada escore gera uma linha separada (unpivot natural).
WITH user_form_scores AS (

  -- Extração do escore PHQ do primeiro formulário do usuário
  SELECT
    document_id                                                AS participant_master_id,
    document_id                                                AS source_document_id,
    'PHQ'                                                      AS score_type,

    -- score_value: STRING → FLOAT64. Registros não numéricos retornam NULL.
    SAFE_CAST(
      (SELECT JSON_VALUE(s, '$.score')
       FROM UNNEST(JSON_EXTRACT_ARRAY(DATA, '$.forms[0].scores')) AS s
       WHERE JSON_VALUE(s, '$.type') = 'PHQ'
       LIMIT 1)
      AS FLOAT64
    )                                                          AS score_value,

    -- Data de referência: timestamp do primeiro formulário
    TIMESTAMP_SECONDS(
      SAFE_CAST(JSON_VALUE(DATA, '$.forms[0].date._seconds') AS INT64)
    )                                                          AS score_reference_date,

    'FORM_INITIAL'                                             AS score_source

  FROM `conemo-412202.firestore_export.users_raw_latest`
  WHERE document_id IS NOT NULL
    AND JSON_EXTRACT_ARRAY(DATA, '$.forms[0].scores') IS NOT NULL

  UNION ALL

  -- Extração do escore GAD do primeiro formulário do usuário
  SELECT
    document_id,
    document_id,
    'GAD'                                                      AS score_type,

    SAFE_CAST(
      (SELECT JSON_VALUE(s, '$.score')
       FROM UNNEST(JSON_EXTRACT_ARRAY(DATA, '$.forms[0].scores')) AS s
       WHERE JSON_VALUE(s, '$.type') = 'GAD'
       LIMIT 1)
      AS FLOAT64
    )                                                          AS score_value,

    TIMESTAMP_SECONDS(
      SAFE_CAST(JSON_VALUE(DATA, '$.forms[0].date._seconds') AS INT64)
    )                                                          AS score_reference_date,

    'FORM_INITIAL'                                             AS score_source

  FROM `conemo-412202.firestore_export.users_raw_latest`
  WHERE document_id IS NOT NULL
    AND JSON_EXTRACT_ARRAY(DATA, '$.forms[0].scores') IS NOT NULL
),

-- ============================================================================
-- FONTE 2: Score de progresso de jornada (journeys_raw_latest.$.score)
-- ============================================================================
-- Score agregado por jornada. O tipo é inferido do tipo da jornada.
-- Este é um indicador operacional distinto dos escores de triagem.
journey_scores AS (
  SELECT
    JSON_VALUE(path_params, '$.userId')                        AS participant_master_id,
    document_id                                                AS source_document_id,

    -- Tipo do escore de jornada: derivado do tipo da jornada (N5)
    CASE
      WHEN UPPER(JSON_VALUE(DATA, '$.type')) IN ('GAD', 'ANXIETY') THEN 'GAD_JOURNEY'
      WHEN UPPER(JSON_VALUE(DATA, '$.type')) IN ('PHQ', 'DEPRESSION',
           'DEPRESSAO', 'DEPRESSÃO')                          THEN 'PHQ_JOURNEY'
      ELSE 'OTHER_JOURNEY'
    END                                                        AS score_type,

    -- score_value: score agregado da jornada (FLOAT64)
    SAFE_CAST(JSON_VALUE(DATA, '$.score') AS FLOAT64)          AS score_value,

    -- score_reference_date: proxy via lastAccess (melhor disponível nesta fonte)
    TIMESTAMP_SECONDS(
      SAFE_CAST(JSON_VALUE(DATA, '$.lastAccess._seconds') AS INT64)
    )                                                          AS score_reference_date,

    'JOURNEY_AGGREGATE'                                        AS score_source

  FROM `conemo-412202.firestore_export.journeys_raw_latest`
  WHERE JSON_VALUE(DATA, '$.score') IS NOT NULL
    AND JSON_VALUE(path_params, '$.userId') IS NOT NULL
    AND TRIM(JSON_VALUE(path_params, '$.userId')) != ''
),

-- ============================================================================
-- UNIÃO DAS FONTES
-- ============================================================================
-- Combinamos os escores de formulário com os scores de jornada.
-- A distinção de score_source permite filtragem posterior.
all_scores AS (
  SELECT * FROM user_form_scores
  WHERE score_value IS NOT NULL  -- Excluir escores sem valor calculável

  UNION ALL

  SELECT
    participant_master_id,
    source_document_id,
    score_type,
    score_value,
    score_reference_date,
    score_source
  FROM journey_scores
),

-- ============================================================================
-- DERIVAÇÃO DE score_quality_flag
-- ============================================================================
scores_with_quality AS (
  SELECT
    participant_master_id,
    source_document_id,
    'RESOLVED_DOCUMENT'                                        AS id_reconciliation_status,
    score_type,
    score_value,
    score_reference_date,
    score_source,

    -- Regras de qualidade do escore:
    --   FAIL → score_value nulo (escore ausente ou não parseável)
    --   WARN → score presente mas data de referência ausente
    --   OK   → score e data de referência disponíveis
    CASE
      WHEN score_value IS NULL               THEN 'FAIL'
      WHEN score_reference_date IS NULL      THEN 'WARN'
      ELSE 'OK'
    END                                                        AS score_quality_flag

  FROM all_scores
)

-- ============================================================================
-- RESULTADO FINAL
-- ============================================================================
-- Uma linha por participant_master_id × score_type × score_reference_date.
-- A distinção de score_source permite análise separada por tipo de origem.
SELECT
  participant_master_id,
  source_document_id,
  id_reconciliation_status,
  score_type,
  score_value,
  score_reference_date,
  score_source,
  score_quality_flag

FROM scores_with_quality
WHERE participant_master_id IS NOT NULL
;
