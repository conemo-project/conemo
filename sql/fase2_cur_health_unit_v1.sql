-- =============================================================================
-- cur_health_unit_v1.sql
-- Entidade: Dimensão padronizada de unidades de saúde (UBS/município)
-- Fonte: conemo-412202.firestore_export.users_raw_latest (subcampo organization)
-- Destino: conemo-412202.firestore_curated.cur_health_unit_v1
-- Camada: B — curada compartilhada (BigQuery-first)
-- Versão: v1
-- Data: 2026-04-07
-- Fase: 2 — Implementação mínima da camada curada
-- Branch: fase-2-implementacao-camada-curada-minima
-- =============================================================================

-- ----------------------------------------------------------------------------
-- OBJETIVO DESTA VIEW
-- ----------------------------------------------------------------------------
-- Construir a dimensão padronizada de unidades de saúde (UBS e município),
-- com granularidade de 1 linha por unidade (health_unit_key).
--
-- Esta dimensão é referenciada por cur_participant_current_v1 via
-- health_unit_key e serve como base de filtros territoriais no dashboard
-- e em agregações operacionais do SGBD.
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- NOTAS DE IMPLEMENTAÇÃO
-- ----------------------------------------------------------------------------
-- N4 (LOCALIZAÇÃO): health_unit_key vem de DATA.$.organization.id
--   A referência do contrato Fase 1 ("users_raw_latest.data.path_params")
--   está incorreta — path_params é vazio para usuários. A fonte real é
--   DATA.$.organization.id, conforme verificação técnica Etapa 2.1.
--
-- NORMALIZAÇÃO ubs_name v1:
--   Versão inicial: trim + uppercase. Dicionário de equivalências de
--   abreviações será incorporado em versão futura conforme levantamento
--   das variantes ortográficas no ambiente de produção.
--
-- NORMALIZAÇÃO ubs_city v1:
--   Versão inicial: trim + INITCAP (caixa título). Harmonização de variantes
--   (ex: "Jaguariúna" vs "Jaguariuna") será incorporada em versão futura.
--
-- FILTRO DE TESTE:
--   Registros com cidades identificadas como teste são excluídos.
--   Registros com organização ausente não compõem esta dimensão.
-- ----------------------------------------------------------------------------

CREATE OR REPLACE VIEW `conemo-412202.firestore_curated.cur_health_unit_v1` AS

-- ============================================================================
-- PASSO 1: Extração dos atributos de organização de cada usuário
-- ============================================================================
-- Cada usuário pertence a uma organização. Extraímos os atributos de
-- organização e depois deduplicamos por health_unit_key para obter
-- a dimensão de UBS (1 linha por unidade).
WITH orgs_extracted AS (
  SELECT
    -- ID da organização: nossa health_unit_key canônica
    TRIM(JSON_VALUE(DATA, '$.organization.id'))                AS org_id_raw,

    -- Nome da UBS: normalizado para uppercase e sem espaços extras
    TRIM(UPPER(JSON_VALUE(DATA, '$.organization.name')))       AS ubs_name_raw,

    -- Cidade: normalizada para título (INITCAP) e sem espaços extras
    TRIM(JSON_VALUE(DATA, '$.organization.city'))              AS ubs_city_raw

  FROM `conemo-412202.firestore_export.users_raw_latest`

  WHERE document_id IS NOT NULL
    -- Excluir registros de teste (pela cidade da organização)
    AND UPPER(TRIM(JSON_VALUE(DATA, '$.organization.city')))
          NOT IN ('FAKE CITY', 'TEST', 'TESTE', 'TESTCITY', 'TESTE CITY')
    -- Excluir registros sem organização
    AND JSON_VALUE(DATA, '$.organization.city') IS NOT NULL
    AND TRIM(JSON_VALUE(DATA, '$.organization.city')) != ''
),

-- ============================================================================
-- PASSO 2: Deduplicação e normalização dos atributos de UBS
-- ============================================================================
-- Uma UBS pode aparecer em múltiplos registros de usuário. Usamos DISTINCT
-- para obter uma linha por combinação (org_id, ubs_name, ubs_city).
-- A granularidade final é 1 linha por health_unit_key (org_id).
orgs_distinct AS (
  SELECT DISTINCT
    org_id_raw,
    ubs_name_raw,
    ubs_city_raw
  FROM orgs_extracted
  WHERE org_id_raw IS NOT NULL
    AND TRIM(org_id_raw) != ''
),

-- ============================================================================
-- PASSO 3: Aplicação de substituições de ausência e derivação de status
-- ============================================================================
-- Campos ausentes recebem valores de missingness conforme contrato Fase 1.
-- health_unit_status é derivado: ACTIVE se a unidade passou pelos filtros.
orgs_normalized AS (
  SELECT
    -- Chave canônica da UBS (N4: vem de organization.id)
    COALESCE(NULLIF(org_id_raw, ''), 'UNK_UHS')               AS health_unit_key,

    -- Nome padronizado da UBS
    -- v1: uppercase + trim. Dicionário de abreviações em versão futura.
    COALESCE(NULLIF(ubs_name_raw, ''), 'NI')                   AS ubs_name,

    -- Cidade padronizada
    -- v1: INITCAP + trim. Mapeamento de variantes em versão futura.
    COALESCE(NULLIF(INITCAP(ubs_city_raw), ''), 'UNK')         AS ubs_city,

    -- Status operacional da unidade:
    -- ACTIVE: unidade aparece com dados reais (já filtrado de teste acima)
    'ACTIVE'                                                   AS health_unit_status

  FROM orgs_distinct
  WHERE org_id_raw IS NOT NULL
    AND TRIM(org_id_raw) != ''
    AND org_id_raw != 'UNK_UHS'
)

-- ============================================================================
-- RESULTADO FINAL
-- ============================================================================
-- Uma linha por unidade de saúde padronizada. Serve como dimensão de
-- referência para joins e filtros em todo o modelo analítico.
SELECT
  health_unit_key,
  ubs_name,
  ubs_city,
  health_unit_status

FROM orgs_normalized
;
