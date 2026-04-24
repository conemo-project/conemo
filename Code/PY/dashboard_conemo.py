import os
import json
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from google.cloud import bigquery

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CONEMO Dashboard",
    page_icon="🏥",
    layout="wide",
)

PARQUET_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../Data/PARQUET/conemo_dados_consolidados_raw_04_03_2026.parquet",
)

# ---------------------------------------------------------------------------
# P0.1 — Timestamp da última atualização (BigQuery ou Cache local)
#
# Na Fase C.2, o BigQuery passa a ser a fonte canônica. O timestamp reflete:
# 1. Se carregado via BigQuery: o momento da consulta.
# 2. Se via Fallback Parquet: a data de modificação do arquivo local.
# ---------------------------------------------------------------------------
def get_update_timestamp() -> str:
    """Retorna o timestamp da última atualização dos dados exibidos."""
    if "last_update" in st.session_state:
        return st.session_state["last_update"]
    
    try:
        if os.path.exists(PARQUET_PATH):
            mtime = os.path.getmtime(PARQUET_PATH)
            return datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        pass
    return "Não disponível"


# ---------------------------------------------------------------------------
# Fase C.2 — Carregamento via BigQuery
# ---------------------------------------------------------------------------
def load_data_from_bigquery() -> pd.DataFrame:
    """Executa consulta controlada no BigQuery preservando o contrato do Dashboard."""
    client = bigquery.Client()
    
    query = """
    WITH raw_perfil AS (
      SELECT 
        document_id as source_user_id,
        JSON_EXTRACT_SCALAR(data, '$.name') as user_name,
        JSON_EXTRACT_SCALAR(data, '$.email') as email,
        JSON_EXTRACT_SCALAR(data, '$.birthDate._seconds') as birth_seconds
      FROM `conemo-412202.firestore_export.users_raw_latest`
    )
    SELECT 
      p.participant_master_id as user_id,
      s.session_number as sessionNumber,
      s.is_completed as isCompleted,
      CAST(s.event_timestamp AS STRING) as completedDate,
      u.ubs_name,
      u.ubs_city,
      p.gender,
      r.user_name,
      r.email,
      CAST(r.birth_seconds AS INT64) as birth_seconds,
      CAST(NULL AS FLOAT64) as phq_score, -- Degradado temporariamente por erro na view original
      CAST(NULL AS FLOAT64) as gad_score, -- Degradado temporariamente por erro na view original
      p.created_at,
      UNIX_SECONDS(p.created_at) as created_at_seconds,
      p.is_test_record
    FROM `conemo-412202.firestore_curated.cur_participant_current_v1` p
    LEFT JOIN `conemo-412202.firestore_curated.cur_session_current_v1` s ON p.participant_master_id = s.participant_master_id
    LEFT JOIN `conemo-412202.firestore_curated.cur_health_unit_v1` u ON p.health_unit_key = u.health_unit_key
    LEFT JOIN raw_perfil r ON p.source_user_id = r.source_user_id
    WHERE p.created_at >= TIMESTAMP('2026-01-25 00:00:00 UTC')
      AND p.is_test_record = false
    """
    
    df = client.query(query).to_dataframe()
    
    # Processamento de Idade (PII mantida conforme decisão do professor)
    def calculate_age(birth_seconds):
        if pd.isna(birth_seconds):
            return None
        try:
            birth = datetime.fromtimestamp(birth_seconds)
            today = datetime.now()
            return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        except Exception:
            return None

    df["age"] = df["birth_seconds"].apply(calculate_age)
    
    # Preenchimento de nulos para conformidade com o Dashboard
    df["ubs_name"] = df["ubs_name"].fillna("N/A")
    df["ubs_city"] = df["ubs_city"].fillna("N/A")
    df["user_name"] = df["user_name"].fillna("N/A")
    df["email"] = df["email"].fillna("N/D")
    df["gender"] = df["gender"].fillna("N/A")
    
    # Flags para manter contrato com código visual antigo
    df["is_test"] = False
    df["is_test_user"] = False
    df["is_invalid"] = False
    df["is_test_environment"] = False
    
    return df


# ---------------------------------------------------------------------------
# Carregamento e pré-processamento dos dados (load_data)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=900) # Cache de 15 minutos (Fase C.2)
def load_data() -> pd.DataFrame:
    """Carrega dados priorizando BigQuery com fallback técnico para Parquet."""
    try:
        # Tenta carregar do BigQuery (Fonte Canônica)
        df = load_data_from_bigquery()
        st.session_state["data_source"] = "BigQuery (Canônico)"
        st.session_state["last_update"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        st.session_state["bq_success"] = True
        return df
        
    except Exception as e:
        # Fallback técnico controlado para Parquet
        st.session_state["bq_success"] = False
        st.error(f"⚠️ Falha na fonte canônica (BigQuery). Erro: {str(e)}")
        st.info("Utilizando fallback temporário: Parquet local (Desatualizado)")
        
        if not os.path.exists(PARQUET_PATH):
            st.error("Falha crítica: nem BigQuery nem Parquet estão disponíveis.")
            return pd.DataFrame()

        df = pd.read_parquet(PARQUET_PATH)
        st.session_state["data_source"] = "Parquet (Fallback Técnico)"
        
        # Lógica legado de pré-processamento Parquet (extração de JSON)
        df["sessionNumber"] = pd.to_numeric(df["sessionNumber"], errors="coerce")
        df["isCompleted"] = df["isCompleted"].map({"true": True, "false": False, True: True, False: False})

        def parse_user_legacy(json_str):
            try:
                data = json.loads(json_str)
                org = data.get("organization", {})
                forms = data.get("forms", [])
                phq, gad = None, None
                if forms:
                    for s in forms[0].get("scores", []):
                        if s.get("type") == "PHQ": phq = s.get("score")
                        if s.get("type") == "GAD": gad = s.get("score")
                
                ca = data.get("createdAt")
                created_at_seconds = ca.get("_seconds") if isinstance(ca, dict) else None
                
                bd = data.get("birthDate")
                birth_seconds = bd.get("_seconds") if isinstance(bd, dict) else None
                
                return pd.Series({
                    "ubs_name": org.get("name", "N/A"),
                    "ubs_city": org.get("city", "N/A"),
                    "phq_score": phq,
                    "gad_score": gad,
                    "gender": data.get("gender", "N/A"),
                    "user_name": data.get("name", "N/A"),
                    "birth_seconds": birth_seconds,
                    "created_at_seconds": created_at_seconds,
                    "is_test": bool(data.get("isTest", False)),
                    "is_test_user": bool(data.get("isTestUser", False)),
                    "is_invalid": bool(data.get("invalid", False)),
                    "is_test_environment": bool(org.get("testEnvironment", False)),
                })
            except Exception:
                return pd.Series({"ubs_name": "N/A", "ubs_city": "N/A", "phq_score": None, "gad_score": None, 
                                 "gender": "N/A", "user_name": "N/A", "birth_seconds": None, "created_at_seconds": None,
                                 "is_test": False, "is_test_user": False, "is_invalid": False, "is_test_environment": False})

        extracted = df["json_data_user"].apply(parse_user_legacy)
        df = pd.concat([df, extracted], axis=1)
        
        def calculate_age(birth_seconds):
            if pd.isna(birth_seconds) or birth_seconds is None: return None
            try:
                birth = datetime.fromtimestamp(birth_seconds)
                today = datetime.now()
                return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            except Exception:
                return None
        
        df["age"] = df["birth_seconds"].apply(calculate_age)
        
        # Filtros Legado (Fase B)
        CUTOFF_SECONDS = 1769299200
        test_city_pattern = r"test|teste|fake|load|carga|break|quebra"
        has_test_or_invalid_flag = (
            df["is_test"].fillna(False) | df["is_test_user"].fillna(False) | 
            df["is_invalid"].fillna(False) | df["is_test_environment"].fillna(False) | 
            df["ubs_city"].fillna("").str.lower().str.contains(test_city_pattern, regex=True)
        )
        df = df[(df["created_at_seconds"] >= CUTOFF_SECONDS) & (~has_test_or_invalid_flag)]

    # Normalizações finais (comuns a ambas as fontes)
    df["ubs_name"] = df["ubs_name"].str.upper().str.strip()
    df["ubs_city"] = df["ubs_city"].str.strip().str.title()
    
    _CIDADES_INVALIDAS = {"Fake City", "N/A", ""}
    df = df[df["ubs_city"].notna() & (~df["ubs_city"].isin(_CIDADES_INVALIDAS))]

    return df


# Inicializa carregamento
df = load_data()

# ---------------------------------------------------------------------------
# Sidebar — navegação, timestamp e botão de atualização
# ---------------------------------------------------------------------------
st.sidebar.title("🏥 CONEMO")
st.sidebar.markdown("---")

# P0.1 — Timestamp da última atualização
st.sidebar.markdown("**📅 Dados atualizados em:**")
st.sidebar.info(get_update_timestamp())
st.sidebar.markdown(f"*Modo: {st.session_state.get('data_source', 'Inicializando...')}*")

st.sidebar.markdown("---")

# P0.3 — Botão de atualização
if st.sidebar.button("🔄 Atualizar dados"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")

# P0.2 — Navegação principal orientada a UBS/gestão
page = st.sidebar.radio(
    "Navegação",
    ["📊 Estatísticas por UBS"],
)

# ---------------------------------------------------------------------------
# P2 — Label discreto de versão MVP
# ---------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.caption("Dashboard CONEMO — Versão MVP (Integrada BigQuery)")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def phq_severity(score):
    if score is None: return "N/D"
    if score <= 4: return "Sem depressão"
    if score <= 9: return "Leve"
    if score <= 14: return "Moderada"
    if score <= 19: return "Moderadamente grave"
    return "Grave"


def gad_severity(score):
    if score is None: return "N/D"
    if score <= 4: return "Mínima"
    if score <= 9: return "Leve"
    if score <= 14: return "Moderada"
    return "Grave"


def severity_color(label):
    colors = {
        "Sem depressão": "green", "Mínima": "green", "Leve": "orange",
        "Moderada": "orange", "Moderadamente grave": "red", "Grave": "red", "N/D": "gray",
    }
    return colors.get(label, "gray")


# ---------------------------------------------------------------------------
# Página 1 — Estatísticas por UBS
# ---------------------------------------------------------------------------
if page == "📊 Estatísticas por UBS":
    st.title("Estatísticas por UBS")

    # --- Filtros ---
    col_f1, col_f2 = st.columns(2)
    all_cities = sorted(df["ubs_city"].dropna().unique())
    sel_cities = col_f1.multiselect("Cidade", all_cities, default=all_cities)

    df_city = df[df["ubs_city"].isin(sel_cities)] if sel_cities else df
    all_ubs = sorted(df_city["ubs_name"].dropna().unique())
    sel_ubs = col_f2.multiselect("UBS", all_ubs, default=all_ubs)

    dff = df_city[df_city["ubs_name"].isin(sel_ubs)] if sel_ubs else df_city

    # DataFrame de participantes únicos (um por user_id)
    df_users = dff.drop_duplicates(subset="user_id")

    # --- Métricas ---
    total_users = df_users["user_id"].nunique()
    mean_phq = df_users["phq_score"].mean()
    mean_gad = df_users["gad_score"].mean()
    sessions_total = len(dff)
    sessions_done = dff["isCompleted"].sum()
    completion_rate = (sessions_done / sessions_total * 100) if sessions_total > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Participantes", total_users)
    m2.metric("Média PHQ-9 (Depressão)", f"{mean_phq:.1f}" if pd.notna(mean_phq) else "N/D")
    m3.metric("Média GAD-7 (Ansiedade)", f"{mean_gad:.1f}" if pd.notna(mean_gad) else "N/D")
    m4.metric("Conclusão de Sessões", f"{completion_rate:.1f}%")

    st.markdown("---")

    # --- Gráficos: linha 1 ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Participantes por UBS")
        ubs_count = df_users["ubs_name"].value_counts().reset_index()
        ubs_count.columns = ["UBS", "Participantes"]
        fig = px.bar(ubs_count.sort_values("Participantes"), x="Participantes", y="UBS", orientation="h", color="Participantes", color_continuous_scale="Blues")
        fig.update_layout(showlegend=False, coloraxis_showscale=False, height=400)
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.subheader("Média PHQ-9 e GAD-7 por UBS")
        scores_ubs = df_users.groupby("ubs_name")[["phq_score", "gad_score"]].mean().reset_index().rename(columns={"ubs_name": "UBS", "phq_score": "PHQ-9", "gad_score": "GAD-7"})
        scores_melt = scores_ubs.melt(id_vars="UBS", var_name="Escala", value_name="Média")
        fig2 = px.bar(scores_melt, x="Média", y="UBS", color="Escala", orientation="h", barmode="group", color_discrete_map={"PHQ-9": "#EF553B", "GAD-7": "#636EFA"})
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, width='stretch')

    # --- Gráficos: linha 2 ---
    col3, col4, col5 = st.columns(3)

    with col3:
        st.subheader("Taxa de Conclusão por UBS")
        comp_ubs = dff.groupby("ubs_name")["isCompleted"].apply(lambda x: x.mean() * 100 if x.count() > 0 else 0.0).reset_index(name="Taxa (%)")
        comp_ubs = comp_ubs.rename(columns={"ubs_name": "UBS"})
        fig3 = px.bar(comp_ubs.sort_values("Taxa (%)"), x="Taxa (%)", y="UBS", orientation="h", color="Taxa (%)", color_continuous_scale="Greens")
        fig3.update_layout(showlegend=False, coloraxis_showscale=False, height=350)
        st.plotly_chart(fig3, width='stretch')

    with col4:
        st.subheader("Distribuição de Gênero")
        gender_map = {"F": "Feminino", "M": "Masculino"}
        gender_counts = df_users["gender"].map(gender_map).fillna("Não informado").value_counts().reset_index()
        gender_counts.columns = ["Gênero", "Contagem"]
        fig4 = px.pie(gender_counts, names="Gênero", values="Contagem", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        fig4.update_layout(height=350)
        st.plotly_chart(fig4, width='stretch')

    with col5:
        st.subheader("Distribuição de Idades")
        ages = df_users["age"].dropna()
        fig5 = px.histogram(ages, nbins=20, labels={"value": "Idade", "count": "Frequência"}, color_discrete_sequence=["#AB63FA"])
        fig5.update_layout(showlegend=False, height=350, xaxis_title="Idade", yaxis_title="Frequência")
        st.plotly_chart(fig5, width='stretch')

    # --- Tabela resumo ---
    st.markdown("---")
    st.subheader("Resumo por UBS")

    comp_lookup = comp_ubs.set_index("UBS")["Taxa (%)"].to_dict()
    resumo = df_users.groupby("ubs_name").agg(Participantes=("user_id", "nunique"), PHQ9_media=("phq_score", "mean"), GAD7_media=("gad_score", "mean")).reset_index().rename(columns={"ubs_name": "UBS"})
    resumo["Conclusão (%)"] = resumo["UBS"].map(comp_lookup).round(1)
    resumo["PHQ-9 Média"] = resumo["PHQ9_media"].round(1)
    resumo["GAD-7 Média"] = resumo["GAD7_media"].round(1)
    resumo = resumo[["UBS", "Participantes", "PHQ-9 Média", "GAD-7 Média", "Conclusão (%)"]].sort_values("Participantes", ascending=False)
    st.dataframe(resumo, width='stretch', hide_index=True)


# ---------------------------------------------------------------------------
# Visão individual por participante
# ---------------------------------------------------------------------------
st.markdown("---")
with st.expander("👤 Consulta individual por participante (visão auxiliar)"):
    st.subheader("Estatísticas por Participante")
    user_ids = sorted(df["user_id"].dropna().unique())
    selected_id = st.selectbox("Selecione o ID do participante", user_ids)

    df_user = df[df["user_id"] == selected_id]
    if df_user.empty:
        st.warning("Participante não encontrado.")
    else:
        row = df_user.iloc[0]
        st.markdown("---")
        st.subheader("Perfil")

        gender_label = {"F": "Feminino", "M": "Masculino"}.get(str(row.get("gender", "")), "Não informado")
        age_str = f"{int(row['age'])} anos" if pd.notna(row.get("age")) else "N/D"
        email_raw = str(row.get("email", "N/D"))
        if "@" in email_raw:
            local, domain = email_raw.split("@", 1)
            email_masked = local[:3] + "***@" + domain
        else:
            email_masked = email_raw

        p1, p2, p3, p4, p5 = st.columns(5)
        p1.metric("UBS", row.get("ubs_name", "N/D"))
        p2.metric("Cidade", row.get("ubs_city", "N/D"))
        p3.metric("Gênero", gender_label)
        p4.metric("Idade", age_str)
        p5.metric("E-mail", email_masked)

        # Scores
        st.markdown("---")
        st.subheader("Scores de Saúde Mental (Baseline)")
        phq = row.get("phq_score")
        gad = row.get("gad_score")
        phq_label, gad_label = phq_severity(phq), gad_severity(gad)
        sc1, sc2 = st.columns(2)

        with sc1:
            phq_val = float(phq) if phq is not None else 0
            fig_phq = go.Figure(go.Indicator(mode="gauge+number", value=phq_val, title={"text": f"PHQ-9 — {phq_label}"}, gauge={"axis": {"range": [0, 27]}, "bar": {"color": "#EF553B"}, "steps": [{"range": [0, 4], "color": "#d4edda"}, {"range": [4, 9], "color": "#fff3cd"}, {"range": [9, 14], "color": "#ffd8b1"}, {"range": [14, 19], "color": "#f8d7da"}, {"range": [19, 27], "color": "#c0392b"}]}))
            fig_phq.update_layout(height=280)
            st.plotly_chart(fig_phq, width='stretch')

        with sc2:
            gad_val = float(gad) if gad is not None else 0
            fig_gad = go.Figure(go.Indicator(mode="gauge+number", value=gad_val, title={"text": f"GAD-7 — {gad_label}"}, gauge={"axis": {"range": [0, 21]}, "bar": {"color": "#636EFA"}, "steps": [{"range": [0, 4], "color": "#d4edda"}, {"range": [4, 9], "color": "#fff3cd"}, {"range": [9, 14], "color": "#f8d7da"}, {"range": [14, 21], "color": "#c0392b"}]}))
            fig_gad.update_layout(height=280)
            st.plotly_chart(fig_gad, width='stretch')

        # Progresso
        st.markdown("---")
        st.subheader("Progresso das Sessões")
        sessions = df_user.drop_duplicates(subset="sessionNumber").sort_values("sessionNumber")[["sessionNumber", "isCompleted", "completedDate"]].copy()
        total_sess, done_sess = len(sessions), int(sessions["isCompleted"].sum())
        s1, s2, s3 = st.columns(3)
        s1.metric("Total de sessões", total_sess)
        s2.metric("Concluídas", done_sess)
        s3.metric("Taxa de conclusão", f"{done_sess/total_sess*100:.0f}%" if total_sess > 0 else "N/D")

        sessions["Status"] = sessions["isCompleted"].map({True: "Concluída", False: "Não concluída", None: "N/D"}).fillna("N/D")
        sessions = sessions.dropna(subset=["sessionNumber"])
        sessions["Sessão"] = "Sessão " + sessions["sessionNumber"].astype(int).astype(str)
        fig_sess = px.bar(sessions, x="Sessão", y=[1] * len(sessions), color="Status", color_discrete_map={"Concluída": "#2ecc71", "Não concluída": "#e74c3c", "N/D": "#bdc3c7"}, height=220)
        fig_sess.update_yaxes(visible=False)
        st.plotly_chart(fig_sess, width='stretch')
