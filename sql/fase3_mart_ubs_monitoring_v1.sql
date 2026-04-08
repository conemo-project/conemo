-- =============================================================================
-- Fase 3.2 — mart_ubs_monitoring_v1
-- Projeto: CONEMO | Camada: marts mínimos do dashboard
-- Destino: conemo-412202.firestore_curated.mart_ubs_monitoring_v1
-- =============================================================================
-- OBJETIVO (programação letrada)
-- Esta mart consolida indicadores operacionais e clínicos agregados por UBS,
-- em granularidade de 1 linha por UBS x período (snapshot semanal).
--
-- FONTES AUTORIZADAS (somente camada curada da Fase 2)
-- - cur_participant_current_v1
-- - cur_health_unit_v1
-- - cur_session_current_v1
-- - cur_journey_current_v1
-- - cur_score_current_v1
--
-- REGRAS DE NEGÓCIO APLICADAS
-- - participante mestre baseado em document_id (D1 herdado, respondent_id ausente)
-- - sessões e jornadas agregadas por UBS, sem parse de JSON bruto
-- - escores PHQ/GAD apenas de score_source = FORM_INITIAL
--
-- LIMITAÇÕES HERDADAS (explícitas)
-- - D1: respondent_id indisponível (não resolvido silenciosamente)
-- - D2: resolvido internamente (não reaberto)
-- - N7: event_timestamp não implementado em cur_session_current_v1
-- - N-IGI: IGI indisponível nas fontes verificadas
-- - notificações/chatbot/help: indisponíveis nesta v1
-- =============================================================================
-- AVISO CRÍTICO — PRESSUPOSIÇÃO ZERO DE HOMOLOGAÇÃO EM PRODUÇÃO
-- Esta mart deriva de views curadas da Fase 2 que foram documentadas e abertas,
-- mas cuja interpretação operacional ainda depende de validação contínua no
-- BigQuery real. Use os números como referência operacional auditável desta fase.
-- =============================================================================

CREATE OR REPLACE VIEW `conemo-412202.firestore_curated.mart_ubs_monitoring_v1` AS
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
    p.record_quality_flag,
    p.created_at
  FROM `conemo-412202.firestore_curated.cur_participant_current_v1` p
  LEFT JOIN `conemo-412202.firestore_curated.cur_health_unit_v1` h
    ON p.health_unit_key = h.health_unit_key
),

journey_base AS (
  SELECT
    pb.health_unit_key,
    pb.ubs_name,
    pb.ubs_city,
    j.participant_master_id,
    j.journey_id,
    j.journey_status,
    j.last_session_number,
    j.journey_updated_at
  FROM `conemo-412202.firestore_curated.cur_journey_current_v1` j
  INNER JOIN participant_base pb
    ON pb.participant_master_id = j.participant_master_id
),

session_base AS (
  SELECT
    pb.health_unit_key,
    pb.ubs_name,
    pb.ubs_city,
    s.participant_master_id,
    s.journey_id,
    s.session_document_id,
    s.session_number,
    s.is_completed,
    s.session_status
  FROM `conemo-412202.firestore_curated.cur_session_current_v1` s
  INNER JOIN participant_base pb
    ON pb.participant_master_id = s.participant_master_id
),

score_base AS (
  SELECT
    pb.health_unit_key,
    pb.ubs_name,
    pb.ubs_city,
    sc.participant_master_id,
    sc.score_type,
    sc.score_value,
    sc.score_source,
    sc.score_quality_flag
  FROM `conemo-412202.firestore_curated.cur_score_current_v1` sc
  INNER JOIN participant_base pb
    ON pb.participant_master_id = sc.participant_master_id
),

agg_participants AS (
  SELECT
    health_unit_key,
    ANY_VALUE(ubs_name) AS ubs_name,
    ANY_VALUE(ubs_city) AS ubs_city,
    COUNT(DISTINCT participant_master_id) AS participant_count_ubs,
    COUNT(DISTINCT IF(record_quality_flag = 'OK', participant_master_id, NULL)) AS participant_quality_ok_count
  FROM participant_base
  GROUP BY health_unit_key
),

agg_baseline AS (
  SELECT
    health_unit_key,
    COUNT(DISTINCT IF(session_number >= 1, participant_master_id, NULL)) AS baseline_completed_count_ubs
  FROM session_base
  GROUP BY health_unit_key
),

agg_active AS (
  SELECT
    health_unit_key,
    COUNT(DISTINCT IF(
      journey_status = 'ACTIVE'
      AND (journey_updated_at IS NULL OR DATE(journey_updated_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)),
      participant_master_id,
      NULL
    )) AS active_participants_ubs
  FROM journey_base
  GROUP BY health_unit_key
),

agg_overdue AS (
  SELECT
    health_unit_key,
    COUNT(DISTINCT IF(session_status = 'OVERDUE', session_document_id, NULL)) AS overdue_sessions_count_ubs,
    COUNT(DISTINCT IF(session_status = 'OVERDUE', participant_master_id, NULL)) AS overdue_participants_count_ubs
  FROM session_base
  GROUP BY health_unit_key
),

agg_abandonment AS (
  SELECT
    health_unit_key,
    COUNT(DISTINCT IF(journey_status = 'INACTIVE', participant_master_id, NULL)) AS abandoned_participants_count_ubs
  FROM journey_base
  GROUP BY health_unit_key
),

journey_completion_detail AS (
  SELECT
    j.health_unit_key,
    j.participant_master_id,
    j.journey_id,
    MAX(IF(s.is_completed, s.session_number, 0)) AS max_completed_session_number,
    MAX(j.last_session_number) AS expected_last_session_number
  FROM journey_base j
  LEFT JOIN session_base s
    ON s.participant_master_id = j.participant_master_id
   AND s.journey_id = j.journey_id
  GROUP BY j.health_unit_key, j.participant_master_id, j.journey_id
),

agg_completion AS (
  SELECT
    health_unit_key,
    COUNT(DISTINCT IF(
      expected_last_session_number IS NOT NULL
      AND expected_last_session_number > 0
      AND max_completed_session_number >= expected_last_session_number,
      CONCAT(participant_master_id, '#', journey_id),
      NULL
    )) AS completed_journeys_count_ubs
  FROM journey_completion_detail
  GROUP BY health_unit_key
),

agg_scores AS (
  SELECT
    health_unit_key,
    AVG(IF(score_type = 'PHQ' AND score_source = 'FORM_INITIAL', score_value, NULL)) AS phq9_score_avg_ubs,
    AVG(IF(score_type = 'GAD' AND score_source = 'FORM_INITIAL', score_value, NULL)) AS gad7_score_avg_ubs,

    COUNTIF(score_type = 'PHQ' AND score_source = 'FORM_INITIAL' AND score_value BETWEEN 0 AND 4) AS phq9_minimo_count,
    COUNTIF(score_type = 'PHQ' AND score_source = 'FORM_INITIAL' AND score_value BETWEEN 5 AND 9) AS phq9_leve_count,
    COUNTIF(score_type = 'PHQ' AND score_source = 'FORM_INITIAL' AND score_value BETWEEN 10 AND 14) AS phq9_moderado_count,
    COUNTIF(score_type = 'PHQ' AND score_source = 'FORM_INITIAL' AND score_value BETWEEN 15 AND 19) AS phq9_mod_severo_count,
    COUNTIF(score_type = 'PHQ' AND score_source = 'FORM_INITIAL' AND score_value >= 20) AS phq9_severo_count,

    COUNTIF(score_type = 'GAD' AND score_source = 'FORM_INITIAL' AND score_value BETWEEN 0 AND 4) AS gad7_minimo_count,
    COUNTIF(score_type = 'GAD' AND score_source = 'FORM_INITIAL' AND score_value BETWEEN 5 AND 9) AS gad7_leve_count,
    COUNTIF(score_type = 'GAD' AND score_source = 'FORM_INITIAL' AND score_value BETWEEN 10 AND 14) AS gad7_moderado_count,
    COUNTIF(score_type = 'GAD' AND score_source = 'FORM_INITIAL' AND score_value >= 15) AS gad7_severo_count,

    COUNTIF(score_quality_flag != 'OK') AS score_quality_warning_count
  FROM score_base
  GROUP BY health_unit_key
)

SELECT
  p.period_start_date,
  p.period_end_date,
  a.health_unit_key,
  a.ubs_name,
  a.ubs_city,

  a.participant_count_ubs,
  COALESCE(b.baseline_completed_count_ubs, 0) AS baseline_completed_count_ubs,
  COALESCE(ac.active_participants_ubs, 0) AS active_participants_ubs,
  COALESCE(ov.overdue_sessions_count_ubs, 0) AS overdue_sessions_count_ubs,
  COALESCE(ov.overdue_participants_count_ubs, 0) AS overdue_participants_count_ubs,
  COALESCE(ab.abandoned_participants_count_ubs, 0) AS abandoned_participants_count_ubs,
  COALESCE(cm.completed_journeys_count_ubs, 0) AS completed_journeys_count_ubs,

  sc.phq9_score_avg_ubs,
  sc.gad7_score_avg_ubs,
  COALESCE(sc.phq9_minimo_count, 0) AS phq9_minimo_count,
  COALESCE(sc.phq9_leve_count, 0) AS phq9_leve_count,
  COALESCE(sc.phq9_moderado_count, 0) AS phq9_moderado_count,
  COALESCE(sc.phq9_mod_severo_count, 0) AS phq9_mod_severo_count,
  COALESCE(sc.phq9_severo_count, 0) AS phq9_severo_count,
  COALESCE(sc.gad7_minimo_count, 0) AS gad7_minimo_count,
  COALESCE(sc.gad7_leve_count, 0) AS gad7_leve_count,
  COALESCE(sc.gad7_moderado_count, 0) AS gad7_moderado_count,
  COALESCE(sc.gad7_severo_count, 0) AS gad7_severo_count,

  a.participant_quality_ok_count,
  SAFE_DIVIDE(a.participant_quality_ok_count, NULLIF(a.participant_count_ubs, 0)) * 100 AS participant_quality_ok_percent,
  COALESCE(sc.score_quality_warning_count, 0) AS score_quality_warning_count,

  FALSE AS igi_observavel,
  FALSE AS notifications_observavel,
  FALSE AS chatbot_observavel,
  FALSE AS help_request_observavel,

  'D1 mantido; N7 sem event_timestamp; N-IGI e eventos operacionais externos indisponíveis nesta v1.' AS inherited_limits_note,
  p.snapshot_timestamp
FROM agg_participants a
CROSS JOIN params p
LEFT JOIN agg_baseline b USING (health_unit_key)
LEFT JOIN agg_active ac USING (health_unit_key)
LEFT JOIN agg_overdue ov USING (health_unit_key)
LEFT JOIN agg_abandonment ab USING (health_unit_key)
LEFT JOIN agg_completion cm USING (health_unit_key)
LEFT JOIN agg_scores sc USING (health_unit_key)
;

-- =============================================================================
-- INTERPRETAÇÃO OPERACIONAL DO OUTPUT
-- - Uma linha por UBS no período de snapshot da execução da query.
-- - Métricas de tempo fino dependentes de event_timestamp não são apresentadas.
-- - Métricas indisponíveis foram explicitamente sinalizadas em colunas booleanas.
-- =============================================================================
