# Fase A.1 — Verificacao complementar no BigQuery do filtro de usuarios pre-merge PR #2

**Data:** 24/04/2026
**Repositorio institucional:** `conemo-project/conemo`
**Branch:** `fechamento-rodada-preparacao-pr`
**Projeto BigQuery:** `conemo-412202`
**Escopo:** diagnostico complementar somente leitura, sem alteracao funcional.

## 1) Objetivo

Complementar a Fase A com verificacao direta no BigQuery institucional antes de qualquer implementacao funcional da Fase B.

A verificacao buscou confirmar objetos atuais, nomes fisicos, campo de data de entrada, contagens atualizadas e ponto recomendado para aplicar a regra operacional urgente:

> usuario ativo, para esta correcao urgente, significa usuario/paciente com `createdAt >= 2026-01-01`, salvo se o BigQuery revelar campo canonico melhor.

## 2) Fontes e arquivos lidos

Governanca:

- `Docs/RULES.md` e `Docs/Workflow-Projeto.md` lidos integralmente a partir do workspace raiz do projeto, pois esses arquivos nao estao presentes no clone institucional `_clone_oficial_conemo`.
- `AGENTS.md`: ausente no clone institucional.

Arquivos obrigatorios lidos no clone institucional:

- `Docs/Plano-implementacao-dashboard.md`
- `README.md`
- `Docs/fechamento-rodada-preparacao-pr.md`
- `Docs/correcao-pre-merge-pr2-diagnostico-filtro-usuarios.md`
- `Code/PY/dashboard_conemo.py`
- `sql/fase2_cur_participant_current_v1.sql`
- `sql/fase2_cur_journey_current_v1.sql`
- `sql/fase2_cur_session_current_v1.sql`
- `sql/fase2_cur_score_current_v1.sql`
- `sql/fase2_cur_health_unit_v1.sql`
- `sql/fase2_validacao_contagens.sql`
- `sql/fase3_mart_dashboard_export_v1.sql`
- `sql/fase3_mart_ubs_monitoring_v1.sql`
- `sql/fase3_mart_project_management_v1.sql`

Documentacao local relacionada ao PR #2 lida quando disponivel:

- `Docs/Nota-Decisoria-Pull-Request-02.md`
- `Docs/parecer-auditoria-preparacao-pr-2026-04-08.md`
- `Docs/parecer-auditoria-abertura-pr-2026-04-08.md`
- `Docs/parecer-encerramento-fase-6-plano-preprocessamento-2026-04-08.md`

Referencias oficiais usadas como criterio operacional para as consultas:

- BigQuery `INFORMATION_SCHEMA`: <https://cloud.google.com/bigquery/docs/information-schema-intro>
- BigQuery `INFORMATION_SCHEMA.COLUMNS`: <https://docs.cloud.google.com/bigquery/docs/information-schema-columns>
- BigQuery dry run: <https://cloud.google.com/bigquery/docs/running-queries>

## 3) Ambiente BigQuery confirmado

Comandos diagnosticos executados sem criacao, alteracao ou exclusao de objetos:

- projeto ativo do `gcloud`: `conemo-412202`;
- conta autenticada ativa: `ricardo-ceneviva@conemo-412202.iam.gserviceaccount.com`;
- conta adicional listada, sem status ativo: `ceneviva@gmail.com`;
- BigQuery CLI: `bq` versao `2.1.31`;
- datasets visiveis:
  - `conemo-412202:firestore_export`, localizacao `southamerica-east1`;
  - `conemo-412202:firestore_curated`, localizacao `southamerica-east1`.

O ambiente e compativel com consultas diagnosticas somente leitura. Todas as consultas BigQuery foram executadas com `--location=southamerica-east1`.

## 4) Objetos BigQuery verificados

Consulta em `INFORMATION_SCHEMA.TABLES` confirmou os objetos atuais:

| Dataset | Objeto | Tipo |
|---|---|---|
| `firestore_export` | `users_raw_changelog` | tabela |
| `firestore_export` | `users_raw_latest` | view |
| `firestore_export` | `sessions_raw_changelog` | tabela |
| `firestore_export` | `sessions_raw_latest` | view |
| `firestore_export` | `journeys_raw_changelog` | tabela |
| `firestore_export` | `journeys_raw_latest` | view |
| `firestore_export` | `notifications_raw_changelog` | tabela |
| `firestore_export` | `notifications_raw_latest` | view |
| `firestore_export` | `patient_feedback_raw_changelog` | tabela |
| `firestore_export` | `patient_feedback_raw_latest` | view |
| `firestore_curated` | `cur_participant_current_v1` | view |
| `firestore_curated` | `cur_journey_current_v1` | view |
| `firestore_curated` | `cur_session_current_v1` | view |
| `firestore_curated` | `cur_score_current_v1` | view |
| `firestore_curated` | `cur_health_unit_v1` | view |
| `firestore_curated` | `mart_dashboard_export_v1` | view |
| `firestore_curated` | `mart_ubs_monitoring_v1` | view |
| `firestore_curated` | `mart_project_management_v1` | view |

Dry run da consulta de metadados de tabelas: `10.485.760` bytes estimados.

## 5) Nomes fisicos verificados

### 5.1 Camada bruta

`INFORMATION_SCHEMA.COLUMNS` confirmou que as views brutas principais possuem colunas fisicas top-level:

- `users_raw_latest`: `document_name`, `document_id`, `timestamp`, `event_id`, `operation`, `data`, `old_data`, `path_params`;
- `sessions_raw_latest`: `document_name`, `document_id`, `timestamp`, `event_id`, `operation`, `data`, `old_data`, `path_params`;
- `journeys_raw_latest`: `document_name`, `document_id`, `timestamp`, `event_id`, `operation`, `data`, `old_data`.

Observacao relevante: `journeys_raw_latest` nao expoe `path_params` no BigQuery atual, embora `sql/fase2_cur_journey_current_v1.sql`, linhas 27-34, documente e use esse campo como origem do vinculo `userId`.

### 5.2 Camada curada e marts

`cur_participant_current_v1` expoe os campos relevantes:

- identificador: `participant_master_id`;
- identificadores de origem: `source_document_id`, `source_user_id`, `source_respondent_id`;
- data de entrada curada: `created_at` (`TIMESTAMP`);
- flag observavel de teste: `is_test_record` (`BOOL`);
- metadados: `participant_group`, `registration_source`, `record_quality_flag`.

As marts existem como views, mas nao expoem campo de data de entrada por participante. Elas trazem metricas agregadas, como `participant_count`, `participant_count_ubs`, `active_participants_ubs` e `participant_count_global`.

## 6) Campo canonico recomendado para data de entrada

O BigQuery nao revelou campo canonico melhor que `createdAt`/`created_at`.

Campo recomendado:

- na fonte bruta: `users_raw_latest.data`, caminho JSON `$.createdAt._seconds`;
- na camada curada: `cur_participant_current_v1.created_at`;
- no dashboard atual baseado em Parquet: `json_data_user.createdAt._seconds`, conforme ja diagnosticado na Fase A.

Justificativa observada:

1. `sql/fase2_cur_participant_current_v1.sql`, linhas 82-85, extrai `JSON_VALUE(DATA, '$.createdAt._seconds')`;
2. `sql/fase2_cur_participant_current_v1.sql`, linha 167, transforma esse valor em `TIMESTAMP_SECONDS(created_at_seconds)`;
3. `sql/fase2_cur_participant_current_v1.sql`, linhas 229-239, publica `created_at` na saida curada;
4. no BigQuery atual, `createdAt` aparece como objeto JSON em 426 de 481 usuarios brutos, e `createdAt._seconds` e castavel em 426 de 481;
5. candidatos alternativos testados na fonte bruta (`created_at`, `entered_at`, `registration_date`, `first_submission_at`) tiveram cobertura zero.

Conclusao: a regra operacional `createdAt >= 2026-01-01` permanece adequada para esta correcao urgente, usando `cur_participant_current_v1.created_at` como equivalente curado.

## 7) Identificadores e flags de teste/invalidade

Identificadores observados:

- bruto: `users_raw_latest.document_id` como identificador fisico; `JSON_VALUE(data, '$.id')` apareceu em 428 de 481 registros;
- curado: `participant_master_id`, `source_document_id`, `source_user_id`;
- dashboard atual: `user_id` no Parquet, conforme Fase A.

Flags/campos observados:

- bruto:
  - `isTestUser`: presente em 17 registros;
  - `invalid`: presente em 9 registros;
  - `organization.testEnvironment`: presente em 7 registros;
  - `organization.city`: presente em 281 registros;
- curado:
  - `is_test_record`, derivado apenas de cidade de teste, conforme `sql/fase2_cur_participant_current_v1.sql`, linhas 153-162;
  - a view curada exclui `is_test_record = TRUE`, preservando nulos como possiveis registros legitimos, conforme linhas 218-221.

Limite importante: `is_test_record` nao incorpora, no SQL atual, `isTestUser`, `invalid` ou `organization.testEnvironment`. Portanto, essas flags servem para diagnostico de exclusao/teste, mas nao substituem a decisao operacional vinculante de usuario ativo por data de criacao.

## 8) Contagens atualizadas

### 8.1 Fonte bruta `firestore_export.users_raw_latest`

Dry run da consulta de contagem: `9.646.217` bytes estimados.

| Medida | Contagem |
|---|---:|
| Linhas/usuarios brutos por `document_id` | 481 |
| `createdAt >= 2026-01-01` | 230 |
| `createdAt < 2026-01-01` | 196 |
| `createdAt` ausente | 55 |
| Registros com alguma flag observavel de teste/invalidade | 29 |
| Pos-2026 com alguma flag observavel de teste/invalidade | 4 |
| Pos-2026 sem flag observavel de teste/invalidade | 226 |
| Menor `createdAt` observado | 2024-08-20 |
| Maior `createdAt` observado | 2026-04-24 |

### 8.2 Fonte curada `firestore_curated.cur_participant_current_v1`

Dry run da consulta de contagem principal: `9.646.217` bytes estimados.
Dry run complementar para nulos em `is_test_record`: `9.778.126` bytes estimados.

| Medida | Contagem |
|---|---:|
| Linhas curadas | 480 |
| Participantes distintos por `participant_master_id` | 480 |
| `created_at >= 2026-01-01` | 230 |
| `created_at < 2026-01-01` | 196 |
| `created_at` ausente | 54 |
| `is_test_record = TRUE` | 0 |
| `is_test_record = FALSE` | 274 |
| `is_test_record IS NULL` | 206 |
| Pos-2026 com `is_test_record = TRUE` | 0 |
| Pos-2026 sem `is_test_record = TRUE`, tratando nulo como sem flag confirmada | 230 |

Interpretacao: a camada curada confirma a contagem pos-2026 da fonte bruta, mas nao carrega como exclusao confirmada as flags brutas `isTestUser`, `invalid` e `organization.testEnvironment`.

### 8.3 Marts

As marts foram verificadas por metadados, mas suas contagens nao puderam ser produzidas porque os dry-runs falharam antes da execucao:

- `cur_journey_current_v1`;
- `mart_dashboard_export_v1`;
- `mart_project_management_v1`;
- `mart_ubs_monitoring_v1`.

Erro observado em todas as consultas dependentes de jornada:

```text
Unrecognized name: path_params; failed to parse view
'conemo-412202.firestore_curated.cur_journey_current_v1' at [30:9]
```

Evidencia tecnica: `INFORMATION_SCHEMA.COLUMNS` confirmou que `journeys_raw_latest` nao possui `path_params`, enquanto `sql/fase2_cur_journey_current_v1.sql`, linhas 27-34, espera esse campo.

Conclusao: as marts nao devem ser usadas como fonte de Fase B ate que a definicao de jornada seja saneada em etapa propria autorizada. Esta Fase A.1 nao alterou SQL nem objetos BigQuery.

## 9) Comparacao com Fase A local e contagem do professor

| Fonte | Total | Pos-2026 | Pos-2026 sem flags observaveis | Observacao |
|---|---:|---:|---:|---|
| Parquet local da Fase A | 389 | 138 | 136 | Snapshot local usado pelo dashboard atual. |
| BigQuery bruto atual | 481 | 230 | 226 | Fonte institucional atual em `users_raw_latest`. |
| BigQuery curado atual | 480 | 230 | 230 sem `is_test_record=TRUE` | `is_test_record` curado nao reflete todas as flags brutas. |
| Contagem informada pelo professor | aprox. 222 | aprox. 222 | nao informado | Compatibilidade aproximada com BigQuery atual. |

Explicacao da divergencia 138 vs. aproximadamente 222:

1. o Parquet local do dashboard e da Fase A e um snapshot defasado em relacao ao BigQuery atual;
2. o BigQuery atual contem 481 usuarios brutos contra 389 participantes unicos no Parquet local;
3. a diferenca pos-2026 e material: 230 no BigQuery atual contra 138 no Parquet local;
4. a contagem do professor, aproximadamente 222, fica muito mais proxima do BigQuery atual: 230 usando apenas `createdAt >= 2026-01-01`, ou 226 se forem excluidas flags brutas observaveis de teste/invalidade;
5. a diferenca residual entre 226/230 e aproximadamente 222 pode decorrer de snapshot, horario de consulta, criterio manual adicional, ou flags/invalidacoes ainda nao materializadas como campo canonico. Nao ha evidencia suficiente para substituir `createdAt` por outro campo.

## 10) Consultas SQL usadas

As consultas nao retornaram PII; apenas metadados e agregacoes.

Metadados:

```sql
SELECT table_schema, table_name, table_type
FROM `conemo-412202.region-southamerica-east1.INFORMATION_SCHEMA.TABLES`
WHERE table_schema IN ('firestore_export', 'firestore_curated');
```

```sql
SELECT table_schema, table_name, column_name, data_type
FROM `conemo-412202.region-southamerica-east1.INFORMATION_SCHEMA.COLUMNS`
WHERE table_schema IN ('firestore_export', 'firestore_curated');
```

Campos candidatos na fonte bruta:

```sql
SELECT
  COUNT(*) AS total_rows,
  COUNT(DISTINCT document_id) AS distinct_document_id,
  COUNTIF(JSON_QUERY(data, '$.createdAt') IS NOT NULL) AS createdAt_object_nonnull,
  COUNTIF(JSON_VALUE(data, '$.createdAt._seconds') IS NOT NULL) AS createdAt_seconds_nonnull,
  COUNTIF(SAFE_CAST(JSON_VALUE(data, '$.createdAt._seconds') AS INT64) IS NOT NULL) AS createdAt_seconds_castable,
  COUNTIF(JSON_VALUE(data, '$.created_at') IS NOT NULL) AS created_at_nonnull,
  COUNTIF(JSON_VALUE(data, '$.entered_at') IS NOT NULL) AS entered_at_nonnull,
  COUNTIF(JSON_VALUE(data, '$.registration_date') IS NOT NULL) AS registration_date_nonnull,
  COUNTIF(JSON_VALUE(data, '$.first_submission_at') IS NOT NULL) AS first_submission_at_nonnull
FROM `conemo-412202.firestore_export.users_raw_latest`;
```

Contagem bruta:

```sql
WITH users AS (
  SELECT
    document_id,
    TIMESTAMP_SECONDS(SAFE_CAST(JSON_VALUE(data, '$.createdAt._seconds') AS INT64)) AS created_at,
    (
      IFNULL(LOWER(TRIM(JSON_VALUE(data, '$.isTestUser'))) = 'true', FALSE)
      OR IFNULL(LOWER(TRIM(JSON_VALUE(data, '$.invalid'))) = 'true', FALSE)
      OR IFNULL(LOWER(TRIM(JSON_VALUE(data, '$.organization.testEnvironment'))) = 'true', FALSE)
      OR IFNULL(REGEXP_CONTAINS(LOWER(TRIM(JSON_VALUE(data, '$.organization.city'))), r'(test|teste|fake|load|carga|break|quebra)'), FALSE)
    ) AS test_invalid_flag
  FROM `conemo-412202.firestore_export.users_raw_latest`
)
SELECT
  COUNT(DISTINCT document_id) AS distinct_users,
  COUNT(DISTINCT IF(created_at >= TIMESTAMP('2026-01-01'), document_id, NULL)) AS created_ge_2026_01_01,
  COUNT(DISTINCT IF(created_at < TIMESTAMP('2026-01-01'), document_id, NULL)) AS created_lt_2026_01_01,
  COUNT(DISTINCT IF(created_at IS NULL, document_id, NULL)) AS created_at_missing,
  COUNT(DISTINCT IF(created_at >= TIMESTAMP('2026-01-01') AND test_invalid_flag, document_id, NULL)) AS post_2026_test_invalid_flagged
FROM users;
```

Contagem curada:

```sql
SELECT
  COUNT(DISTINCT participant_master_id) AS distinct_participants,
  COUNT(DISTINCT IF(created_at >= TIMESTAMP('2026-01-01'), participant_master_id, NULL)) AS created_ge_2026_01_01,
  COUNT(DISTINCT IF(created_at < TIMESTAMP('2026-01-01'), participant_master_id, NULL)) AS created_lt_2026_01_01,
  COUNT(DISTINCT IF(created_at IS NULL, participant_master_id, NULL)) AS created_at_missing,
  COUNTIF(is_test_record IS TRUE) AS is_test_true_rows,
  COUNTIF(is_test_record IS FALSE) AS is_test_false_rows,
  COUNTIF(is_test_record IS NULL) AS is_test_null_rows
FROM `conemo-412202.firestore_curated.cur_participant_current_v1`;
```

## 11) Localizacao do ponto atual do dashboard

`Code/PY/dashboard_conemo.py` continua usando Parquet local:

- linhas 50-52: `load_data()` executa `pd.read_parquet(PARQUET_PATH)`;
- linhas 60-111: extrai campos do JSON do usuario;
- linhas 141-145: aplica filtro atual de cidades invalidas;
- linha 147: retorna o DataFrame que alimenta as visualizacoes.

Portanto, o ponto funcional atual para um filtro urgente no dashboard continua sendo `load_data()`, caso a Fase B seja autorizada.

## 12) Riscos e limitacoes

1. O dashboard atual nao consome BigQuery diretamente; consome Parquet local. Mesmo com filtro correto, a contagem exibida pelo dashboard permanecera limitada ao snapshot local ate haver atualizacao de fonte.
2. A divergencia 138 vs. 230/226 indica defasagem relevante do Parquet local.
3. As marts existem, mas nao puderam ser consultadas por falha de parse em `cur_journey_current_v1`.
4. `is_test_record` curado nao cobre todas as flags brutas de teste/invalidade.
5. Nao foi encontrada flag canonica unica de piloto, carga ou quebra.
6. Nenhum dado individual foi exportado ou registrado; apenas contagens e metadados foram usados.

## 13) Recomendacao para Fase B

Recomendacao objetiva: **avancar com ressalva, usando `createdAt >= 2026-01-01` como regra operacional e `cur_participant_current_v1.created_at` como referencia canonica BigQuery.**

Camada recomendada:

1. **Implementacao urgente no dashboard:** aplicar o filtro em `load_data()` enquanto o dashboard continuar consumindo Parquet local, usando `json_data_user.createdAt._seconds >= 2026-01-01` e excluindo datas ausentes.
2. **Referencia institucional para validacao:** usar `firestore_curated.cur_participant_current_v1.created_at`.
3. **Nao usar marts como fonte da Fase B neste momento**, pois os dry-runs das marts falham por dependencia de `cur_journey_current_v1`.
4. Se o professor exigir que a contagem exibida pelo dashboard reflita o BigQuery atual, a Fase B deve incluir decisao explicita de atualizacao/migracao da fonte do dashboard, pois o Parquet local explica a divergencia.

A Fase B nao deve usar `enabled = true` nem `journey_status = ACTIVE` como criterio mestre de usuario ativo.

## 14) Validacao de escopo da Fase A.1

- Nenhum codigo funcional foi alterado.
- Nenhum SQL ou mart foi alterado.
- Nenhum objeto BigQuery foi criado, substituido ou excluido.
- Nomes fisicos foram verificados no BigQuery via `INFORMATION_SCHEMA`.
- Contagens atualizadas foram produzidas no BigQuery para fonte bruta e camada curada.
- A divergencia 138 vs. aproximadamente 222 foi analisada.
- A regra `createdAt >= 2026-01-01` foi confirmada; nao foi encontrado campo canonico melhor.
- A Fase B nao foi iniciada.
- O PR #2 permanece aberto e nao foi mergeado.
