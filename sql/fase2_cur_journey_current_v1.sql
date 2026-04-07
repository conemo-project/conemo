-- =============================================================================
-- cur_journey_current_v1.sql
-- Entidade: Estado atual da jornada terapêutica por participante
-- Fonte: conemo-412202.firestore_export.journeys_raw_latest
-- Vínculo com participante: path_params.$.userId → users_raw_latest.document_id
-- Destino: conemo-412202.firestore_curated.cur_journey_current_v1
-- Camada: B — curada compartilhada (BigQuery-first)
-- Versão: v1
-- Data: 2026-04-07
-- Fase: 2 — Implementação mínima da camada curada
-- Branch: fase-2-implementacao-camada-curada-minima
-- =============================================================================

-- ----------------------------------------------------------------------------
-- OBJETIVO DESTA VIEW
-- ----------------------------------------------------------------------------
-- Registrar o estado atual de cada jornada terapêutica por participante.
-- Granularidade: 1 linha por participant_master_id × journey_id.
--
-- Um participante pode ter até 2 jornadas ativas (GAD e DEPRESSION), conforme
-- protocolo CONEMO: alocação por critério GAD-7 e/ou PHQ-9.
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- ESTRUTURA FÍSICA DE ORIGEM
-- ----------------------------------------------------------------------------
-- journeys_raw_latest:
--   document_id    → ID do documento de jornada no Firestore
--                    Valor observado: "GAD" ou "DEPRESSION" (tipo como ID)
--   path_params    → JSON: {"userId": "<uid>"} — vínculo com o usuário
--   DATA           → JSON com: type, enabled, lastAccess, lastSession, score
--
-- VÍNCULO DE JOIN:
--   path_params.$.userId = users_raw_latest.document_id = participant_master_id
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- NOTAS DE IMPLEMENTAÇÃO
-- ----------------------------------------------------------------------------
-- N2 (journey_updated_at):
--   Não existe campo "updatedAt" em journeys_raw_latest.
--   journey_updated_at é derivado de DATA.$.lastAccess._seconds.
--
-- journey_type (normalização):
--   Valores físicos: "GAD", "DEPRESSION". Mapeados ao domínio canônico
--   definido na Fase 1: ANXIETY (GAD) e DEPRESSION.
--
-- journey_status (derivação):
--   Derivado de DATA.$.enabled ("true"/"false"). Sem campo de status direto.
-- ----------------------------------------------------------------------------

CREATE OR REPLACE VIEW `conemo-412202.firestore_curated.cur_journey_current_v1` AS

-- ============================================================================
-- PASSO 1: Extração dos campos brutos de journeys_raw_latest
-- ============================================================================
-- O campo path_params contém o userId como JSON. Extraímos com JSON_VALUE.
-- O campo DATA contém os atributos da jornada em formato JSON string.
WITH journeys_extracted AS (
  SELECT
    -- journey_id: ID do documento da jornada (ex: "GAD", "DEPRESSION")
    document_id                                                AS journey_id,

    -- Vínculo com o participante via path_params.$.userId
    JSON_VALUE(path_params, '$.userId')                        AS user_id_raw,

    -- Tipo da jornada: valores físicos "GAD", "DEPRESSION", ou outro
    TRIM(UPPER(JSON_VALUE(DATA, '$.type')))                    AS journey_type_raw,

    -- Estado de ativação: STRING "true"/"false" (não BOOLEAN nativo)
    TRIM(LOWER(JSON_VALUE(DATA, '$.enabled')))                 AS enabled_raw,

    -- Última sessão completada ou acessada (usado para métricas de progresso)
    SAFE_CAST(JSON_VALUE(DATA, '$.lastSession') AS INT64)      AS last_session_number,

    -- Timestamp da última atividade (N2: substitui journey_updated_at)
    SAFE_CAST(
      JSON_VALUE(DATA, '$.lastAccess._seconds') AS INT64
    )                                                          AS last_access_seconds,

    -- Score agregado da jornada (distinto dos escores de formulário — ver N5)
    SAFE_CAST(JSON_VALUE(DATA, '$.score') AS FLOAT64)          AS journey_score

  FROM `conemo-412202.firestore_export.journeys_raw_latest`

  -- Filtro de integridade: exige vínculo com participante
  WHERE document_id IS NOT NULL
    AND path_params IS NOT NULL
    AND JSON_VALUE(path_params, '$.userId') IS NOT NULL
    AND TRIM(JSON_VALUE(path_params, '$.userId')) != ''
),

-- ============================================================================
-- PASSO 2: Normalização de domínios e derivação de campos curados
-- ============================================================================
journeys_normalized AS (
  SELECT
    -- -------------------------------------------------------------------
    -- BLOCO DE IDENTIFICAÇÃO
    -- -------------------------------------------------------------------
    -- participant_master_id: path_params.userId equivale a document_id
    -- na coleção de usuários. Sem respondent_id disponível (D1 herdado).
    user_id_raw                                                AS participant_master_id,
    user_id_raw                                                AS source_user_id,
    'RESOLVED_DOCUMENT'                                        AS id_reconciliation_status,

    -- journey_id: ID do documento (ex: "GAD", "DEPRESSION")
    journey_id,

    -- -------------------------------------------------------------------
    -- BLOCO DE TIPO DE JORNADA
    -- -------------------------------------------------------------------
    -- Mapeamento para domínio canônico (Fase 1, seção 11.5):
    --   GAD  → ANXIETY
    --   PHQ / DEPRESSION → DEPRESSION
    --   Ambos → registros separados (modelo CONEMO permite 2 jornadas)
    CASE
      WHEN journey_type_raw IN ('GAD', 'ANXIETY', 'ANSIEDADE')        THEN 'ANXIETY'
      WHEN journey_type_raw IN ('PHQ', 'DEPRESSION', 'DEPRESSAO',
                                'DEPRESSÃO')                          THEN 'DEPRESSION'
      WHEN journey_type_raw IS NULL OR journey_type_raw = ''          THEN 'UNKNOWN'
      ELSE journey_type_raw  -- preservar valor não mapeado com transparência
    END                                                        AS journey_type,

    -- -------------------------------------------------------------------
    -- BLOCO DE STATUS DA JORNADA
    -- -------------------------------------------------------------------
    -- Derivado do campo enabled ("true"/"false").
    -- Domínio canônico: ACTIVE, INACTIVE, UNKNOWN.
    CASE
      WHEN enabled_raw = 'true'    THEN 'ACTIVE'
      WHEN enabled_raw = 'false'   THEN 'INACTIVE'
      ELSE 'UNKNOWN'
    END                                                        AS journey_status,

    -- -------------------------------------------------------------------
    -- BLOCO DE PROGRESSO E TEMPORALIDADE
    -- -------------------------------------------------------------------
    last_session_number,
    journey_score,

    -- journey_updated_at: derivado de lastAccess._seconds (N2)
    -- NULL quando lastAccess ausente; marcado como NULL_TECH na nota técnica
    TIMESTAMP_SECONDS(last_access_seconds)                     AS journey_updated_at

  FROM journeys_extracted
  WHERE user_id_raw IS NOT NULL
    AND TRIM(user_id_raw) != ''
)

-- ============================================================================
-- RESULTADO FINAL
-- ============================================================================
-- Uma linha por participante × jornada. A combinação (participant_master_id,
-- journey_id) é a chave composta desta entidade.
SELECT
  participant_master_id,
  source_user_id,
  id_reconciliation_status,
  journey_id,
  journey_type,
  journey_status,
  last_session_number,
  journey_score,
  journey_updated_at

FROM journeys_normalized
;
