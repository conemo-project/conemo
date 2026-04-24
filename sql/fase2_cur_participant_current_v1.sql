-- =============================================================================
-- cur_participant_current_v1.sql
-- Entidade: Retrato analítico atual do participante (sem PII direta)
-- Fonte principal: conemo-412202.firestore_export.users_raw_latest
-- Destino: conemo-412202.firestore_curated.cur_participant_current_v1
-- Camada: B — curada compartilhada (BigQuery-first)
-- Versão: v1
-- Data: 2026-04-07
-- Fase: 2 — Implementação mínima da camada curada
-- Branch: fase-2-implementacao-camada-curada-minima
-- =============================================================================

-- ----------------------------------------------------------------------------
-- OBJETIVO DESTA VIEW
-- ----------------------------------------------------------------------------
-- Construir o retrato analítico atual de cada participante do CONEMO,
-- eliminando campos PII e normalizando os domínios canônicos definidos na
-- Fase 1. A granularidade é 1 linha por participante (document_id único).
--
-- Esta view é a entidade central da camada compartilhada: todos os demais
-- objetos curados (jornadas, sessões, escores) fazem join com ela via
-- participant_master_id.
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- NOTAS DE IMPLEMENTAÇÃO (resultado da verificação técnica — Etapa 2.1)
-- ----------------------------------------------------------------------------
-- D1 (DIVERGÊNCIA ESTRUTURAL — BLOQUEIO PARCIAL):
--   respondent_id não existe em users_raw_latest (nem como coluna top-level
--   nem dentro do JSON DATA). O tier 1 da hierarquia de reconciliação de IDs
--   não pode ser implementado. source_respondent_id = NULL em todos os
--   registros. id_reconciliation_status = 'RESOLVED_DOCUMENT'. Decisão formal
--   pendente (ver Docs/fase-2-verificacao-tecnica-bigquery.md, seção 6, D1).
--
-- D2 (DIVERGÊNCIA NOMINAL — RESOLVIDA):
--   userId não é coluna top-level. O identificador único do usuário é
--   document_id (= DATA.$.id). source_user_id deriva de JSON_VALUE(DATA,'$.id').
--
-- N4 (NOTA — LOCALIZAÇÃO DE health_unit_key):
--   health_unit_key vem de DATA.$.organization.id, não de path_params
--   (que é vazio para a coleção raiz de usuários).
--
-- N6 (NOTA — NORMALIZAÇÃO DE GÊNERO):
--   Valores físicos: "F", "M". Mapeados para domínio canônico:
--   FEMININO, MASCULINO, OUTRO, NAO_INFORMADO.
--
-- SEGREGAÇÃO PII:
--   Excluídos: name, email, cpf, birthDate, termsOfConsent, phone.
--   Incluídos: atributos analíticos não identificáveis diretamente.
-- ----------------------------------------------------------------------------

CREATE OR REPLACE VIEW `conemo-412202.firestore_curated.cur_participant_current_v1` AS

-- ============================================================================
-- PASSO 1: Extração dos campos brutos de users_raw_latest
-- ============================================================================
-- Extraímos apenas os atributos analíticos necessários. Campos PII
-- (name, email, cpf, birthDate) são deliberadamente omitidos.
-- A coluna DATA contém o JSON principal; usamos JSON_VALUE para acessar
-- cada atributo de interesse.
WITH users_extracted AS (
  SELECT
    -- Identificador primário do Firestore (único e estável)
    document_id                                                AS source_document_id,

    -- source_user_id: DATA.$.id é idêntico a document_id nesta coleção (D2)
    JSON_VALUE(DATA, '$.id')                                   AS source_user_id_raw,

    -- Atributos demográficos analíticos (sem PII direta)
    TRIM(UPPER(JSON_VALUE(DATA, '$.gender')))                  AS gender_raw,
    TRIM(UPPER(JSON_VALUE(DATA, '$.risk')))                    AS risk_raw,

    -- Vínculo com unidade de saúde (N4: de organization.id, não de path_params)
    TRIM(JSON_VALUE(DATA, '$.organization.id'))                AS org_id_raw,
    TRIM(UPPER(JSON_VALUE(DATA, '$.organization.name')))       AS org_name_raw,
    TRIM(JSON_VALUE(DATA, '$.organization.city'))              AS org_city_raw,

    -- Metadados operacionais (grupo e origem do cadastro)
    JSON_VALUE(DATA, '$.group')                                AS participant_group,
    JSON_VALUE(DATA, '$.source')                               AS registration_source,

    -- Timestamp de criação (para auditoria e séries temporais)
    SAFE_CAST(
      JSON_VALUE(DATA, '$.createdAt._seconds') AS INT64
    )                                                          AS created_at_seconds

  FROM `conemo-412202.firestore_export.users_raw_latest`

  -- Filtro de qualidade mínima: document_id deve ser não-nulo e não-vazio
  WHERE document_id IS NOT NULL
    AND TRIM(document_id) != ''
),

-- ============================================================================
-- PASSO 2: Normalização de domínios canônicos e derivação de campos
-- ============================================================================
-- Aqui aplicamos as regras de negócio para mapear valores brutos para
-- os domínios fechados definidos no contrato lógico da Fase 1.
-- Também derivamos campos compostos (health_unit_key, is_test_record).
users_normalized AS (
  SELECT
    -- -------------------------------------------------------------------
    -- BLOCO DE IDENTIFICAÇÃO
    -- -------------------------------------------------------------------
    -- participant_master_id: document_id é o identificador único e estável.
    -- D1: respondent_id ausente na fonte — tier 1 da hierarquia indisponível.
    -- D2: source_user_id = DATA.$.id = document_id (mesma chave).
    source_document_id                                         AS participant_master_id,
    source_document_id,
    source_user_id_raw                                         AS source_user_id,

    -- respondent_id ausente da fonte física (D1 — ver etapa 2.1)
    CAST(NULL AS STRING)                                       AS source_respondent_id,

    -- Status de reconciliação: apenas document_id disponível nesta implementação
    'RESOLVED_DOCUMENT'                                        AS id_reconciliation_status,

    -- -------------------------------------------------------------------
    -- BLOCO DE GÊNERO
    -- -------------------------------------------------------------------
    -- Regra de normalização: valores físicos são "F", "M" ou nulo.
    -- Domínio canônico: FEMININO, MASCULINO, OUTRO, NAO_INFORMADO.
    CASE
      WHEN gender_raw IN ('F', 'FEMININO', 'FEMALE', 'MULHER')        THEN 'FEMININO'
      WHEN gender_raw IN ('M', 'MASCULINO', 'MALE', 'HOMEM')          THEN 'MASCULINO'
      WHEN gender_raw IS NULL OR gender_raw IN ('', 'N/A', 'NAO INFORMADO') THEN 'NAO_INFORMADO'
      ELSE 'OUTRO'
    END                                                        AS gender,

    -- -------------------------------------------------------------------
    -- BLOCO DE RISCO OPERACIONAL
    -- -------------------------------------------------------------------
    -- Normalização do campo de risco. Não altera regra clínica;
    -- apenas padroniza representação operacional para filtros e agrupamentos.
    CASE
      WHEN risk_raw IN ('BAIXO', 'LOW', 'B')                  THEN 'BAIXO'
      WHEN risk_raw IN ('MODERADO', 'MODERATE', 'M', 'MED')   THEN 'MODERADO'
      WHEN risk_raw IN ('ALTO', 'HIGH', 'A', 'H')             THEN 'ALTO'
      WHEN risk_raw IS NULL OR risk_raw IN ('', 'N/A')         THEN 'NAO_CLASSIFICADO'
      ELSE 'NAO_CLASSIFICADO'
    END                                                        AS risk,

    -- -------------------------------------------------------------------
    -- BLOCO DE UNIDADE DE SAÚDE
    -- -------------------------------------------------------------------
    -- health_unit_key: ID canônico da UBS, vindo de organization.id (N4).
    -- Se ausente, usa 'UNK_UHS' para preservar linha sem quebrar joins.
    COALESCE(NULLIF(TRIM(org_id_raw), ''), 'UNK_UHS')         AS health_unit_key,

    -- -------------------------------------------------------------------
    -- BLOCO DE FLAG DE TESTE
    -- -------------------------------------------------------------------
    -- Registros de teste são identificados pela cidade da organização.
    -- Valores conhecidos de cidades-teste: 'Fake City', 'Test', 'Teste'.
    -- NULL indica ausência de informação, não necessariamente teste.
    CASE
      WHEN UPPER(TRIM(org_city_raw)) IN (
             'FAKE CITY', 'TEST', 'TESTE', 'TESTCITY', 'TESTE CITY'
           )                                                   THEN TRUE
      WHEN org_city_raw IS NULL OR TRIM(org_city_raw) = ''    THEN NULL
      ELSE FALSE
    END                                                        AS is_test_record,

    -- -------------------------------------------------------------------
    -- BLOCO DE METADADOS
    -- -------------------------------------------------------------------
    TIMESTAMP_SECONDS(created_at_seconds)                      AS created_at,
    participant_group,
    registration_source,

    -- Campos auxiliares para o cálculo do quality_flag (próxima etapa)
    gender_raw,
    risk_raw,
    org_id_raw

  FROM users_extracted
),

-- ============================================================================
-- PASSO 3: Avaliação de qualidade por registro e filtragem de teste
-- ============================================================================
-- Calculamos o record_quality_flag baseado na presença de campos críticos.
-- Registros marcados como teste (is_test_record = TRUE) são excluídos.
--
-- Regras de qualidade:
--   FAIL  → participant_master_id nulo (impossível após filtro, mas defensivo)
--   WARN  → gender = NAO_INFORMADO OU risk = NAO_CLASSIFICADO OU
--            health_unit_key = UNK_UHS (dados incompletos mas usáveis)
--   OK    → todos os campos críticos presentes
users_with_quality AS (
  SELECT
    participant_master_id,
    source_document_id,
    source_user_id,
    source_respondent_id,
    id_reconciliation_status,
    gender,
    risk,
    health_unit_key,
    is_test_record,
    created_at,
    participant_group,
    registration_source,

    -- Semáforo de qualidade por linha
    CASE
      WHEN participant_master_id IS NULL OR TRIM(participant_master_id) = ''
        THEN 'FAIL'
      WHEN gender = 'NAO_INFORMADO'
        OR risk = 'NAO_CLASSIFICADO'
        OR health_unit_key = 'UNK_UHS'
        THEN 'WARN'
      ELSE 'OK'
    END                                                        AS record_quality_flag

  FROM users_normalized

  -- Excluir registros de teste confirmados.
  -- Registros com is_test_record = NULL (informação ausente) são preservados
  -- como WARN, pois podem ser registros legítimos com dado incompleto.
  WHERE COALESCE(is_test_record, FALSE) = FALSE
)

-- ============================================================================
-- RESULTADO FINAL
-- ============================================================================
-- Uma linha por participante analítico. Nenhum campo PII. Todos os campos
-- têm tipo, domínio e tratamento de ausência documentados no contrato Fase 1.
SELECT
  participant_master_id,
  source_document_id,
  source_user_id,
  source_respondent_id,         -- NULL (D1) — awaiting decision
  id_reconciliation_status,
  gender,
  risk,
  health_unit_key,
  is_test_record,
  created_at,
  participant_group,
  registration_source,
  record_quality_flag

FROM users_with_quality
;
