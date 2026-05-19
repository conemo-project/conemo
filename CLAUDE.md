# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

CONEMO is a Streamlit dashboard that monitors a mental health intervention study. It tracks participants enrolled at UBS (primary care units), their session progress across therapeutic journeys (depression/PHQ-9, anxiety/GAD-7), clinical scores, and patient feedback. Data comes from Google BigQuery (curated views) or a local PARQUET fallback.

## Running the dashboard

```bash
pip install -r requirements.txt
streamlit run Code/PY/dashboard_conemo.py
```

The dashboard runs on `http://localhost:8501`. Streamlit config is in `.streamlit/config.toml`.

## Data modes

**BigQuery (canonical source):** `load_data()` tries BigQuery first via `load_data_from_bigquery()`. Credentials come from `st.secrets["gcp_service_account"]` on Streamlit Cloud, or `GOOGLE_APPLICATION_CREDENTIALS` locally. The dashboard **never** falls back to the GCE metadata server — a missing credential raises a `RuntimeError` immediately.

**Parquet (fallback):** If BigQuery fails, `load_data()` falls back to `Data/PARQUET/conemo_dados_consolidados_raw_04_03_2026.parquet`. This directory is **not tracked in git** and must be copied manually.

**Operational cutoff:** `DASHBOARD_CUTOFF_TS = "2026-01-28 00:00:00 UTC"` — all BigQuery queries filter `p.created_at >= TIMESTAMP(cutoff)`.

## Code architecture

`Code/PY/dashboard_conemo.py` is a single-file Streamlit app (~1340 lines). Execution is top-to-bottom:

1. **BigQuery client** — `_get_bq_client()`: tries `st.secrets` → `GOOGLE_APPLICATION_CREDENTIALS` → raises `RuntimeError`. Never uses ADC metadata server.
2. **Data loader (BigQuery)** — `load_data_from_bigquery()`: JOINs five curated views plus a `raw_perfil` CTE. Returns a flat DataFrame with one row per session event.
3. **Data loader (Parquet legacy)** — inside `load_data()`: invokes `parse_user_legacy()` to unpack nested Firestore JSON from the old parquet schema.
4. **Protocol classification** — `add_conemo_protocol_status(df)`: called on every code path, immediately before `df_all` is created. Classifies each row as `"Aderiu"` / `"Não Aderiu"` using `health_unit_key == 'UNK_UHS'` as the canonical criterion (text fallback when key is missing). Never removes rows.
5. **Global DataFrames** — `df_all` (full), `df_main` (Aderiu only), `df_nao_aderiu`, `df_main_users` (deduplicated by `user_id`).
6. **Sidebar** — timestamp display, `🔄` button (`st.cache_data.clear()` + `st.rerun()`), and `st.sidebar.radio` page selector.
7. **Pages (if/elif blocks)**:
   - `📊 Estatísticas por UBS` — main analytics, UBS-first view
   - `🔍 Governança — Não Aderiu` — governance page for protocol non-adherents
   - `👤 Consulta auxiliar` — individual participant lookup with longitudinal PHQ/GAD history via `load_history_from_bigquery()`
8. **Clinical helpers** — `phq_severity()`, `gad_severity()`, `age_group()`, `normalize_gender()` translate raw scores/values to clinical labels.

## BigQuery schema

**Curated views** (dataset `conemo-412202.firestore_curated`):

| View | Purpose |
|---|---|
| `cur_participant_current_v1` | One row per participant; key: `participant_master_id`. PII-free. `health_unit_key = 'UNK_UHS'` means no UBS assigned. |
| `cur_session_current_v1` | Session events; joins on `participant_master_id` |
| `cur_health_unit_v1` | UBS dimension; joins on `health_unit_key` |
| `cur_score_current_v1` | PHQ/GAD scores (saneada Fase D.2); `instrument` values: `PHQ`, `PHQ_JOURNEY`, `GAD`, `GAD_JOURNEY` |
| `cur_journey_current_v1` | Journey enrollment |

**Raw tables** (dataset `conemo-412202.firestore_export`): `users_raw_latest`, `sessions_raw_latest`, `journeys_raw_latest`, `patient_feedback_raw_latest`. The main query still pulls PII fields (`name`, `email`, `birthDate`) from `users_raw_latest` directly via a `raw_perfil` CTE, by professor decision.

**Score deduplication rule:** `ROW_NUMBER() OVER (PARTITION BY participant_id, instrument ORDER BY score_timestamp DESC, source_document_id DESC)` — only `rn = 1` is used.

**Test record exclusion:** three independent guards — `p.is_test_record IS NOT TRUE` (curated), `r.is_test_raw = 'false'` (raw `$.isTest`), `r.is_test_user_raw = 'false'` (raw `$.isTestUser`). `NULL` values in raw flags are treated as non-test (safe inclusion).

## SQL layer (`sql/`)

Nine `.sql` files define the curated views and marts. Prefix convention: `fase2_cur_*` = curated shared views; `fase3_mart_*` = analytical marts. These are deployed manually to BigQuery — there is no migration runner.

## Key data invariants

- `ubs_city` → Title Case; `ubs_name` → UPPERCASE; both filled with `"Não respondeu"` when NULL.
- `conemo_protocol_status` must be present on every DataFrame before any page renders — `validate_runtime_contract()` checks this.
- The `🔄` button must remain visible per a binding coordination decision (Fase B, 2026-04-06).

## Workflow and governance

**New phases require explicit approval from the project coordinator before implementation.** All technical work must be on a feature branch; direct commits to `main` are prohibited.

Canonical documents:
- `Docs/Plano-implementacao-dashboard.md` — implementation plan V.2.0.0 (canonical reference)
- `Docs/fase-e-handoff-final.md` — current phase handoff

Current state: Fase D.3 (PHQ/GAD reintegration) is merged into `main`. Fase D.4 (longitudinal history per participant) is partially implemented in `load_history_from_bigquery()`.
