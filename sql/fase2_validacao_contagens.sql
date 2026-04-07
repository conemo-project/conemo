-- =============================================================================
-- fase2_validacao_contagens.sql
-- Queries de validação e evidência de consistência — Fase 2
-- Propósito: verificar aderência ao contrato lógico da Fase 1 após
--   implantação das views curadas mínimas v1 no BigQuery.
-- Dataset curado: conemo-412202.firestore_curated
-- Dataset bruto: conemo-412202.firestore_export
-- Data: 2026-04-07
-- Fase: 2 — Implementação mínima da camada curada
-- Branch: fase-2-implementacao-camada-curada-minima
-- =============================================================================

-- ----------------------------------------------------------------------------
-- INSTRUÇÕES DE USO
-- ----------------------------------------------------------------------------
-- Execute cada query individualmente no BigQuery Console ou via SDK.
-- Os resultados esperados são comparados contra a fonte bruta (8.940 linhas
-- no export CSV consolidado — referência de 04/03/2026).
-- Resultados devem ser registrados manualmente na nota técnica da Fase 2
-- antes da aprovação.
-- ----------------------------------------------------------------------------

-- ============================================================================
-- BLOCO 1: Validação de cur_participant_current_v1
-- ============================================================================

-- V1.1 — Contagem total de participantes analíticos (não-teste)
-- Esperado: menor que 8.940 (total bruto) por exclusão de teste e dedup.
SELECT
  COUNT(*)                                                     AS total_participants,
  COUNT(DISTINCT participant_master_id)                        AS distinct_participants
FROM `conemo-412202.firestore_curated.cur_participant_current_v1`
;

-- V1.2 — Distribuição por id_reconciliation_status
-- Esperado v1: todos 'RESOLVED_DOCUMENT' (D1 — respondent_id ausente)
SELECT
  id_reconciliation_status,
  COUNT(*)                                                     AS n,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)          AS pct
FROM `conemo-412202.firestore_curated.cur_participant_current_v1`
GROUP BY 1
ORDER BY 2 DESC
;

-- V1.3 — Distribuição por record_quality_flag
-- Atenção: alto número de WARN indica campos críticos ausentes.
SELECT
  record_quality_flag,
  COUNT(*)                                                     AS n,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)          AS pct
FROM `conemo-412202.firestore_curated.cur_participant_current_v1`
GROUP BY 1
ORDER BY 2 DESC
;

-- V1.4 — Distribuição por gênero (domínio canônico)
-- Verificar se todos os valores pertencem ao domínio: FEMININO, MASCULINO, OUTRO, NAO_INFORMADO
SELECT
  gender,
  COUNT(*)                                                     AS n,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)          AS pct
FROM `conemo-412202.firestore_curated.cur_participant_current_v1`
GROUP BY 1
ORDER BY 2 DESC
;

-- V1.5 — Distribuição por risco (domínio canônico)
SELECT
  risk,
  COUNT(*)                                                     AS n,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)          AS pct
FROM `conemo-412202.firestore_curated.cur_participant_current_v1`
GROUP BY 1
ORDER BY 2 DESC
;

-- V1.6 — Contagem de health_unit_keys distintas (diagnóstico de UBS)
-- Verificar se há 'UNK_UHS' e em que proporção.
SELECT
  health_unit_key,
  COUNT(*)                                                     AS n_participants
FROM `conemo-412202.firestore_curated.cur_participant_current_v1`
GROUP BY 1
ORDER BY 2 DESC
;

-- ============================================================================
-- BLOCO 2: Validação de cur_health_unit_v1
-- ============================================================================

-- V2.1 — Contagem de unidades de saúde padronizadas
SELECT
  COUNT(*)                                                     AS n_health_units
FROM `conemo-412202.firestore_curated.cur_health_unit_v1`
;

-- V2.2 — Lista completa de UBS e cidades (para auditoria visual)
SELECT
  health_unit_key,
  ubs_name,
  ubs_city,
  health_unit_status
FROM `conemo-412202.firestore_curated.cur_health_unit_v1`
ORDER BY ubs_city, ubs_name
;

-- ============================================================================
-- BLOCO 3: Validação de cur_journey_current_v1
-- ============================================================================

-- V3.1 — Contagem total de registros e jornadas distintas
SELECT
  COUNT(*)                                                     AS total_journey_records,
  COUNT(DISTINCT participant_master_id)                        AS participants_with_journey,
  COUNT(DISTINCT journey_id)                                   AS distinct_journey_types
FROM `conemo-412202.firestore_curated.cur_journey_current_v1`
;

-- V3.2 — Distribuição por tipo de jornada
SELECT
  journey_type,
  COUNT(*)                                                     AS n,
  COUNT(DISTINCT participant_master_id)                        AS n_participants
FROM `conemo-412202.firestore_curated.cur_journey_current_v1`
GROUP BY 1
ORDER BY 2 DESC
;

-- V3.3 — Distribuição por status de jornada
SELECT
  journey_status,
  COUNT(*)                                                     AS n
FROM `conemo-412202.firestore_curated.cur_journey_current_v1`
GROUP BY 1
ORDER BY 2 DESC
;

-- V3.4 — Participantes com mais de uma jornada ativa
-- Esperado: subconjunto de participantes com critério GAD+PHQ simultâneos.
SELECT
  participant_master_id,
  COUNT(DISTINCT journey_id)                                   AS n_journeys
FROM `conemo-412202.firestore_curated.cur_journey_current_v1`
GROUP BY 1
HAVING COUNT(DISTINCT journey_id) > 1
ORDER BY 2 DESC
LIMIT 20
;

-- ============================================================================
-- BLOCO 4: Validação de cur_session_current_v1
-- ============================================================================

-- V4.1 — Contagem total de sessões e distribuição por journey_id
SELECT
  journey_id,
  COUNT(*)                                                     AS n_sessions,
  COUNT(DISTINCT participant_master_id)                        AS n_participants,
  COUNT(DISTINCT session_number)                               AS distinct_session_numbers
FROM `conemo-412202.firestore_curated.cur_session_current_v1`
GROUP BY 1
ORDER BY 2 DESC
;

-- V4.2 — Distribuição por session_status
SELECT
  session_status,
  COUNT(*)                                                     AS n,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)          AS pct
FROM `conemo-412202.firestore_curated.cur_session_current_v1`
GROUP BY 1
ORDER BY 2 DESC
;

-- V4.3 — Progresso máximo de sessão por participante × jornada
-- Verificar distribuição de progresso (última sessão atingida)
SELECT
  journey_id,
  MAX(session_number)                                          AS max_session_number,
  AVG(session_number)                                          AS avg_session_number,
  COUNT(DISTINCT participant_master_id)                        AS n_participants
FROM `conemo-412202.firestore_curated.cur_session_current_v1`
WHERE session_status = 'COMPLETED'
GROUP BY 1
ORDER BY 1
;

-- ============================================================================
-- BLOCO 5: Validação de cur_score_current_v1
-- ============================================================================

-- V5.1 — Contagem e distribuição por score_type
SELECT
  score_type,
  score_source,
  COUNT(*)                                                     AS n,
  ROUND(AVG(score_value), 2)                                   AS avg_score,
  MIN(score_value)                                             AS min_score,
  MAX(score_value)                                             AS max_score
FROM `conemo-412202.firestore_curated.cur_score_current_v1`
GROUP BY 1, 2
ORDER BY score_source, score_type
;

-- V5.2 — Distribuição por score_quality_flag
SELECT
  score_type,
  score_quality_flag,
  COUNT(*)                                                     AS n
FROM `conemo-412202.firestore_curated.cur_score_current_v1`
GROUP BY 1, 2
ORDER BY 1, 2
;

-- ============================================================================
-- BLOCO 6: Verificação de integridade referencial entre entidades
-- ============================================================================

-- V6.1 — Participantes com jornada vs. sem jornada
-- Verificar cobertura de vínculo entre participante e jornada.
SELECT
  'com_jornada'                                                AS status,
  COUNT(DISTINCT p.participant_master_id)                      AS n
FROM `conemo-412202.firestore_curated.cur_participant_current_v1` p
INNER JOIN `conemo-412202.firestore_curated.cur_journey_current_v1` j
  ON p.participant_master_id = j.participant_master_id

UNION ALL

SELECT
  'sem_jornada'                                                AS status,
  COUNT(DISTINCT p.participant_master_id)                      AS n
FROM `conemo-412202.firestore_curated.cur_participant_current_v1` p
WHERE NOT EXISTS (
  SELECT 1
  FROM `conemo-412202.firestore_curated.cur_journey_current_v1` j
  WHERE j.participant_master_id = p.participant_master_id
)
;

-- V6.2 — Sessões sem jornada correspondente
-- Esperado: zero ou próximo de zero (integridade referencial).
SELECT
  COUNT(*)                                                     AS sessions_without_journey
FROM `conemo-412202.firestore_curated.cur_session_current_v1` s
WHERE NOT EXISTS (
  SELECT 1
  FROM `conemo-412202.firestore_curated.cur_journey_current_v1` j
  WHERE j.participant_master_id = s.participant_master_id
    AND j.journey_id = s.journey_id
)
;

-- V6.3 — Participantes com escore vs. sem escore
SELECT
  'com_escore'                                                 AS status,
  COUNT(DISTINCT p.participant_master_id)                      AS n
FROM `conemo-412202.firestore_curated.cur_participant_current_v1` p
INNER JOIN `conemo-412202.firestore_curated.cur_score_current_v1` sc
  ON p.participant_master_id = sc.participant_master_id

UNION ALL

SELECT
  'sem_escore'                                                 AS status,
  COUNT(DISTINCT p.participant_master_id)                      AS n
FROM `conemo-412202.firestore_curated.cur_participant_current_v1` p
WHERE NOT EXISTS (
  SELECT 1
  FROM `conemo-412202.firestore_curated.cur_score_current_v1` sc
  WHERE sc.participant_master_id = p.participant_master_id
)
;

-- ============================================================================
-- BLOCO 7: Verificação de fonte bruta vs. camada curada
-- ============================================================================

-- V7.1 — Comparação de contagem bruta vs. curada de usuários
-- Evidência da exclusão de registros de teste e deduplicação.
SELECT
  'bruto_total'                                                AS fonte,
  COUNT(*)                                                     AS n
FROM `conemo-412202.firestore_export.users_raw_latest`

UNION ALL

SELECT
  'curado_participante_v1'                                     AS fonte,
  COUNT(*)                                                     AS n
FROM `conemo-412202.firestore_curated.cur_participant_current_v1`
;

-- V7.2 — Cidades presentes na fonte bruta mas ausentes na camada curada
-- Diagnóstico de registros de teste excluídos.
SELECT DISTINCT
  TRIM(JSON_VALUE(DATA, '$.organization.city'))                AS city_in_raw,
  'ausente_no_curado'                                          AS status
FROM `conemo-412202.firestore_export.users_raw_latest`
WHERE UPPER(TRIM(JSON_VALUE(DATA, '$.organization.city')))
      IN ('FAKE CITY', 'TEST', 'TESTE', 'TESTCITY', 'TESTE CITY')
ORDER BY 1
;
