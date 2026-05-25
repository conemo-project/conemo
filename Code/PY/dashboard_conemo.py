from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import google.auth
from google.cloud import bigquery
from google.oauth2 import service_account

st.set_page_config(page_title="CONEMO Dashboard", page_icon="🏥", layout="wide")

# ─── Constantes ───────────────────────────────────────────────────────────────
DASHBOARD_CUTOFF_TS = "2026-01-28 00:00:00 UTC"
DASHBOARD_CUTOFF_SECONDS = int(pd.Timestamp(DASHBOARD_CUTOFF_TS).timestamp())
_BQ_PROJECT = "conemo-412202"
_BQ_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


# =============================================================================
# AUTENTICAÇÃO
# =============================================================================

def _get_bq_client() -> bigquery.Client:
    try:
        has_secret = "gcp_service_account" in st.secrets
    except Exception:
        has_secret = False

    if has_secret:
        try:
            info = dict(st.secrets["gcp_service_account"])
            creds = service_account.Credentials.from_service_account_info(info, scopes=_BQ_SCOPES)
            return bigquery.Client(credentials=creds, project=creds.project_id)
        except Exception as exc:
            raise RuntimeError(
                "Secret [gcp_service_account] ausente, incompleto ou inválido no Streamlit Cloud. "
                "Configure os Secrets em Manage app → Settings → Secrets."
            ) from exc

    try:
        creds, project_id = google.auth.default(scopes=_BQ_SCOPES)
        return bigquery.Client(credentials=creds, project=project_id or _BQ_PROJECT)
    except Exception as exc:
        raise RuntimeError(
            "Credenciais BigQuery indisponíveis. "
            "No Streamlit Cloud: configure [gcp_service_account] nos Secrets. "
            "No ambiente local: use credenciais de desenvolvimento seguras (ADC) antes de executar."
        ) from exc


# =============================================================================
# LOADERS
# =============================================================================

def _query_main() -> str:
    return f"""
    WITH score_ranked AS (
      SELECT
        participant_id, instrument, score_total, score_timestamp,
        ROW_NUMBER() OVER (
          PARTITION BY participant_id, instrument
          ORDER BY score_timestamp DESC, source_document_id DESC
        ) AS rn
      FROM `conemo-412202.firestore_curated.cur_score_current_v1`
    ),
    score_latest AS (
      SELECT
        participant_id,
        MAX(CASE WHEN instrument IN ('PHQ','PHQ_JOURNEY') THEN score_total END) AS phq_score,
        MAX(CASE WHEN instrument IN ('GAD','GAD_JOURNEY') THEN score_total END) AS gad_score
      FROM score_ranked WHERE rn = 1
      GROUP BY participant_id
    )
    SELECT
      p.participant_master_id  AS user_id,
      p.health_unit_key,
      s.session_number         AS sessionNumber,
      s.is_completed           AS isCompleted,
      CAST(s.event_timestamp AS STRING) AS completedDate,
      u.ubs_name,
      u.ubs_city,
      p.gender,
      sl.phq_score,
      sl.gad_score,
      p.created_at,
      UNIX_SECONDS(p.created_at) AS created_at_seconds,
      p.is_test_record
    FROM `conemo-412202.firestore_curated.cur_participant_current_v1` p
    LEFT JOIN `conemo-412202.firestore_curated.cur_session_current_v1` s
           ON p.participant_master_id = s.participant_master_id
    LEFT JOIN `conemo-412202.firestore_curated.cur_health_unit_v1` u
           ON p.health_unit_key = u.health_unit_key
    LEFT JOIN score_latest sl ON p.participant_master_id = sl.participant_id
    WHERE p.created_at >= TIMESTAMP('{DASHBOARD_CUTOFF_TS}')
      AND (p.is_test_record IS NOT TRUE)
    """


def _query_historico(participant_id: str) -> str:
    return f"""
    SELECT
      instrument,
      score_total            AS score,
      score_timestamp        AS data_avaliacao,
      score_source           AS fonte,
      source_document_name   AS path_firestore,
      ROW_NUMBER() OVER (
        PARTITION BY instrument
        ORDER BY score_timestamp DESC, source_document_id DESC
      ) AS rn
    FROM `conemo-412202.firestore_curated.cur_score_current_v1`
    WHERE participant_id = '{participant_id}'
      AND instrument IN ('PHQ','PHQ_JOURNEY','GAD','GAD_JOURNEY')
    ORDER BY score_timestamp DESC
    """


def _query_formulario_web() -> str:
    return f"""
    WITH users AS (
      SELECT
        document_id AS patient_id,
        TIMESTAMP_MICROS(
          COALESCE(
            SAFE_CAST(JSON_VALUE(DATA, '$.createdAt._seconds') AS INT64),
            SAFE_CAST(JSON_VALUE(DATA, '$.createdAt.seconds')  AS INT64)
          ) * 1000000
          + DIV(COALESCE(
            SAFE_CAST(JSON_VALUE(DATA, '$.createdAt._nanoseconds') AS INT64),
            SAFE_CAST(JSON_VALUE(DATA, '$.createdAt.nanos')        AS INT64),
            0
          ), 1000)
        ) AS created_at_ts,
        TRIM(UPPER(JSON_VALUE(DATA, '$.gender')))                 AS gender_raw,
        JSON_VALUE(DATA, '$.whatsapp.authorizedNotifications')    AS whatsapp_authorized,
        JSON_QUERY(DATA, '$.lastBaselineDate')                    AS last_baseline_date,
        COALESCE(SAFE_CAST(JSON_VALUE(DATA,'$.isTestUser') AS BOOL), FALSE) AS is_test_user,
        COALESCE(SAFE_CAST(JSON_VALUE(DATA,'$.isTest')     AS BOOL), FALSE) AS is_test,
        JSON_VALUE(DATA, '$.invalid')                             AS is_invalid_raw
      FROM `conemo-412202.firestore_export.users_raw_latest`
    ),
    journeys_enabled AS (
      SELECT
        REGEXP_EXTRACT(document_name, r'/' || 'users' || r'/([^/]+)/') AS user_id,
        COUNT(*) AS num_jornadas
      FROM `conemo-412202.firestore_export.journeys_raw_latest`
      WHERE COALESCE(SAFE_CAST(JSON_VALUE(DATA,'$.enabled') AS BOOL), FALSE) = TRUE
      GROUP BY user_id
    )
    SELECT
      u.patient_id,
      DATE(u.created_at_ts) AS data_cadastro,
      CASE
        WHEN u.gender_raw IN ('F','FEMININO','FEMALE') THEN 'F'
        WHEN u.gender_raw IN ('M','MASCULINO','MALE')  THEN 'M'
        ELSE 'N/I'
      END AS genero,
      CASE WHEN u.whatsapp_authorized = 'true' THEN 'Habilitado' ELSE 'Desabilitado' END AS status_whatsapp,
      CASE WHEN u.last_baseline_date IS NOT NULL THEN 'Sim' ELSE 'Não' END AS completou_form_app,
      j.num_jornadas AS jornadas
    FROM users u
    INNER JOIN journeys_enabled j ON j.user_id = u.patient_id
    WHERE u.created_at_ts >= TIMESTAMP('{DASHBOARD_CUTOFF_TS}')
      AND u.is_test_user IS FALSE
      AND u.is_test     IS FALSE
      AND (u.is_invalid_raw IS NULL OR u.is_invalid_raw = 'false')
    ORDER BY u.created_at_ts ASC
    """



def _query_fw01() -> str:
    """Alias canônico para validação/reauditoria: usa a mesma extração do Formulário Web."""
    return _query_formulario_web()


def _query_fw02() -> str:
    """Alias canônico para validação/reauditoria: usa a mesma extração do Formulário Web."""
    return _query_formulario_web()

def _fetch(query: str) -> pd.DataFrame:
    return _get_bq_client().query(query).to_dataframe()


def _load_main_raw() -> pd.DataFrame:
    df = _fetch(_query_main())
    for col, default in [("ubs_name", "Não respondeu"), ("ubs_city", "Não respondeu"),
                         ("gender", "N/A")]:
        df[col] = df[col].fillna(default)
    df["is_test"] = False
    df["is_test_user"] = False
    df["is_invalid"] = False
    df["is_test_environment"] = False
    return df


@st.cache_data(ttl=900)
def load_data() -> pd.DataFrame:
    try:
        df = _load_main_raw()
        st.session_state["last_update"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        st.error("⚠️ Falha ao carregar dados do BigQuery. Credenciais ausentes ou erro de consulta.")
        st.caption("Modo Beta: execução segura sem detalhar credenciais, paths ou payloads.")
        return _add_protocol_status(pd.DataFrame())

    df["ubs_name"] = df["ubs_name"].str.upper().str.strip()
    df["ubs_city"] = df["ubs_city"].str.strip().str.title()
    df = df[df["ubs_city"].notna() & (~df["ubs_city"].isin({"Fake City", "N/A", ""}))]
    return _add_protocol_status(df)


@st.cache_data(ttl=900)
def load_history(participant_id: str) -> pd.DataFrame:
    try:
        df = _fetch(_query_historico(participant_id))
        df["status_score"] = df["rn"].apply(lambda x: "Atual" if x == 1 else "Histórico")
        df["contexto"] = df["path_firestore"].apply(_score_context)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=900)
def load_formulario_web() -> pd.DataFrame:
    try:
        return _fetch(_query_formulario_web())
    except Exception:
        return pd.DataFrame()


# =============================================================================
# PROCESSAMENTO
# =============================================================================

def _calculate_age(birth_seconds):
    if pd.isna(birth_seconds):
        return None
    try:
        birth = datetime.fromtimestamp(birth_seconds)
        today = datetime.now()
        return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    except Exception:
        return None


def _score_context(path: str) -> str:
    if not path or pd.isna(path):
        return "Vínculo não observável"
    if "journeys/" in path:
        parts = path.split("/")
        if "sessions" in path:
            idx = parts.index("sessions")
            return f"Sessão {parts[idx+1]}" if len(parts) > idx + 1 else "Jornada"
        return "Jornada"
    return "Triagem/Baseline"


def _add_protocol_status(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if df.empty:
        for col in ("conemo_protocol_status", "ubs_status"):
            if col not in df.columns:
                df[col] = pd.Series(dtype="object")
        return df

    def _norm(v) -> str:
        return "" if pd.isna(v) else str(v).strip().upper()

    def _is_nao_aderiu(row: pd.Series) -> bool:
        key = _norm(row.get("health_unit_key", ""))
        if key in {"UNK_UHS", "NO_MATCH"}:
            return True
        if key in {"", "NONE", "NULL", "NAN"}:
            return (_norm(row.get("ubs_name", "")) == "NÃO RESPONDEU"
                    or _norm(row.get("ubs_city", "")) == "NÃO RESPONDEU")
        return False

    mask = df.apply(_is_nao_aderiu, axis=1)
    df["conemo_protocol_status"] = mask.map({True: "Não Aderiu", False: "Aderiu"})
    df["ubs_status"] = mask.map({True: "Sem UBS/município informado", False: "UBS/município informado"})
    return df


def _build_domains(df_all: pd.DataFrame):
    if "conemo_protocol_status" not in df_all.columns:
        st.error("Campo conemo_protocol_status ausente. Análises bloqueadas.")
        empty = df_all.iloc[0:0].copy()
        return empty, empty, empty
    df_main = df_all[df_all["conemo_protocol_status"] == "Aderiu"].copy()
    df_nao = df_all[df_all["conemo_protocol_status"] == "Não Aderiu"].copy()
    df_users = df_main.drop_duplicates(subset="user_id").copy()
    return df_main, df_nao, df_users


def _guard_domains(df_main: pd.DataFrame) -> None:
    if (not df_main.empty) and not df_main["conemo_protocol_status"].eq("Aderiu").all():
        st.error("Erro de integridade: domínio analítico contém registros fora de Aderiu.")
        st.stop()
    if "created_at" in df_main.columns:
        ts = pd.to_datetime(df_main["created_at"], errors="coerce", utc=True).min()
        if pd.notna(ts) and ts < pd.Timestamp(DASHBOARD_CUTOFF_TS):
            st.error("Erro de integridade: domínio analítico contém registros antes do corte temporal.")
            st.stop()


# =============================================================================
# HELPERS CLÍNICOS
# =============================================================================

def phq_severity(score):
    if score is None: return "N/D"
    if score <= 4:  return "Sem depressão"
    if score <= 9:  return "Leve"
    if score <= 14: return "Moderada"
    if score <= 19: return "Moderadamente grave"
    return "Grave"


def gad_severity(score):
    if score is None: return "N/D"
    if score <= 4:  return "Mínima"
    if score <= 9:  return "Leve"
    if score <= 14: return "Moderada"
    return "Grave"


def age_group(v):
    if pd.isna(v): return "Não informado"
    try: v = int(v)
    except Exception: return "Não informado"
    if v < 18:  return "< 18"
    if v <= 29: return "18–29"
    if v <= 39: return "30–39"
    if v <= 49: return "40–49"
    if v <= 59: return "50–59"
    if v <= 69: return "60–69"
    if v <= 79: return "70–79"
    return "80+"


def normalize_gender(value) -> str:
    if pd.isna(value): return "Não informado"
    v = str(value).strip().upper()
    if v in ("F", "FEMININO", "FEMALE", "MULHER", "WOMAN", "2"): return "Feminino"
    if v in ("M", "MASCULINO", "MALE", "HOMEM", "MAN", "1"):     return "Masculino"
    if v in ("OUTRO", "OUTROS", "OTHER", "NAO_BINARIO", "NON-BINARY"): return "Outro"
    return "Não informado"


def _status_caption(label: str) -> None:
    st.caption(f"**{label}** — dashboard permanece **NÃO OPERACIONAL**. "
               "Execução local/validação técnica ≠ operacionalização institucional.")


def _validate_runtime(df_all, df_main, df_nao, df_users):
    critical, warns = [], []
    if df_all is None or df_main is None or df_nao is None:
        return (["DataFrames essenciais ausentes."], [])
    if "conemo_protocol_status" not in df_all.columns:
        return (["Coluna `conemo_protocol_status` ausente em `df_all`."], [])
    if (not df_main.empty) and (df_main["conemo_protocol_status"] == "Não Aderiu").any():
        critical.append("Violação de denominador: `df_main` contém registros `Não Aderiu`.")
    if (not df_nao.empty) and (df_nao["conemo_protocol_status"] == "Aderiu").any():
        critical.append("Violação de segregação: `df_nao_aderiu` contém registros `Aderiu`.")
    if df_users is None or "user_id" not in df_users.columns:
        critical.append("Base `df_main_users` ausente ou sem coluna `user_id`.")
    sensitive = {"cpf", "phone", "telefone", "whatsapp", "address", "endereco"}
    if {c.lower() for c in df_all.columns} & sensitive:
        warns.append("Atenção: colunas sensíveis detectadas; não devem ser exibidas.")
    return critical, warns


def _download(label, df, filename, key):
    blocked_cols = {
        "cpf", "email", "user_name", "name", "phone", "telefone", "address", "endereco",
        "whatsapp", "risk_alert", "human_followup",
        "user_id", "participant_id", "patient_id",
        "birth_seconds", "birthdate", "json", "payload",
    }
    cols_lower = {c.lower() for c in df.columns}
    if cols_lower & blocked_cols:
        st.warning("Exportação bloqueada: CSV contém campos identificáveis/sensíveis (Beta).")
        st.caption("Apenas exportações agregadas ou pseudonimizadas aprovadas são permitidas nesta fase.")
        _download_disabled(f"{label} (bloqueado)", filename, f"{key}_blocked")
        return
    st.download_button(label, df.to_csv(index=False).encode("utf-8"), filename, "text/csv", key=key)


def _download_disabled(label, filename, key):
    st.download_button(label, data=b"", file_name=filename, mime="text/csv", key=key, disabled=True)


# =============================================================================
# PÁGINA: ESTATÍSTICAS POR UBS
# =============================================================================

def _ubs_filtros(df_main: pd.DataFrame, df_users: pd.DataFrame):
    col_f1, col_f2 = st.columns(2)
    all_cities = sorted(df_users["ubs_city"].dropna().unique())
    sel_cities = col_f1.multiselect("Cidade", all_cities, default=all_cities, key="filtro_cidade")
    df_c = df_main[df_main["ubs_city"].isin(sel_cities)] if sel_cities else df_main
    df_cu = df_users[df_users["ubs_city"].isin(sel_cities)] if sel_cities else df_users
    all_ubs = sorted(df_cu["ubs_name"].dropna().unique())
    sel_ubs = col_f2.multiselect("UBS", all_ubs, default=all_ubs, key="filtro_ubs")
    dff = df_c[df_c["ubs_name"].isin(sel_ubs)] if sel_ubs else df_c
    dfu = df_cu[df_cu["ubs_name"].isin(sel_ubs)] if sel_ubs else df_cu
    return dff, dfu


def _ubs_metricas(df_users: pd.DataFrame, dff: pd.DataFrame) -> None:
    total = df_users["user_id"].nunique()
    mean_phq = df_users["phq_score"].mean()
    mean_gad = df_users["gad_score"].mean()
    n_sess = len(dff)
    rate = dff["isCompleted"].sum() / n_sess * 100 if n_sess > 0 else 0
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Participantes", total)
    m2.metric("Média PHQ-9", f"{mean_phq:.1f}" if pd.notna(mean_phq) else "N/D")
    m3.metric("Média GAD-7", f"{mean_gad:.1f}" if pd.notna(mean_gad) else "N/D")
    m4.metric("Conclusão de Sessões", f"{rate:.1f}%")
    st.caption("Métricas calculadas sobre participantes aderentes (df_main_users) com filtros aplicados.")


def _ubs_tab_indicadores(df_users: pd.DataFrame, dff: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Participantes por UBS")
        ubs_count = df_users["ubs_name"].value_counts().reset_index()
        ubs_count.columns = ["UBS", "Participantes"]
        fig = px.bar(ubs_count.sort_values("Participantes"), x="Participantes", y="UBS",
                     orientation="h", color="Participantes", color_continuous_scale="Blues")
        fig.update_layout(showlegend=False, coloraxis_showscale=False, height=420)
        st.plotly_chart(fig, width="stretch")
        st.caption("⚠️ Exportação para uso interno autorizado. Dashboard NÃO OPERACIONAL.")
        _download("⬇️ CSV — Participantes por UBS", ubs_count, "participantes_por_ubs.csv", "dl_ubs_count")

    with col2:
        st.subheader("Média PHQ-9 e GAD-7 por UBS")
        scores_ubs = (df_users.groupby("ubs_name")[["phq_score", "gad_score"]].mean().reset_index()
                      .rename(columns={"ubs_name": "UBS", "phq_score": "PHQ-9", "gad_score": "GAD-7"}))
        fig2 = px.bar(scores_ubs.melt(id_vars="UBS", var_name="Escala", value_name="Média"),
                      x="Média", y="UBS", color="Escala", orientation="h", barmode="group",
                      color_discrete_map={"PHQ-9": "#EF553B", "GAD-7": "#636EFA"})
        fig2.update_layout(height=420)
        st.plotly_chart(fig2, width="stretch")
        st.caption("⚠️ Exportação para uso interno autorizado. Dashboard NÃO OPERACIONAL.")
        _download("⬇️ CSV — Scores PHQ-9 e GAD-7 por UBS", scores_ubs, "scores_phq_gad_por_ubs.csv", "dl_scores_ubs")

    st.divider()
    st.subheader("Resumo por UBS")
    comp_lookup = (dff.groupby("ubs_name")["isCompleted"]
                   .apply(lambda x: x.mean() * 100 if x.count() > 0 else 0.0)
                   .to_dict())
    resumo = (df_users.groupby("ubs_name")
              .agg(Participantes=("user_id", "nunique"),
                   PHQ9=("phq_score", "mean"), GAD7=("gad_score", "mean"))
              .reset_index().rename(columns={"ubs_name": "UBS"}))
    resumo["Conclusão (%)"] = resumo["UBS"].map(comp_lookup).round(1)
    resumo["PHQ-9 Média"] = resumo["PHQ9"].round(1)
    resumo["GAD-7 Média"] = resumo["GAD7"].round(1)
    resumo = resumo[["UBS", "Participantes", "PHQ-9 Média", "GAD-7 Média", "Conclusão (%)"]].sort_values("Participantes", ascending=False)
    with st.expander("Ver tabela completa de resumo por UBS", expanded=True):
        st.dataframe(resumo, width="stretch", hide_index=True)
        st.caption("⚠️ Exportação para uso interno autorizado. Dashboard NÃO OPERACIONAL.")
        _download("⬇️ CSV — Resumo por UBS", resumo, "resumo_por_ubs.csv", "dl_resumo")

    resumo_mun = (df_users.groupby("ubs_city")
                  .agg(Participantes=("user_id", "nunique"), UBSs=("ubs_name", "nunique"),
                       PHQ9=("phq_score", "mean"), GAD7=("gad_score", "mean"))
                  .reset_index().rename(columns={"ubs_city": "Município"}))
    resumo_mun["PHQ-9 Média"] = resumo_mun["PHQ9"].round(1)
    resumo_mun["GAD-7 Média"] = resumo_mun["GAD7"].round(1)
    resumo_mun = resumo_mun[["Município", "Participantes", "UBSs", "PHQ-9 Média", "GAD-7 Média"]].sort_values("Participantes", ascending=False)
    with st.expander("Resumo por Município", expanded=False):
        st.dataframe(resumo_mun, width="stretch", hide_index=True)
        st.caption("⚠️ Exportação para uso interno autorizado. Dashboard NÃO OPERACIONAL.")
        _download("⬇️ CSV — Resumo por Município", resumo_mun, "resumo_municipios.csv", "dl_mun")


def _ubs_tab_perfil(df_users: pd.DataFrame, dff: pd.DataFrame) -> None:
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Taxa de Conclusão por UBS")
        comp_ubs = (dff.groupby("ubs_name")["isCompleted"]
                    .apply(lambda x: x.mean() * 100 if x.count() > 0 else 0.0)
                    .reset_index(name="Taxa (%)").rename(columns={"ubs_name": "UBS"}))
        fig3 = px.bar(comp_ubs.sort_values("Taxa (%)"), x="Taxa (%)", y="UBS", orientation="h",
                      color="Taxa (%)", color_continuous_scale="Greens")
        fig3.update_layout(showlegend=False, coloraxis_showscale=False, height=380)
        st.plotly_chart(fig3, width="stretch")
        st.caption("⚠️ Exportação para uso interno autorizado. Dashboard NÃO OPERACIONAL.")
        _download("⬇️ CSV — Taxa de Conclusão por UBS", comp_ubs, "taxa_conclusao_por_ubs.csv", "dl_comp_ubs")

    with col4:
        st.subheader("Distribuição de Gênero")
        gender_counts = df_users["gender"].apply(normalize_gender).value_counts().reset_index()
        gender_counts.columns = ["Gênero", "Contagem"]
        fig4 = px.pie(gender_counts, names="Gênero", values="Contagem", hole=0.4,
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig4.update_layout(height=380)
        st.plotly_chart(fig4, width="stretch")
        st.caption("⚠️ Exportação para uso interno autorizado. Dashboard NÃO OPERACIONAL.")
        _download("⬇️ CSV — Distribuição de Gênero", gender_counts, "distribuicao_genero.csv", "dl_gender")

    st.divider()
    st.subheader("Distribuição por Faixa Etária")
    if "age" not in df_users.columns:
        st.info("Faixa etária indisponível nesta versão Beta (PII: data de nascimento não é consumida).")
        _download_disabled("⬇️ CSV — Distribuição por Faixa Etária (indisponível)", "distribuicao_faixa_etaria.csv", "dl_ages_disabled")
        st.caption("Mantém conformidade: não consumir `birthDate`/PII em consultas amplas.")
        _ubs_exportacoes_pendentes()
        return
    age_order = ["< 18", "18–29", "30–39", "40–49", "50–59", "60–69", "70–79", "80+", "Não informado"]
    age_data = (df_users["age"].apply(age_group).value_counts()
                .reindex(age_order, fill_value=0).reset_index())
    age_data.columns = ["Faixa Etária", "Participantes"]
    fig5 = px.bar(age_data, x="Faixa Etária", y="Participantes", color="Participantes",
                  color_continuous_scale="Purples")
    fig5.update_layout(showlegend=False, coloraxis_showscale=False, height=360)
    st.plotly_chart(fig5, width="stretch")
    st.caption("⚠️ Exportação para uso interno autorizado. Dashboard NÃO OPERACIONAL.")
    _download("⬇️ CSV — Distribuição por Faixa Etária", age_data, "distribuicao_faixa_etaria.csv", "dl_ages")
    st.caption("Calculado apenas sobre participantes aderentes (df_main_users).")
    _ubs_exportacoes_pendentes()


def _ubs_exportacoes_pendentes() -> None:
    with st.expander("📤 Exportações pendentes de fonte canônica (E.7-C.3)", expanded=False):
        st.info("Exportação preservada. Conteúdo pendente de fonte canônica validada.")
        st.caption("Dashboard NÃO OPERACIONAL.")
        st.caption("Fontes ausentes: `journeys_raw_latest`, `patient_feedback_raw_latest`.")
        c1, c2, c3 = st.columns(3)
        c1.download_button("⬇️ Jornadas por Tipo (indisponível)",        data=b"", file_name="jornadas_por_tipo.csv",            mime="text/csv", key="dl_jtype",            disabled=True)
        c2.download_button("⬇️ Jornadas por UBS (indisponível)",         data=b"", file_name="jornadas_por_ubs.csv",             mime="text/csv", key="dl_jubs",             disabled=True)
        c3.download_button("⬇️ Feedback por Tipo (indisponível)",        data=b"", file_name="feedback_por_tipo.csv",            mime="text/csv", key="dl_ftype",            disabled=True)
        c4, c5, c6 = st.columns(3)
        c4.download_button("⬇️ Feedback por Fonte (indisponível)",       data=b"", file_name="feedback_por_fonte.csv",           mime="text/csv", key="dl_fsource",          disabled=True)
        c5.download_button("⬇️ Feedback por Participante (indisponível)",data=b"", file_name="feedback_participante.csv",        mime="text/csv", key="dl_pfb_placeholder",  disabled=True)
        c6.download_button("⬇️ Sessões por Paciente completo (indisponível)", data=b"", file_name="sessoes_por_paciente_completo.csv", mime="text/csv", key="dl_sessoes_completo", disabled=True)

    with st.expander("🔒 Exportações pendentes de deliberação (E.7-C.4)", expanded=False):
        st.warning("Exportação condicionada à decisão do professor sobre dados sensíveis.")
        st.caption("Campos sensíveis: `user_id` por linha, `patientId`, `patientWhatsAppId`, PHQ crítico, IGI atual.")
        st.caption("Nenhum código escrito até deliberação formal em `Docs/fase-e7c-incorporacao-csv-dashboard.md`.")
        d1, d2, d3 = st.columns(3)
        d1.download_button("⬇️ Jornadas Detalhes (deliberação pendente)",      data=b"", file_name="jornadas_detalhes.csv",          mime="text/csv", key="dl_jdetails",  disabled=True)
        d2.download_button("⬇️ Feedbacks Recentes (deliberação pendente)",     data=b"", file_name="feedbacks_recentes.csv",          mime="text/csv", key="dl_freq",      disabled=True)
        d3.download_button("⬇️ Formulário Web por Paciente (deliberação pendente)", data=b"", file_name="formulario_web_por_paciente.csv", mime="text/csv", key="dl_forms_web", disabled=True)


def render_estatisticas_ubs(df_all, df_main, df_nao, df_users) -> None:
    st.title("Estatísticas por UBS")
    _status_caption("Tela central (UBS)")

    critical, warns = _validate_runtime(df_all, df_main, df_nao, df_users)
    for msg in warns:
        st.warning(msg)
    if critical:
        st.error("Checagens de integridade falharam:")
        for msg in critical:
            st.write(f"- {msg}")
        st.stop()

    st.divider()
    with st.container():
        st.subheader("Usuários Ativos")
        dff, dfu = _ubs_filtros(df_main, df_users)

    if (not dfu.empty) and (not df_users.empty):
        if not set(dfu["user_id"]).issubset(set(df_users["user_id"])):
            st.error("Violação de denominador: df_users filtrado não é subconjunto de df_main_users.")
            st.stop()

    st.divider()
    st.subheader("Resumo executivo")
    _ubs_metricas(dfu, dff)
    st.divider()

    tab_a, tab_b = st.tabs(["📈 Indicadores por UBS", "👥 Perfil e completude"])
    with tab_a:
        _ubs_tab_indicadores(dfu, dff)
    with tab_b:
        _ubs_tab_perfil(dfu, dff)


# =============================================================================
# PÁGINA: FORMULÁRIO WEB
# =============================================================================

def _fw_filtros(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Filtros — Formulário Web**")
    generos = ["Todos"] + sorted(df["genero"].dropna().unique().tolist())
    sel_g = st.sidebar.selectbox("Gênero", generos, key="fw_genero")
    sel_w = st.sidebar.selectbox("Status WhatsApp", ["Todos", "Habilitado", "Desabilitado"], key="fw_whatsapp")
    sel_f = st.sidebar.selectbox("Completou Form App", ["Todos", "Sim", "Não"], key="fw_form")
    mask = pd.Series(True, index=df.index)
    if sel_g != "Todos": mask &= df["genero"] == sel_g
    if sel_w != "Todos": mask &= df["status_whatsapp"] == sel_w
    if sel_f != "Todos": mask &= df["completou_form_app"] == sel_f
    return df[mask].copy()


def _fw_metricas(df: pd.DataFrame) -> None:
    total = len(df)
    w_hab = (df["status_whatsapp"] == "Habilitado").sum()
    f_ok  = (df["completou_form_app"] == "Sim").sum()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de pacientes", total)
    c2.metric("WhatsApp habilitado",  w_hab, f"{w_hab/total*100:.0f}%" if total else "—")
    c3.metric("Completaram Form App", f_ok,  f"{f_ok/total*100:.0f}%"  if total else "—")
    c4.metric("Jornadas (média/paciente)", f"{df['jornadas'].mean():.1f}" if total else "—")


def _fw_tabela(df: pd.DataFrame) -> None:
    dfv = df.copy()
    dfv["patient_id_masked"] = dfv["patient_id"].astype(str).str.slice(0, 6) + "…"
    display = df.rename(columns={
        "data_cadastro": "Data", "patient_id": "ID do Paciente", "genero": "Gênero",
        "status_whatsapp": "Status WhatsApp", "completou_form_app": "Completou Form App",
        "jornadas": "Jornadas",
    })
    display = dfv.rename(columns={
        "data_cadastro": "Data",
        "patient_id_masked": "ID do Paciente (mascarado)",
        "genero": "Gênero",
        "status_whatsapp": "Status WhatsApp",
        "completou_form_app": "Completou Form App",
        "jornadas": "Jornadas",
    })[["Data", "ID do Paciente (mascarado)", "Gênero", "Status WhatsApp", "Completou Form App", "Jornadas"]]
    st.dataframe(display, use_container_width=True, hide_index=False)
    st.caption(f"{len(display)} paciente(s) exibido(s)")

def _fw_export_resumo(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby(["genero", "status_whatsapp", "completou_form_app"])
            .agg(Pacientes=("patient_id", "nunique"),
                 Jornadas_media=("jornadas", "mean"))
            .reset_index()
            .rename(columns={
                "genero": "Genero",
                "status_whatsapp": "Status_WhatsApp",
                "completou_form_app": "Completou_Form_App",
            }))


def render_formulario_web() -> None:
    st.title("📋 Formulário Web — Pacientes com Jornadas Habilitadas")
    with st.spinner("Carregando dados do BigQuery..."):
        df_raw = load_formulario_web()
    if df_raw.empty:
        st.warning("Nenhum dado disponível. Verifique a conexão com o BigQuery.")
        return
    df = _fw_filtros(df_raw)
    _fw_metricas(df)
    st.markdown("---")
    _fw_tabela(df)
    st.markdown("---")
    st.caption("Exportação na Beta: apenas resumo agregado (sem IDs por paciente).")
    resumo = _fw_export_resumo(df)
    _download("⬇️ Exportar CSV (agregado)", resumo, "formulario_web_resumo.csv", "fw_download_agg")


# =============================================================================
# PÁGINA: GOVERNANÇA — NÃO ADERIU
# =============================================================================

def _gov_metricas(df_nao: pd.DataFrame, df_aderiu_users: pd.DataFrame) -> None:
    total_na = df_nao["user_id"].nunique()
    total_a  = df_aderiu_users["user_id"].nunique()
    total    = total_a + total_na
    pct      = total_na / total * 100 if total > 0 else 0
    com_score = df_nao[df_nao["phq_score"].notna() | df_nao["gad_score"].notna()]["user_id"].nunique()
    unk_uhs   = df_nao[df_nao["health_unit_key"] == "UNK_UHS"]["user_id"].nunique()
    no_match  = df_nao[df_nao["health_unit_key"] == "NO_MATCH"]["user_id"].nunique()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total — Não Aderiu", total_na)
    c2.metric("% do Total Interno", f"{pct:.1f}%")
    c3.metric("Sem Score PHQ/GAD",  total_na - com_score)
    c4, c5, c6 = st.columns(3)
    c4.metric("Com algum Score PHQ/GAD",   com_score)
    c5.metric("health_unit_key = UNK_UHS", unk_uhs)
    c6.metric("health_unit_key = NO_MATCH", no_match)


def _gov_temporal(df: pd.DataFrame) -> None:
    if "created_at" not in df.columns:
        return
    st.subheader("Distribuição Temporal — Entrada de Não Aderentes")
    df_t = df.copy()
    df_t["created_at"] = pd.to_datetime(df_t["created_at"], errors="coerce")
    df_t["mes"] = df_t["created_at"].dt.strftime("%Y-%m")
    agg = df_t.groupby("mes")["user_id"].nunique().reset_index()
    agg.columns = ["Mês", "Contagem"]
    fig = px.bar(agg.sort_values("Mês"), x="Mês", y="Contagem", color="Contagem",
                 color_continuous_scale="Blues", title="Entrada de Usuários — Não Aderiu")
    fig.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig, width="stretch")
    mn, mx = df_t["created_at"].min(), df_t["created_at"].max()
    st.info(f"**Intervalo:** {mn.strftime('%d/%m/%Y %H:%M') if pd.notna(mn) else 'N/D'} "
            f"até {mx.strftime('%d/%m/%Y %H:%M') if pd.notna(mx) else 'N/D'}")


def _gov_territorial(df: pd.DataFrame) -> None:
    if "ubs_status" not in df.columns:
        return
    st.subheader("Status Territorial — Não Aderentes")
    counts = df["ubs_status"].value_counts().reset_index()
    counts.columns = ["Status", "Contagem"]
    fig = px.pie(counts, names="Status", values="Contagem", hole=0.4,
                 title="Distribuição — Status Territorial")
    fig.update_layout(height=300)
    st.plotly_chart(fig, width="stretch")


def render_governanca_nao_aderiu(df_nao: pd.DataFrame, df_users: pd.DataFrame) -> None:
    st.title("Governança — Não Aderiu")
    _status_caption("Governança (Não Aderiu)")
    st.divider()
    with st.expander("🔍 Governança — Qualidade de Dados (Não Aderiu)", expanded=True):
        st.caption("Esta página usa o domínio Não Aderiu e não compõe o denominador analítico principal.")
        st.markdown("""
**Nota de Governança:**

Usuários classificados como "Não Aderiu" não aderiram plenamente ao protocolo clínico de
inclusão/entrada do CONEMO. São monitorados apenas para governança e qualidade dos dados.
**Não compõem os indicadores principais do dashboard.**
        """)
        st.markdown("---")
        if df_nao.empty:
            st.info("Nenhum usuário registrado no grupo 'Não Aderiu'.")
            return
        _gov_metricas(df_nao, df_users)
        st.markdown("---")
        _gov_temporal(df_nao)
        st.markdown("---")
        _gov_territorial(df_nao)


# =============================================================================
# PÁGINA: CONSULTA AUXILIAR
# =============================================================================

def _aux_perfil(row: pd.Series) -> None:
    st.subheader("Perfil")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("UBS",    row.get("ubs_name", "N/D"))
    p2.metric("Cidade", row.get("ubs_city", "N/D"))
    p3.metric("Gênero", normalize_gender(row.get("gender", "")))
    p4.metric("Participante", row.get("user_id", "N/D"))


def _aux_scores(row: pd.Series) -> None:
    st.subheader("Scores de Saúde Mental (Representação Atual)")
    phq, gad = row.get("phq_score"), row.get("gad_score")
    sc1, sc2 = st.columns(2)
    with sc1:
        v = float(phq) if phq is not None else 0
        fig = go.Figure(go.Indicator(mode="gauge+number", value=v,
            title={"text": f"PHQ-9 — {phq_severity(phq)}"},
            gauge={"axis": {"range": [0, 27]}, "bar": {"color": "#EF553B"},
                   "steps": [{"range": [0,  4], "color": "#d4edda"},
                              {"range": [4,  9], "color": "#fff3cd"},
                              {"range": [9, 14], "color": "#ffd8b1"},
                              {"range": [14,19], "color": "#f8d7da"},
                              {"range": [19,27], "color": "#c0392b"}]}))
        fig.update_layout(height=280)
        st.plotly_chart(fig, width="stretch")
    with sc2:
        v = float(gad) if gad is not None else 0
        fig = go.Figure(go.Indicator(mode="gauge+number", value=v,
            title={"text": f"GAD-7 — {gad_severity(gad)}"},
            gauge={"axis": {"range": [0, 21]}, "bar": {"color": "#636EFA"},
                   "steps": [{"range": [0,  4], "color": "#d4edda"},
                              {"range": [4,  9], "color": "#fff3cd"},
                              {"range": [9, 14], "color": "#f8d7da"},
                              {"range": [14,21], "color": "#c0392b"}]}))
        fig.update_layout(height=280)
        st.plotly_chart(fig, width="stretch")


def _aux_historico(participant_id: str) -> None:
    st.subheader("📜 Histórico Longitudinal PHQ/GAD")
    df = load_history(participant_id)
    if not df.empty:
        st.dataframe(
            df[["instrument", "score", "data_avaliacao", "status_score", "contexto"]].rename(
                columns={"instrument": "Instrumento", "score": "Score",
                         "data_avaliacao": "Data da Avaliação",
                         "status_score": "Status", "contexto": "Origem/Contexto"}),
            width="stretch", hide_index=True)
    else:
        st.info("Nenhum histórico adicional encontrado para este participante.")


def _aux_sessoes(df_user: pd.DataFrame, df_main: pd.DataFrame, selected_id: str) -> None:
    st.subheader("Progresso das Sessões")
    sessions = (df_user.drop_duplicates(subset="sessionNumber")
                .sort_values("sessionNumber")[["sessionNumber", "isCompleted", "completedDate"]].copy())
    total_s, done_s = len(sessions), int(sessions["isCompleted"].sum())
    s1, s2, s3 = st.columns(3)
    s1.metric("Total de sessões", total_s)
    s2.metric("Concluídas", done_s)
    s3.metric("Taxa de conclusão", f"{done_s/total_s*100:.0f}%" if total_s > 0 else "N/D")

    sessions["Status"] = sessions["isCompleted"].map(
        {True: "Concluída", False: "Não concluída", None: "N/D"}).fillna("N/D")
    sessions = sessions.dropna(subset=["sessionNumber"])
    sessions["Sessão"] = "Sessão " + sessions["sessionNumber"].astype(int).astype(str)
    fig = px.bar(sessions, x="Sessão", y=[1]*len(sessions), color="Status", height=220,
                 color_discrete_map={"Concluída": "#2ecc71", "Não concluída": "#e74c3c", "N/D": "#bdc3c7"})
    fig.update_yaxes(visible=False)
    st.plotly_chart(fig, width="stretch")

    with st.expander("Ver tabela de sessões e exportar"):
        tbl = sessions[["Sessão", "Status", "completedDate"]].rename(columns={"completedDate": "Data de conclusão"})
        st.dataframe(tbl, width="stretch", hide_index=True)
        st.warning("Exportação individual bloqueada na Beta (risco de dados clínicos individualizados).")
        _download_disabled("⬇️ CSV — Sessões deste participante (bloqueado)", f"sessoes_{selected_id}.csv", "dl_sessions")

    with st.expander("📋 Resumo de sessões — todos os participantes aderentes (E.7-C.2)", expanded=False):
        st.caption("Resumo agregado por UBS (sem identificação individual).")
        sp = (df_main.groupby(["ubs_city", "ubs_name"])
              .agg(Participantes=("user_id", "nunique"),
                   Total_Sessoes=("sessionNumber", "nunique"),
                   Sessoes_Concluidas=("isCompleted", lambda x: int(x.sum())))
              .reset_index().rename(columns={"ubs_city": "Cidade", "ubs_name": "UBS"}))
        sp["Taxa_Conclusao_pct"] = (sp["Sessoes_Concluidas"] / sp["Total_Sessoes"] * 100).round(1)
        st.dataframe(sp, width="stretch", hide_index=True)
        st.caption("⚠️ Exportação agregada para uso interno autorizado. Dashboard NÃO OPERACIONAL.")
        _download("⬇️ CSV — Sessões por UBS (agregado)", sp, "sessoes_por_ubs.csv", "dl_sessoes_ubs")


def render_consulta_auxiliar(df_users: pd.DataFrame, df_events: pd.DataFrame, df_main: pd.DataFrame) -> None:
    st.title("Consulta auxiliar por participante")
    _status_caption("Consulta auxiliar")
    st.divider()
    with st.expander("👤 Consulta individual por participante (visão auxiliar)", expanded=True):
        st.subheader("Estatísticas por Participante")
        user_ids = sorted(df_users["user_id"].dropna().unique())
        selected_id = st.selectbox("Selecione o ID do participante", user_ids)
        df_user = df_events[df_events["user_id"] == selected_id]
        if df_user.empty:
            st.warning("Participante não encontrado.")
            return
        row = df_user.iloc[0]
        st.markdown("---")
        _aux_perfil(row)
        st.markdown("---")
        _aux_scores(row)
        st.markdown("---")
        _aux_historico(selected_id)
        st.markdown("---")
        _aux_sessoes(df_user, df_main, selected_id)


# =============================================================================
# SIDEBAR
# =============================================================================

def render_sidebar() -> str:
    st.sidebar.title("🏥 CONEMO")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📅 Dados atualizados em:**")
    st.sidebar.info(st.session_state.get("last_update", "Não disponível"))
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Atualizar dados"):
        st.cache_data.clear()
        st.rerun()
    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navegação", [
        "📊 Estatísticas por UBS",
        "📋 Formulário Web",
        "🔍 Governança — Não Aderiu",
        "👤 Consulta auxiliar",
    ])
    st.sidebar.markdown("---")
    st.sidebar.caption("Dashboard CONEMO — Versão MVP (Integrada BigQuery)")
    return page


# =============================================================================
# ENTRYPOINT
# =============================================================================

def main() -> None:
    df_all = load_data()
    df_main, df_nao, df_users = _build_domains(df_all)
    _guard_domains(df_main)

    page = render_sidebar()

    if page == "📊 Estatísticas por UBS":
        render_estatisticas_ubs(df_all, df_main, df_nao, df_users)
    elif page == "📋 Formulário Web":
        render_formulario_web()
    elif page == "🔍 Governança — Não Aderiu":
        render_governanca_nao_aderiu(df_nao, df_users)
    elif page == "👤 Consulta auxiliar":
        render_consulta_auxiliar(df_users, df_main, df_main)


main()
