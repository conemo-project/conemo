-- =============================================================================
-- Fase 3.2 — mart_dashboard_export_v1
-- Projeto: CONEMO | Camada: marts mínimos do dashboard
-- Destino: conemo-412202.firestore_curated.mart_dashboard_export_v1
-- =============================================================================
-- OBJETIVO (programação letrada)
-- Consolidar dimensões e métricas em formato de exportação (linha a linha),
-- pronto para consumo por Streamlit/CSV sem transformação estrutural adicional.
--
-- GRANULARIDADE
-- - 1 linha por período x escopo x métrica
-- - escopos: UBS, CITY, GLOBAL
--
-- FONTES AUTORIZADAS (somente Fase 2 curada)
-- - cur_participant_current_v1
-- - cur_health_unit_v1
-- - cur_session_current_v1
-- - cur_journey_current_v1
-- - cur_score_current_v1
--
-- LIMITES HERDADOS EXPLÍCITOS
-- - D1 mantido; D2 não reaberto
-- - N7 com proxy quando aplicável
-- - IGI, notificações, chatbot e help requests como INDISPONÍVEIS
-- =============================================================================
-- AVISO CRÍTICO — PRESSUPOSIÇÃO ZERO DE HOMOLOGAÇÃO EM PRODUÇÃO
-- Esta mart organiza métricas para consumo visual, mas não substitui a etapa
-- formal de validação cruzada da Fase 3.3.
-- =============================================================================

CREATE OR REPLACE VIEW `conemo-412202.firestore_curated.mart_dashboard_export_v1` AS
WITH
params AS (
  SELECT
    DATE_TRUNC(CURRENT_DATE(), WEEK(MONDAY)) AS period_start_date,
    CURRENT_DATE() AS period_end_date,
    CURRENT_TIMESTAMP() AS snapshot_timestamp
),

participant_base AS (
  SELECT
    p.participant_master_id,
    p.health_unit_key,
    h.ubs_name,
    h.ubs_city,
    p.created_at,
    p.record_quality_flag
  FROM `conemo-412202.firestore_curated.cur_participant_current_v1` p
  LEFT JOIN `conemo-412202.firestore_curated.cur_health_unit_v1` h
    ON p.health_unit_key = h.health_unit_key
),

session_base AS (
  SELECT
    pb.health_unit_key,
    pb.ubs_name,
    pb.ubs_city,
    s.participant_master_id,
    s.session_document_id,
    s.session_number,
    s.session_status
  FROM `conemo-412202.firestore_curated.cur_session_current_v1` s
  INNER JOIN participant_base pb
    ON pb.participant_master_id = s.participant_master_id
),

journey_base AS (
  SELECT
    pb.health_unit_key,
    pb.ubs_name,
    pb.ubs_city,
    j.participant_master_id,
    j.journey_type,
    j.journey_status,
    j.journey_updated_at
  FROM `conemo-412202.firestore_curated.cur_journey_current_v1` j
  INNER JOIN participant_base pb
    ON pb.participant_master_id = j.participant_master_id
),

score_base AS (
  SELECT
    pb.health_unit_key,
    pb.ubs_name,
    pb.ubs_city,
    sc.participant_master_id,
    sc.score_type,
    sc.score_value,
    sc.score_source
  FROM `conemo-412202.firestore_curated.cur_score_current_v1` sc
  INNER JOIN participant_base pb
    ON pb.participant_master_id = sc.participant_master_id
),

ubs_metric_rows AS (
  -- participant_count_ubs
  SELECT
    pb.health_unit_key,
    ANY_VALUE(pb.ubs_name) AS ubs_name,
    ANY_VALUE(pb.ubs_city) AS ubs_city,
    'UBS' AS scope_level,
    'ALL' AS journey_type,
    'participant_count_ubs' AS metric_name,
    CAST(COUNT(DISTINCT pb.participant_master_id) AS FLOAT64) AS metric_value,
    NULL AS metric_denominator,
    NULL AS metric_rate_percent,
    'COUNT' AS metric_unit,
    'OBSERVAVEL' AS metric_status
  FROM participant_base pb
  GROUP BY pb.health_unit_key

  UNION ALL

  -- active_participants_ubs
  SELECT
    jb.health_unit_key,
    ANY_VALUE(jb.ubs_name),
    ANY_VALUE(jb.ubs_city),
    'UBS',
    'ALL',
    'active_participants_ubs',
    CAST(COUNT(DISTINCT IF(jb.journey_status = 'ACTIVE', jb.participant_master_id, NULL)) AS FLOAT64),
    NULL,
    NULL,
    'COUNT',
    'OBSERVAVEL'
  FROM journey_base jb
  GROUP BY jb.health_unit_key

  UNION ALL

  -- overdue_sessions_ubs
  SELECT
    sb.health_unit_key,
    ANY_VALUE(sb.ubs_name),
    ANY_VALUE(sb.ubs_city),
    'UBS',
    'ALL',
    'overdue_sessions_ubs',
    CAST(COUNT(DISTINCT IF(sb.session_status = 'OVERDUE', sb.session_document_id, NULL)) AS FLOAT64),
    NULL,
    NULL,
    'COUNT',
    'OBSERVAVEL'
  FROM session_base sb
  GROUP BY sb.health_unit_key

  UNION ALL

  -- phq9_score_avg_ubs
  SELECT
    sc.health_unit_key,
    ANY_VALUE(sc.ubs_name),
    ANY_VALUE(sc.ubs_city),
    'UBS',
    'ALL',
    'phq9_score_avg_ubs',
    AVG(IF(sc.score_type = 'PHQ' AND sc.score_source = 'FORM_INITIAL', sc.score_value, NULL)),
    NULL,
    NULL,
    'AVG',
    'OBSERVAVEL'
  FROM score_base sc
  GROUP BY sc.health_unit_key

  UNION ALL

  -- gad7_score_avg_ubs
  SELECT
    sc.health_unit_key,
    ANY_VALUE(sc.ubs_name),
    ANY_VALUE(sc.ubs_city),
    'UBS',
    'ALL',
    'gad7_score_avg_ubs',
    AVG(IF(sc.score_type = 'GAD' AND sc.score_source = 'FORM_INITIAL', sc.score_value, NULL)),
    NULL,
    NULL,
    'AVG',
    'OBSERVAVEL'
  FROM score_base sc
  GROUP BY sc.health_unit_key
),

city_metric_rows AS (
  SELECT
    NULL AS health_unit_key,
    NULL AS ubs_name,
    pb.ubs_city AS ubs_city,
    'CITY' AS scope_level,
    'ALL' AS journey_type,
    'participant_count_city' AS metric_name,
    CAST(COUNT(DISTINCT pb.participant_master_id) AS FLOAT64) AS metric_value,
    NULL AS metric_denominator,
    NULL AS metric_rate_percent,
    'COUNT' AS metric_unit,
    'OBSERVAVEL' AS metric_status
  FROM participant_base pb
  GROUP BY pb.ubs_city
),

global_metric_rows AS (
  SELECT
    NULL AS health_unit_key,
    NULL AS ubs_name,
    'GLOBAL' AS ubs_city,
    'GLOBAL' AS scope_level,
    'ALL' AS journey_type,
    'participant_count_global' AS metric_name,
    CAST(COUNT(DISTINCT participant_master_id) AS FLOAT64) AS metric_value,
    NULL AS metric_denominator,
    NULL AS metric_rate_percent,
    'COUNT' AS metric_unit,
    'OBSERVAVEL' AS metric_status
  FROM participant_base

  UNION ALL

  SELECT
    NULL,
    NULL,
    'GLOBAL',
    'GLOBAL',
    'ALL',
    'data_quality_ok_percent_global',
    SAFE_DIVIDE(
      COUNT(DISTINCT IF(record_quality_flag = 'OK', participant_master_id, NULL)),
      NULLIF(COUNT(DISTINCT participant_master_id), 0)
    ) * 100,
    100,
    SAFE_DIVIDE(
      COUNT(DISTINCT IF(record_quality_flag = 'OK', participant_master_id, NULL)),
      NULLIF(COUNT(DISTINCT participant_master_id), 0)
    ) * 100,
    'PERCENT',
    'OBSERVAVEL'
  FROM participant_base
),

unavailable_metric_rows AS (
  -- Métricas indisponíveis explicitadas, não omitidas silenciosamente.
  SELECT NULL AS health_unit_key, NULL AS ubs_name, 'GLOBAL' AS ubs_city, 'GLOBAL' AS scope_level,
         'ALL' AS journey_type, 'igi_distribution_global' AS metric_name,
         NULL AS metric_value, NULL AS metric_denominator, NULL AS metric_rate_percent,
         'NA' AS metric_unit, 'INDISPONIVEL' AS metric_status
  UNION ALL
  SELECT NULL, NULL, 'GLOBAL', 'GLOBAL', 'ALL', 'notifications_global', NULL, NULL, NULL, 'NA', 'INDISPONIVEL'
  UNION ALL
  SELECT NULL, NULL, 'GLOBAL', 'GLOBAL', 'ALL', 'chatbot_global', NULL, NULL, NULL, 'NA', 'INDISPONIVEL'
  UNION ALL
  SELECT NULL, NULL, 'GLOBAL', 'GLOBAL', 'ALL', 'help_request_global', NULL, NULL, NULL, 'NA', 'INDISPONIVEL'
),

all_metric_rows AS (
  SELECT * FROM ubs_metric_rows
  UNION ALL
  SELECT * FROM city_metric_rows
  UNION ALL
  SELECT * FROM global_metric_rows
  UNION ALL
  SELECT * FROM unavailable_metric_rows
)

SELECT
  p.period_start_date,
  p.period_end_date,
  r.scope_level,
  r.health_unit_key,
  r.ubs_name,
  r.ubs_city,
  r.journey_type,
  r.metric_name,
  r.metric_value,
  r.metric_denominator,
  r.metric_rate_percent,
  r.metric_unit,
  r.metric_status,
  'curated_v1' AS source_layer,
  'fase3.2' AS source_phase,
  'D1 mantido; N7 com proxy quando aplicável; métricas IGI/notificações/chatbot/help indisponíveis.' AS inherited_limits_note,
  p.snapshot_timestamp
FROM all_metric_rows r
CROSS JOIN params p
;

-- =============================================================================
-- INTERPRETAÇÃO OPERACIONAL DO OUTPUT
-- - O consumo visual pode filtrar por scope_level e metric_name.
-- - metric_status = INDISPONIVEL preserva transparência de lacunas de dados.
-- - Não há PII nesta estrutura de exportação.
-- =============================================================================
