-- =============================================================================
-- cur_session_current_v1.sql
-- Entidade: Estado atual de sessões por participante × jornada
-- Fonte: conemo-412202.firestore_export.sessions_raw_latest
-- Vínculo: path_params.{$.userId, $.journeyId}
-- Destino: conemo-412202.firestore_curated.cur_session_current_v1
-- Camada: B — curada compartilhada (BigQuery-first)
-- Versão: v1
-- Data: 2026-04-07
-- Fase: 2 — Implementação mínima da camada curada
-- Branch: fase-2-implementacao-camada-curada-minima
-- =============================================================================

-- ----------------------------------------------------------------------------
-- OBJETIVO DESTA VIEW
-- ----------------------------------------------------------------------------
-- Registrar o estado atual de cada sessão terapêutica, vinculada ao
-- participante e à jornada correspondente.
-- Granularidade: 1 linha por participant_master_id × journey_id × session_number.
--
-- Esta entidade é a base para indicadores de progresso, adesão, completude
-- e atraso de sessão no dashboard e no SGBD.
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- ESTRUTURA FÍSICA DE ORIGEM
-- ----------------------------------------------------------------------------
-- sessions_raw_latest:
--   document_id  → ID da sessão no Firestore
--   path_params  → JSON: {"userId": "<uid>", "journeyId": "<GAD|DEPRESSION>"}
--   DATA         → JSON com: sessionNumber, isCompleted, name, daily, steps
--
-- VÍNCULO DE JOIN:
--   path_params.$.userId    → participant_master_id (document_id de usuários)
--   path_params.$.journeyId → journey_id (document_id de jornadas)
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- NOTAS DE IMPLEMENTAÇÃO
-- ----------------------------------------------------------------------------
-- sessionNumber (N_CAST):
--   Valor físico em STRING. Requer SAFE_CAST para INT64. Registros sem
--   número de sessão recebem NULL_TECH na nota técnica.
--
-- isCompleted (BOOL):
--   Valor físico em STRING ("true"/"false"). Booleanizado via CASE.
--   Default conservativo: FALSE quando ausente.
--
-- session_status (DERIVADO):
--   Inferido de is_completed + session_number.
--   Lógica: COMPLETED → concluída; UNKNOWN → session_number nulo;
--   NOT_STARTED → session_number = 1 e não concluída;
--   IN_PROGRESS → demais casos.
--
-- N7 (event_timestamp):
--   Não há timestamp de início de sessão confirmado. completedDate existe
--   em DATA mas como STRING sem formato fixo verificado neste export.
--   event_timestamp = NULL nesta v1; marcado como NULL_TECH.
-- ----------------------------------------------------------------------------

CREATE OR REPLACE VIEW `conemo-412202.firestore_curated.cur_session_current_v1` AS

-- ============================================================================
-- PASSO 1: Extração dos campos brutos de sessions_raw_latest
-- ============================================================================
-- path_params é um JSON string que contém o userId e o journeyId.
-- Ambos são extraídos com JSON_VALUE para uso como chaves de join.
WITH sessions_extracted AS (
  SELECT
    -- Identificador da sessão no Firestore
    document_id                                                AS session_document_id,

    -- Vínculos de join via path_params
    JSON_VALUE(path_params, '$.userId')                        AS user_id_raw,
    JSON_VALUE(path_params, '$.journeyId')                     AS journey_id_raw,

    -- Número da sessão: STRING no JSON → SAFE_CAST para INT64
    SAFE_CAST(
      TRIM(JSON_VALUE(DATA, '$.sessionNumber')) AS INT64
    )                                                          AS session_number,

    -- Status de conclusão: STRING "true"/"false" → booleanizado no passo 2
    LOWER(TRIM(JSON_VALUE(DATA, '$.isCompleted')))             AS is_completed_raw,

    -- Nome da sessão (metadado operacional para referência humana)
    JSON_VALUE(DATA, '$.name')                                 AS session_name

  FROM `conemo-412202.firestore_export.sessions_raw_latest`

  -- Filtro de integridade: exige vínculo com participante
  WHERE document_id IS NOT NULL
    AND path_params IS NOT NULL
    AND JSON_VALUE(path_params, '$.userId') IS NOT NULL
    AND TRIM(JSON_VALUE(path_params, '$.userId')) != ''
),

-- ============================================================================
-- PASSO 2: Normalização e derivação dos campos curados
-- ============================================================================
sessions_normalized AS (
  SELECT
    -- -------------------------------------------------------------------
    -- BLOCO DE IDENTIFICAÇÃO
    -- -------------------------------------------------------------------
    user_id_raw                                                AS participant_master_id,
    user_id_raw                                                AS source_user_id,
    'RESOLVED_DOCUMENT'                                        AS id_reconciliation_status,

    -- journey_id: de path_params.$.journeyId
    -- Quando ausente, marcado como 'UNK' para preservar linha
    COALESCE(NULLIF(TRIM(journey_id_raw), ''), 'UNK')          AS journey_id,

    -- Identificador do documento de sessão (para auditoria)
    session_document_id,

    -- -------------------------------------------------------------------
    -- BLOCO DE PROGRESSÃO DE SESSÃO
    -- -------------------------------------------------------------------
    -- session_number: INT64 (NULL quando SAFE_CAST falha — dados corrompidos)
    session_number,
    session_name,

    -- Booleanização de is_completed:
    --   "true"  → TRUE
    --   "false" → FALSE
    --   ausente → FALSE (conservativo: não assumir conclusão sem confirmação)
    CASE
      WHEN is_completed_raw = 'true'   THEN TRUE
      WHEN is_completed_raw = 'false'  THEN FALSE
      ELSE FALSE
    END                                                        AS is_completed,

    -- -------------------------------------------------------------------
    -- BLOCO DE STATUS OPERACIONAL DA SESSÃO
    -- -------------------------------------------------------------------
    -- session_status: derivado de is_completed e session_number.
    -- Domínio canônico (Fase 1, seção 11.6):
    --   COMPLETED   → sessão concluída
    --   IN_PROGRESS → sessão iniciada (> sessão 1 e não concluída)
    --   NOT_STARTED → sessão 1 não iniciada
    --   UNKNOWN     → session_number nulo (dado corrompido ou ausente)
    CASE
      WHEN CASE WHEN is_completed_raw = 'true' THEN TRUE ELSE FALSE END = TRUE
        THEN 'COMPLETED'
      WHEN session_number IS NULL
        THEN 'UNKNOWN'
      WHEN session_number = 1
        AND COALESCE(is_completed_raw = 'true', FALSE) = FALSE
        THEN 'NOT_STARTED'
      ELSE 'IN_PROGRESS'
    END                                                        AS session_status,

    -- -------------------------------------------------------------------
    -- BLOCO DE TEMPORALIDADE
    -- -------------------------------------------------------------------
    -- event_timestamp: ausente nesta v1 (N7 — ver verificação técnica 2.1)
    -- completedDate existe como STRING mas formato não confirmado neste export.
    -- Implementação futura quando timestamp de sessão for confirmado.
    CAST(NULL AS TIMESTAMP)                                    AS event_timestamp

  FROM sessions_extracted
  WHERE user_id_raw IS NOT NULL
    AND TRIM(user_id_raw) != ''
)

-- ============================================================================
-- RESULTADO FINAL
-- ============================================================================
-- Uma linha por participant_master_id × journey_id × session_number.
-- Base para indicadores de adesão, progresso e atraso.
SELECT
  participant_master_id,
  source_user_id,
  id_reconciliation_status,
  journey_id,
  session_document_id,
  session_number,
  session_name,
  is_completed,
  session_status,
  event_timestamp  -- NULL nesta v1 (N7 — awaiting format confirmation)

FROM sessions_normalized
;
