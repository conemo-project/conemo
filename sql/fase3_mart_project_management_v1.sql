-- =============================================================================
-- Fase 3.2 — mart_project_management_v1
-- Projeto: CONEMO | Camada: marts mínimos do dashboard
-- Destino: conemo-412202.firestore_curated.mart_project_management_v1
-- =============================================================================
-- OBJETIVO (programação letrada)
-- Esta mart entrega visão executiva por período para gestão do projeto, com
-- recortes GLOBAL e por CIDADE, a partir exclusivamente da camada curada v1.
--
-- GRANULARIDADE
-- - 1 linha por período x escopo de gestão
-- - escopo de gestão: GLOBAL ou CITY (ubs_city)
--
-- FONTES AUTORIZADAS (somente Fase 2 curada)
-- - cur_participant_current_v1
-- - cur_health_unit_v1
-- - cur_session_current_v1
-- - cur_journey_current_v1
-- - cur_score_current_v1
--
-- LIMITAÇÕES HERDADAS
-- - D1 preservado (participant_master_id por document_id)
-- - N7 preservado (tempos com proxy quando necessário)
-- - métricas de notificações/chatbot/help continuam indisponíveis nesta v1
-- =============================================================================
-- AVISO CRÍTICO — PRESSUPOSIÇÃO ZERO DE HOMOLOGAÇÃO EM PRODUÇÃO
-- Os resultados devem ser interpretados no contexto de validação contínua dos
-- objetos curados de origem. Não inferir homologação automática de produção.
-- =============================================================================

CREATE OR REPLACE VIEW `conemo-412202.firestore_curated.mart_project_management_v1` AS
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
    h.ubs_city,
    p.created_at,
    p.record_quality_flag
  FROM `conemo-412202.firestore_curated.cur_participant_current_v1` p
  LEFT JOIN `conemo-412202.firestore_curated.cur_health_unit_v1` h
    ON p.health_unit_key = h.health_unit_key
),

session_base AS (
  SELECT
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
    pb.ubs_city,
    j.participant_master_id,
    j.journey_status,
    j.journey_updated_at
  FROM `conemo-412202.firestore_curated.cur_journey_current_v1` j
  INNER JOIN participant_base pb
    ON pb.participant_master_id = j.participant_master_id
),

score_base AS (
  SELECT
    pb.ubs_city,
    sc.participant_master_id,
    sc.score_type,
    sc.score_source,
    sc.score_value
  FROM `conemo-412202.firestore_curated.cur_score_current_v1` sc
  INNER JOIN participant_base pb
    ON pb.participant_master_id = sc.participant_master_id
),

participant_first_journey AS (
  SELECT
    pb.participant_master_id,
    pb.ubs_city,
    pb.created_at,
    MIN(j.journey_updated_at) AS first_journey_updated_at
  FROM participant_base pb
  LEFT JOIN journey_base j
    ON j.participant_master_id = pb.participant_master_id
  GROUP BY pb.participant_master_id, pb.ubs_city, pb.created_at
),

city_metrics AS (
  SELECT
    pb.ubs_city AS management_scope_key,
    'CITY' AS management_scope_type,

    COUNT(DISTINCT pb.participant_master_id) AS participant_count,
    COUNT(DISTINCT pb.participant_master_id) AS web_initiated_count,

    COUNT(DISTINCT IF(sb.session_number >= 1, pb.participant_master_id, NULL)) AS baseline_completed_count,
    COUNT(DISTINCT IF(sc.score_type IN ('PHQ', 'GAD') AND sc.score_source = 'FORM_INITIAL', pb.participant_master_id, NULL)) AS eligible_count_proxy,
    COUNT(DISTINCT IF(sb.session_number >= 1, pb.participant_master_id, NULL)) AS app_download_count_proxy,

    COUNT(DISTINCT IF(jb.journey_status = 'ACTIVE', pb.participant_master_id, NULL)) AS active_in_journey_count,
    COUNT(DISTINCT IF(jb.journey_status = 'INACTIVE', pb.participant_master_id, NULL)) AS abandoned_participants_count,
    COUNT(DISTINCT IF(sb.session_status = 'OVERDUE', sb.session_document_id, NULL)) AS overdue_sessions_count,

    COUNT(DISTINCT IF(pb.record_quality_flag = 'OK', pb.participant_master_id, NULL)) AS data_quality_ok_count,
    SAFE_DIVIDE(
      COUNT(DISTINCT IF(pb.record_quality_flag = 'OK', pb.participant_master_id, NULL)),
      NULLIF(COUNT(DISTINCT pb.participant_master_id), 0)
    ) * 100 AS data_quality_ok_percent,

    COUNT(DISTINCT IF(sc.score_source = 'FORM_INITIAL', pb.participant_master_id, NULL)) AS participants_with_score_count,
    SAFE_DIVIDE(
      COUNT(DISTINCT IF(sc.score_source = 'FORM_INITIAL', pb.participant_master_id, NULL)),
      NULLIF(COUNT(DISTINCT pb.participant_master_id), 0)
    ) * 100 AS participants_with_score_percent,

    AVG(IF(
      pfj.first_journey_updated_at IS NOT NULL,
      DATE_DIFF(DATE(pfj.first_journey_updated_at), DATE(pfj.created_at), DAY),
      NULL
    )) AS avg_days_web_to_app_proxy

  FROM participant_base pb
  LEFT JOIN session_base sb ON sb.participant_master_id = pb.participant_master_id
  LEFT JOIN journey_base jb ON jb.participant_master_id = pb.participant_master_id
  LEFT JOIN score_base sc ON sc.participant_master_id = pb.participant_master_id
  LEFT JOIN participant_first_journey pfj ON pfj.participant_master_id = pb.participant_master_id
  GROUP BY pb.ubs_city
),

global_metrics AS (
  SELECT
    'GLOBAL' AS management_scope_key,
    'GLOBAL' AS management_scope_type,

    COUNT(DISTINCT pb.participant_master_id) AS participant_count,
    COUNT(DISTINCT pb.participant_master_id) AS web_initiated_count,

    COUNT(DISTINCT IF(sb.session_number >= 1, pb.participant_master_id, NULL)) AS baseline_completed_count,
    COUNT(DISTINCT IF(sc.score_type IN ('PHQ', 'GAD') AND sc.score_source = 'FORM_INITIAL', pb.participant_master_id, NULL)) AS eligible_count_proxy,
    COUNT(DISTINCT IF(sb.session_number >= 1, pb.participant_master_id, NULL)) AS app_download_count_proxy,

    COUNT(DISTINCT IF(jb.journey_status = 'ACTIVE', pb.participant_master_id, NULL)) AS active_in_journey_count,
    COUNT(DISTINCT IF(jb.journey_status = 'INACTIVE', pb.participant_master_id, NULL)) AS abandoned_participants_count,
    COUNT(DISTINCT IF(sb.session_status = 'OVERDUE', sb.session_document_id, NULL)) AS overdue_sessions_count,

    COUNT(DISTINCT IF(pb.record_quality_flag = 'OK', pb.participant_master_id, NULL)) AS data_quality_ok_count,
    SAFE_DIVIDE(
      COUNT(DISTINCT IF(pb.record_quality_flag = 'OK', pb.participant_master_id, NULL)),
      NULLIF(COUNT(DISTINCT pb.participant_master_id), 0)
    ) * 100 AS data_quality_ok_percent,

    COUNT(DISTINCT IF(sc.score_source = 'FORM_INITIAL', pb.participant_master_id, NULL)) AS participants_with_score_count,
    SAFE_DIVIDE(
      COUNT(DISTINCT IF(sc.score_source = 'FORM_INITIAL', pb.participant_master_id, NULL)),
      NULLIF(COUNT(DISTINCT pb.participant_master_id), 0)
    ) * 100 AS participants_with_score_percent,

    AVG(IF(
      pfj.first_journey_updated_at IS NOT NULL,
      DATE_DIFF(DATE(pfj.first_journey_updated_at), DATE(pfj.created_at), DAY),
      NULL
    )) AS avg_days_web_to_app_proxy

  FROM participant_base pb
  LEFT JOIN session_base sb ON sb.participant_master_id = pb.participant_master_id
  LEFT JOIN journey_base jb ON jb.participant_master_id = pb.participant_master_id
  LEFT JOIN score_base sc ON sc.participant_master_id = pb.participant_master_id
  LEFT JOIN participant_first_journey pfj ON pfj.participant_master_id = pb.participant_master_id
),

scope_union AS (
  SELECT * FROM city_metrics
  UNION ALL
  SELECT * FROM global_metrics
),

active_ubs_by_city AS (
  SELECT
    h.ubs_city,
    COUNT(DISTINCT h.health_unit_key) AS total_ubs_count,
    COUNT(DISTINCT IF(j.journey_status = 'ACTIVE', h.health_unit_key, NULL)) AS active_ubs_count
  FROM `conemo-412202.firestore_curated.cur_health_unit_v1` h
  LEFT JOIN participant_base pb ON pb.health_unit_key = h.health_unit_key
  LEFT JOIN journey_base j ON j.participant_master_id = pb.participant_master_id
  GROUP BY h.ubs_city
),

active_ubs_global AS (
  SELECT
    COUNT(DISTINCT h.health_unit_key) AS total_ubs_count,
    COUNT(DISTINCT IF(j.journey_status = 'ACTIVE', h.health_unit_key, NULL)) AS active_ubs_count
  FROM `conemo-412202.firestore_curated.cur_health_unit_v1` h
  LEFT JOIN participant_base pb ON pb.health_unit_key = h.health_unit_key
  LEFT JOIN journey_base j ON j.participant_master_id = pb.participant_master_id
)

SELECT
  p.period_start_date,
  p.period_end_date,
  s.management_scope_type,
  s.management_scope_key,

  s.participant_count,
  s.web_initiated_count,
  s.baseline_completed_count,
  s.eligible_count_proxy,
  s.app_download_count_proxy,
  s.active_in_journey_count,
  s.overdue_sessions_count,
  s.abandoned_participants_count,

  CASE
    WHEN s.management_scope_type = 'CITY' THEN COALESCE(ac.active_ubs_count, 0)
    ELSE COALESCE(ag.active_ubs_count, 0)
  END AS active_ubs_count,

  CASE
    WHEN s.management_scope_type = 'CITY' THEN COALESCE(ac.total_ubs_count, 0)
    ELSE COALESCE(ag.total_ubs_count, 0)
  END AS total_ubs_count,

  SAFE_DIVIDE(
    CASE WHEN s.management_scope_type = 'CITY' THEN COALESCE(ac.active_ubs_count, 0)
         ELSE COALESCE(ag.active_ubs_count, 0)
    END,
    NULLIF(
      CASE WHEN s.management_scope_type = 'CITY' THEN COALESCE(ac.total_ubs_count, 0)
           ELSE COALESCE(ag.total_ubs_count, 0)
      END,
      0
    )
  ) * 100 AS active_ubs_percent,

  s.data_quality_ok_count,
  s.data_quality_ok_percent,
  s.participants_with_score_count,
  s.participants_with_score_percent,
  s.avg_days_web_to_app_proxy,

  TRUE AS time_metric_is_proxy,
  FALSE AS notifications_observavel,
  FALSE AS chatbot_observavel,
  FALSE AS help_request_observavel,
  FALSE AS igi_observavel,

  'N7 aplicado com proxy temporal; métricas de notificação/chatbot/help e IGI indisponíveis nesta v1.' AS inherited_limits_note,
  p.snapshot_timestamp
FROM scope_union s
CROSS JOIN params p
LEFT JOIN active_ubs_by_city ac
  ON ac.ubs_city = s.management_scope_key
LEFT JOIN active_ubs_global ag
  ON s.management_scope_type = 'GLOBAL'
;

-- =============================================================================
-- INTERPRETAÇÃO OPERACIONAL DO OUTPUT
-- - Escopo CITY apoia gestão territorial por cidade.
-- - Escopo GLOBAL apoia acompanhamento executivo do projeto.
-- - Campos *_proxy carregam aproximações aceitas formalmente na Fase 3.
-- =============================================================================
