import os
import json
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

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

# Data de corte operacional canônica do dashboard (inclusiva)
DASHBOARD_CUTOFF_TS = "2026-01-28 00:00:00 UTC"
DASHBOARD_CUTOFF_SECONDS = int(pd.Timestamp(DASHBOARD_CUTOFF_TS).timestamp())

# ---------------------------------------------------------------------------
# Helper: cria cliente BigQuery com credenciais de st.secrets.
#
# Streamlit Cloud: usa obrigatoriamente [gcp_service_account] dos Secrets.
#   Se ausente ou inválido, levanta RuntimeError explícito — NÃO tenta o
#   Compute Engine Metadata Server (metadata.google.internal), que não existe
#   no ambiente Streamlit Community Cloud.
#
# Desenvolvimento local: fallback ADC somente quando GOOGLE_APPLICATION_CREDENTIALS
#   apontar para um arquivo existente.
#
# Ref: Fase Beta-2 v2 — corrigir queda para metadata server quando secret
#   ausente/inválido (erro: "Failed to retrieve http://metadata.google.internal").
# ---------------------------------------------------------------------------
def _get_bq_client() -> bigquery.Client:
    """Retorna cliente BigQuery autenticado via st.secrets ou ADC local.

    Streamlit Cloud: exige [gcp_service_account] nos Secrets. Falha explícita
    e controlada se ausente — nunca tenta o metadata server.
    Local: usa GOOGLE_APPLICATION_CREDENTIALS se definido e existir.
    """
    try:
        if "gcp_service_account" in st.secrets:
            info = dict(st.secrets["gcp_service_account"])
            creds = service_account.Credentials.from_service_account_info(
                info,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            return bigquery.Client(
                credentials=creds,
                project=creds.project_id,
            )
    except Exception as exc:
        raise RuntimeError(
            "Secret [gcp_service_account] ausente, incompleto ou inválido no Streamlit Cloud. "
            "Configure os Secrets em Manage app → Settings → Secrets."
        ) from exc

    # Fallback local: somente quando GOOGLE_APPLICATION_CREDENTIALS existir explicitamente.
    # Garante que o metadata server NUNCA seja tentado no Streamlit Cloud.
    local_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if local_creds and os.path.exists(local_creds):
        return bigquery.Client(project="conemo-412202")

    raise RuntimeError(
        "Credenciais BigQuery indisponíveis. "
        "No Streamlit Cloud: configure [gcp_service_account] nos Secrets. "
        "Localmente: defina GOOGLE_APPLICATION_CREDENTIALS."
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
# Fase C.2 / D.3 — Carregamento via BigQuery
# ---------------------------------------------------------------------------
def load_data_from_bigquery() -> pd.DataFrame:
    """Executa consulta controlada no BigQuery preservando o contrato do Dashboard."""
    client = _get_bq_client()
    
    # Query reintegrando scores PHQ/GAD via cur_score_current_v1 (Fase D.3)
    # Correção D.3 Corretiva: Ajuste de denominador para incluir UNK_UHS (válidos) 
    # e excluir rigorosamente testes do RAW.
    query = f"""
    WITH raw_perfil AS (
      -- Extração de campos demográficos e identificadores da camada RAW
      -- Adição de flags de teste do RAW para exclusão segura (D.3 Corretiva)
      SELECT 
        document_id as source_user_id,
        JSON_EXTRACT_SCALAR(data, '$.name') as user_name,
        JSON_EXTRACT_SCALAR(data, '$.email') as email,
        JSON_EXTRACT_SCALAR(data, '$.birthDate._seconds') as birth_seconds,
        JSON_EXTRACT_SCALAR(data, '$.isTest') as is_test_raw,
        JSON_EXTRACT_SCALAR(data, '$.isTestUser') as is_test_user_raw,
        JSON_EXTRACT_SCALAR(data, '$.invalid') as is_invalid_raw
      FROM `conemo-412202.firestore_export.users_raw_latest`
    ),
    score_ranked AS (
      -- Etapa 4: Regra determinística para múltiplos scores
      -- Prioridade: score_timestamp, desempate por source_document_id
      SELECT 
        participant_id,
        instrument,
        score_total,
        score_timestamp,
        ROW_NUMBER() OVER (
          PARTITION BY participant_id, instrument 
          ORDER BY score_timestamp DESC, source_document_id DESC
        ) as rn
      FROM `conemo-412202.firestore_curated.cur_score_current_v1`
    ),
    score_latest AS (
      -- Etapa 5: Seleção do score atual por instrumento
      SELECT 
        participant_id,
        MAX(CASE WHEN instrument IN ('PHQ', 'PHQ_JOURNEY') THEN score_total END) as phq_score,
        MAX(CASE WHEN instrument IN ('GAD', 'GAD_JOURNEY') THEN score_total END) as gad_score
      FROM score_ranked
      WHERE rn = 1
      GROUP BY participant_id
    )
    SELECT 
      p.participant_master_id as user_id,
            p.health_unit_key,
      s.session_number as sessionNumber,
      s.is_completed as isCompleted,
      CAST(s.event_timestamp AS STRING) as completedDate,
      u.ubs_name,
      u.ubs_city,
      p.gender,
      r.user_name,
      r.email,
      CAST(r.birth_seconds AS INT64) as birth_seconds,
      sl.phq_score, -- Reintegrado via cur_score_current_v1 saneada (Fase D.3)
      sl.gad_score, -- Reintegrado via cur_score_current_v1 saneada (Fase D.3)
      p.created_at,
      UNIX_SECONDS(p.created_at) as created_at_seconds,
      p.is_test_record
    FROM `conemo-412202.firestore_curated.cur_participant_current_v1` p
    LEFT JOIN `conemo-412202.firestore_curated.cur_session_current_v1` s ON p.participant_master_id = s.participant_master_id
    LEFT JOIN `conemo-412202.firestore_curated.cur_health_unit_v1` u ON p.health_unit_key = u.health_unit_key
    LEFT JOIN raw_perfil r ON p.source_user_id = r.source_user_id
    LEFT JOIN score_latest sl ON p.participant_master_id = sl.participant_id
        WHERE p.created_at >= TIMESTAMP('{DASHBOARD_CUTOFF_TS}')
      -- Regra Segura D.3 Corretiva: Inclui NULLs (válidos), exclui testes explícitos do Curated e do RAW
      AND (p.is_test_record IS NOT TRUE)
      AND (r.is_test_raw IS NULL OR r.is_test_raw = 'false')
      AND (r.is_test_user_raw IS NULL OR r.is_test_user_raw = 'false')
      AND (r.is_invalid_raw IS NULL OR r.is_invalid_raw = 'false')
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
    
    # Preenchimento de nulos (D.3 Corretiva: Rotula UNK_UHS como "Não respondeu")
    df["ubs_name"] = df["ubs_name"].fillna("Não respondeu")
    df["ubs_city"] = df["ubs_city"].fillna("Não respondeu")
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
# Fase D.4 — Carregamento de Histórico Longitudinal
# ---------------------------------------------------------------------------
@st.cache_data(ttl=900)
def load_history_from_bigquery(participant_id: str) -> pd.DataFrame:
    """Carrega o histórico completo de PHQ/GAD para um participante específico."""
    client = _get_bq_client()
    query = f"""
    SELECT 
      instrument,
      score_total as score,
      score_timestamp as data_avaliacao,
      score_source as fonte,
      source_document_name as path_firestore,
      ROW_NUMBER() OVER (
        PARTITION BY instrument 
        ORDER BY score_timestamp DESC, source_document_id DESC
      ) as rn
    FROM `conemo-412202.firestore_curated.cur_score_current_v1`
    WHERE participant_id = '{participant_id}'
      AND instrument IN ('PHQ', 'PHQ_JOURNEY', 'GAD', 'GAD_JOURNEY')
    ORDER BY score_timestamp DESC
    """
    try:
        df_hist = client.query(query).to_dataframe()
        # Classifica score atual vs histórico
        df_hist["status_score"] = df_hist["rn"].apply(lambda x: "Atual" if x == 1 else "Histórico")
        
        # Tenta extrair sessão/jornada do path do Firestore quando disponível
        def extract_context(path):
            if not path or pd.isna(path): return "Vínculo não observável"
            if "journeys/" in path:
                # Extrai o ID da jornada ou parte do path para contexto
                parts = path.split("/")
                if "sessions" in path:
                    idx = parts.index("sessions")
                    return f"Sessão {parts[idx+1]}" if len(parts) > idx+1 else "Jornada"
                return "Jornada"
            return "Triagem/Baseline"
            
        df_hist["contexto"] = df_hist["path_firestore"].apply(extract_context)
        return df_hist
    except Exception:
        return pd.DataFrame()


# ---------------------------------------------------------------------------
# Classificação operacional de adesão ao protocolo CONEMO
#
# Função central: deve ser chamada em TODOS os caminhos de carregamento,
# imediatamente antes de criar df_all, df_main e df_nao_aderiu.
#
# Ref: Docs/nota-decisoria-nao-aderiu-dashboard.md
# ---------------------------------------------------------------------------
def add_conemo_protocol_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica classificação operacional de adesão ao protocolo CONEMO.

    Regra canônica dinâmica (sem hard-code de IDs ou contagens):
    - health_unit_key == 'UNK_UHS'  →  conemo_protocol_status = 'Não Aderiu'
    - Fallback de segurança (health_unit_key ausente/nulo): quando a chave
      territorial não estiver recuperável, usa ubs_name/ubs_city finais
      como mecanismo de segurança — se ambos forem 'NÃO RESPONDEU', classifica
      como 'Não Aderiu'. Esse fallback não é o critério principal.
    - Demais registros  →  conemo_protocol_status = 'Aderiu'

    Garantias:
    - nunca remove usuários;
    - nunca deixa usuário sem classificação;
    - retorna DataFrame válido mesmo se vazio (colunas obrigatórias criadas);
    - não altera BigQuery;
    - não expõe PII.
    """
    df = df.copy()

    # DataFrame vazio: garantir colunas obrigatórias para não quebrar downstream
    if df.empty:
        if "conemo_protocol_status" not in df.columns:
            df["conemo_protocol_status"] = pd.Series(dtype="object")
        if "ubs_status" not in df.columns:
            df["ubs_status"] = pd.Series(dtype="object")
        return df

    def _normalize_text(value) -> str:
        """Normaliza texto para comparação robusta de regras operacionais."""
        if pd.isna(value):
            return ""
        return str(value).strip().upper()

    def _is_nao_aderiu(row: pd.Series) -> bool:
        """
        Critério preferencial canônico: health_unit_key == 'UNK_UHS'.
        Fallback operacional temporário (somente quando health_unit_key não
        estiver recuperável): UBS/cidade final = 'NÃO RESPONDEU'.
        UBS/cidade textual continuam sendo dimensão territorial e não são
        critério principal para status de adesão.
        """
        health_unit_key = _normalize_text(row.get("health_unit_key", ""))
        if health_unit_key == "UNK_UHS":
            return True
        # Fallback de segurança: chave territorial ausente/nula
        if health_unit_key in {"", "NONE", "NULL", "NAN"}:
            ubs_name = _normalize_text(row.get("ubs_name", ""))
            ubs_city = _normalize_text(row.get("ubs_city", ""))
            return (ubs_name == "NÃO RESPONDEU") or (ubs_city == "NÃO RESPONDEU")
        return False

    mask_nao_aderiu = df.apply(_is_nao_aderiu, axis=1)
    df["conemo_protocol_status"] = mask_nao_aderiu.map({True: "Não Aderiu", False: "Aderiu"})
    df["ubs_status"] = mask_nao_aderiu.map({True: "Sem UBS/município informado", False: "UBS/município informado"})
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
        # Não retorna aqui: continua para bloco de normalização e classificação
        # centralizada (add_conemo_protocol_status), comum a todos os caminhos.
        
    except Exception as e:
        # Fallback técnico controlado para Parquet
        st.session_state["bq_success"] = False
        st.error(f"⚠️ Falha na fonte canônica (BigQuery). Erro: {str(e)}")
        st.info("Utilizando fallback temporário: Parquet local (Desatualizado)")
        
        if not os.path.exists(PARQUET_PATH):
            st.error("Falha crítica: nem BigQuery nem Parquet estão disponíveis.")
            # add_conemo_protocol_status garante colunas obrigatórias mesmo no DataFrame vazio
            return add_conemo_protocol_status(pd.DataFrame())

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
                    "ubs_name": org.get("name", "Não respondeu"),
                    "ubs_city": org.get("city", "Não respondeu"),
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
                return pd.Series({"ubs_name": "Não respondeu", "ubs_city": "Não respondeu", "phq_score": None, "gad_score": None, 
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
        test_city_pattern = r"test|teste|fake|load|carga|break|quebra"
        has_test_or_invalid_flag = (
            df["is_test"].fillna(False) | df["is_test_user"].fillna(False) | 
            df["is_invalid"].fillna(False) | df["is_test_environment"].fillna(False) | 
            df["ubs_city"].fillna("").str.lower().str.contains(test_city_pattern, regex=True)
        )
        df = df[(df["created_at_seconds"] >= DASHBOARD_CUTOFF_SECONDS) & (~has_test_or_invalid_flag)]

    # Normalizações finais (comuns a ambas as fontes)
    if "health_unit_key" not in df.columns:
        # Fallback técnico: coluna não existe em alguns legados de parquet.
        df["health_unit_key"] = None

    df["ubs_name"] = df["ubs_name"].str.upper().str.strip()
    df["ubs_city"] = df["ubs_city"].str.strip().str.title()
    
    _CIDADES_INVALIDAS = {"Fake City", "N/A", ""}
    df = df[df["ubs_city"].notna() & (~df["ubs_city"].isin(_CIDADES_INVALIDAS))]

    # -----------------------------------------------------------------------
    # Classificação operacional centralizada.
    # add_conemo_protocol_status cria conemo_protocol_status e ubs_status
    # usando a regra canônica dinâmica (health_unit_key == 'UNK_UHS').
    # Chamada aqui para todos os caminhos (BigQuery e Parquet fallback).
    # Ref: Docs/nota-decisoria-nao-aderiu-dashboard.md
    # -----------------------------------------------------------------------
    return add_conemo_protocol_status(df)


# Inicializa carregamento
df_all = load_data()

# ---------------------------------------------------------------------------
# Etapa 3 — Filtro dinâmico das análises principais
#
# Regras:
# - preservar DataFrame original completo (df_all), sem remoção física;
# - usar apenas aderentes nas análises principais (df_main);
# - não criar nova seção visual nesta etapa.
# ---------------------------------------------------------------------------
if "conemo_protocol_status" in df_all.columns:
    # Domínio analítico principal (Aderiu), sem alterar regra canônica.
    df_main = df_all[df_all["conemo_protocol_status"] == "Aderiu"].copy()
else:
    # Fallback seguro: sem status de adesão, bloquear análises principais
    # para evitar contaminação por base completa.
    st.error("Campo conemo_protocol_status ausente. Análises principais bloqueadas por segurança.")
    df_main = df_all.iloc[0:0].copy()

# Etapa 4 — Seção separada de monitoramento agregado do grupo Não Aderiu
if "conemo_protocol_status" in df_all.columns:
    # Domínio de governança (Não Aderiu), isolado do denominador analítico.
    df_nao_aderiu = df_all[df_all["conemo_protocol_status"] == "Não Aderiu"].copy()
else:
    # Fallback defensivo: sem coluna de status, seção agregada fica vazia.
    df_nao_aderiu = df_all.iloc[0:0].copy()

# Base aderente explícita para todo componente analítico principal
df_main_users = df_main.drop_duplicates(subset="user_id").copy()

# Aliases semânticos explícitos (Beta-F): legibilidade sem nova regra de negócio.
# - df_analysis_events: domínio analítico de eventos/sessões (Aderiu)
# - df_analysis_users: domínio analítico de usuários únicos (Aderiu)
# - df_governance_nao_aderiu: domínio separado de governança (Não Aderiu)
df_analysis_events = df_main
df_analysis_users = df_main_users
df_governance_nao_aderiu = df_nao_aderiu

# Mantém alias legado, porém restrito ao domínio analítico (Aderiu).
df = df_analysis_events

# Guardas de integridade do domínio analítico (Beta-F)
if (not df_analysis_events.empty) and (not df_analysis_events["conemo_protocol_status"].eq("Aderiu").all()):
    st.error("Erro de integridade: domínio analítico contém registros fora de Aderiu.")
    st.stop()

if "created_at" in df_analysis_events.columns:
    _created_at = pd.to_datetime(df_analysis_events["created_at"], errors="coerce", utc=True)
    min_created = _created_at.min()
    if pd.notna(min_created) and min_created < pd.Timestamp(DASHBOARD_CUTOFF_TS):
        st.error("Erro de integridade: domínio analítico contém registros antes de 2026-01-28.")
        st.stop()
elif "created_at_seconds" in df_analysis_events.columns:
    min_created_seconds = pd.to_numeric(df_analysis_events["created_at_seconds"], errors="coerce").min()
    if pd.notna(min_created_seconds) and float(min_created_seconds) < float(DASHBOARD_CUTOFF_SECONDS):
        st.error("Erro de integridade: domínio analítico contém registros antes de 2026-01-28.")
        st.stop()

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
    [
        "📊 Estatísticas por UBS",
        "🔍 Governança — Não Aderiu",
        "👤 Consulta auxiliar",
    ],
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


def age_group(age_value):
    if pd.isna(age_value):
        return "Não informado"
    try:
        age_int = int(age_value)
    except Exception:
        return "Não informado"
    if age_int < 18:
        return "< 18"
    if age_int <= 29:
        return "18–29"
    if age_int <= 39:
        return "30–39"
    if age_int <= 49:
        return "40–49"
    if age_int <= 59:
        return "50–59"
    if age_int <= 69:
        return "60–69"
    if age_int <= 79:
        return "70–79"
    return "80+"


def normalize_gender(value) -> str:
    """
    Normaliza valores de gênero para exibição agregada.
    Cobre formatos do mart curado (FEMININO/MASCULINO/NAO_INFORMADO)
    e do raw Firestore (F/M), sem expor dados individuais.
    Beta-E: correção de regressão de mapeamento.
    """
    if pd.isna(value):
        return "Não informado"
    v = str(value).strip().upper()
    if v in ("F", "FEMININO", "FEMALE", "MULHER", "WOMAN", "2"):
        return "Feminino"
    if v in ("M", "MASCULINO", "MALE", "HOMEM", "MAN", "1"):
        return "Masculino"
    if v in ("OUTRO", "OUTROS", "OTHER", "NAO_BINARIO", "NON-BINARY"):
        return "Outro"
    if v in ("", "NAN", "NONE", "NULL", "N/A", "NA", "NAO_INFORMADO",
             "NÃO INFORMADO", "NAO INFORMADO", "NOT_INFORMED"):
        return "Não informado"
    return "Não informado"


def _status_caption(page_label: str) -> None:
    st.caption(
        f"**{page_label}** — dashboard permanece **NÃO OPERACIONAL**. "
        "Execução local/validação técnica ≠ operacionalização institucional."
    )


def validate_runtime_contract(
    df_all: pd.DataFrame,
    df_main: pd.DataFrame,
    df_nao_aderiu: pd.DataFrame,
    df_main_users: pd.DataFrame,
) -> tuple[list[str], list[str]]:
    """
    Checagens leves de integridade de denominador/segregação/PII.
    - Não altera dados nem controla fonte/query.
    - Separa issues críticos (bloqueiam tela) de warnings preventivos (não bloqueiam por si só).
    """
    critical_issues: list[str] = []
    warnings: list[str] = []

    if df_all is None or df_main is None or df_nao_aderiu is None:
        return (["DataFrames essenciais ausentes (df_all/df_main/df_nao_aderiu)."], [])

    if "conemo_protocol_status" not in df_all.columns:
        critical_issues.append("Coluna `conemo_protocol_status` ausente em `df_all`.")
        return (critical_issues, warnings)

    # Denominadores e segregação
    if (not df_main.empty) and (df_main["conemo_protocol_status"] == "Não Aderiu").any():
        critical_issues.append("Violação de denominador: `df_main` contém registros `Não Aderiu`.")

    if (not df_nao_aderiu.empty) and (df_nao_aderiu["conemo_protocol_status"] == "Aderiu").any():
        critical_issues.append("Violação de segregação: `df_nao_aderiu` contém registros `Aderiu`.")

    if df_main_users is None or ("user_id" not in df_main_users.columns):
        critical_issues.append("Base `df_main_users` ausente ou sem coluna `user_id`.")

    # PII (checagem preventiva: não deve aparecer em tabelas centrais)
    # Observação: a visão auxiliar pode manter e-mail mascarado por legado.
    sensitive_columns = {"cpf", "phone", "telefone", "whatsapp", "address", "endereco"}
    lower_cols = {c.lower() for c in df_all.columns}
    if lower_cols.intersection(sensitive_columns):
        warnings.append("Atenção: colunas sensíveis detectadas no dataset carregado; não devem ser exibidas.")

    return (critical_issues, warnings)


# ---------------------------------------------------------------------------
# Página 1 — Estatísticas por UBS
# ---------------------------------------------------------------------------
if page == "📊 Estatísticas por UBS":
    st.title("Estatísticas por UBS")
    _status_caption("Tela central (UBS)")

    critical_issues, warnings = validate_runtime_contract(df_all, df_analysis_events, df_governance_nao_aderiu, df_analysis_users)
    for msg in warnings:
        st.warning(msg)
    if critical_issues:
        st.error("Checagens de integridade falharam (bloqueio local desta tela):")
        for msg in critical_issues:
            st.write(f"- {msg}")
        st.stop()

    st.divider()

    # --- Filtros (aderentes) ---
    with st.container():
        st.subheader("Usuários Ativos")
        col_f1, col_f2 = st.columns(2)
        all_cities = sorted(df_analysis_users["ubs_city"].dropna().unique())
        sel_cities = col_f1.multiselect(
            "Cidade",
            all_cities,
            default=all_cities,
            key="filtro_cidade_aderiu_v2",
        )

        df_city = df_analysis_events[df_analysis_events["ubs_city"].isin(sel_cities)] if sel_cities else df_analysis_events
        df_city_users = df_analysis_users[df_analysis_users["ubs_city"].isin(sel_cities)] if sel_cities else df_analysis_users
        all_ubs = sorted(df_city_users["ubs_name"].dropna().unique())
        sel_ubs = col_f2.multiselect(
            "UBS",
            all_ubs,
            default=all_ubs,
            key="filtro_ubs_aderiu_v2",
        )

    dff = df_city[df_city["ubs_name"].isin(sel_ubs)] if sel_ubs else df_city

    # DataFrame de participantes únicos (base aderente explícita)
    df_users = df_city_users[df_city_users["ubs_name"].isin(sel_ubs)] if sel_ubs else df_city_users
    if (not df_users.empty) and (not df_analysis_users.empty):
        if not set(df_users["user_id"].unique()).issubset(set(df_analysis_users["user_id"].unique())):
            st.error("Violação de denominador: `df_users` não é subconjunto de `df_analysis_users` (bloqueio local).")
            st.stop()

    st.divider()

    # --- Métricas (aderentes) ---
    st.subheader("Resumo executivo")
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

    st.caption("Todas as métricas acima são calculadas sobre `df_main`/`df_main_users` (aderentes) e seus derivados locais.")

    st.divider()

    tab_a, tab_b = st.tabs(["📈 Indicadores por UBS", "👥 Perfil e completude"])

    with tab_a:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Participantes por UBS")
            ubs_count = df_users["ubs_name"].value_counts().reset_index()
            ubs_count.columns = ["UBS", "Participantes"]
            fig = px.bar(
                ubs_count.sort_values("Participantes"),
                x="Participantes",
                y="UBS",
                orientation="h",
                color="Participantes",
                color_continuous_scale="Blues",
            )
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=420)
            st.plotly_chart(fig, width="stretch")
            # E.7-C.1 — CSV-02: participantes_por_ubs.csv
            # Base: df_users (derivado de df_main_users, aderentes). Sem RAW, sem PII direta.
            st.caption("⚠️ Exportação para uso interno autorizado — dados restritos à finalidade assistencial/operacional CONEMO. Dashboard NÃO OPERACIONAL.")
            st.download_button(
                "⬇️ CSV — Participantes por UBS",
                ubs_count.to_csv(index=False).encode("utf-8"),
                "participantes_por_ubs.csv",
                "text/csv",
                key="dl_ubs_count",
            )

        with col2:
            st.subheader("Média PHQ-9 e GAD-7 por UBS")
            scores_ubs = (
                df_users.groupby("ubs_name")[["phq_score", "gad_score"]]
                .mean()
                .reset_index()
                .rename(columns={"ubs_name": "UBS", "phq_score": "PHQ-9", "gad_score": "GAD-7"})
            )
            scores_melt = scores_ubs.melt(id_vars="UBS", var_name="Escala", value_name="Média")
            fig2 = px.bar(
                scores_melt,
                x="Média",
                y="UBS",
                color="Escala",
                orientation="h",
                barmode="group",
                color_discrete_map={"PHQ-9": "#EF553B", "GAD-7": "#636EFA"},
            )
            fig2.update_layout(height=420)
            st.plotly_chart(fig2, width="stretch")
            # E.7-C.1 — CSV-03: scores_phq_gad_por_ubs.csv
            # Base: df_users agrupado por UBS, médias PHQ-9/GAD-7. Sem RAW, sem PII direta.
            st.caption("⚠️ Exportação para uso interno autorizado. Dashboard NÃO OPERACIONAL.")
            st.download_button(
                "⬇️ CSV — Scores PHQ-9 e GAD-7 por UBS",
                scores_ubs.to_csv(index=False).encode("utf-8"),
                "scores_phq_gad_por_ubs.csv",
                "text/csv",
                key="dl_scores_ubs",
            )

        st.divider()
        st.subheader("Resumo por UBS")
        comp_ubs = (
            dff.groupby("ubs_name")["isCompleted"]
            .apply(lambda x: x.mean() * 100 if x.count() > 0 else 0.0)
            .reset_index(name="Taxa (%)")
            .rename(columns={"ubs_name": "UBS"})
        )
        comp_lookup = comp_ubs.set_index("UBS")["Taxa (%)"].to_dict()
        resumo = (
            df_users.groupby("ubs_name")
            .agg(
                Participantes=("user_id", "nunique"),
                PHQ9_media=("phq_score", "mean"),
                GAD7_media=("gad_score", "mean"),
            )
            .reset_index()
            .rename(columns={"ubs_name": "UBS"})
        )
        resumo["Conclusão (%)"] = resumo["UBS"].map(comp_lookup).round(1)
        resumo["PHQ-9 Média"] = resumo["PHQ9_media"].round(1)
        resumo["GAD-7 Média"] = resumo["GAD7_media"].round(1)
        resumo = resumo[["UBS", "Participantes", "PHQ-9 Média", "GAD-7 Média", "Conclusão (%)"]].sort_values(
            "Participantes", ascending=False
        )
        with st.expander("Ver tabela completa de resumo por UBS", expanded=True):
            st.dataframe(resumo, width="stretch", hide_index=True)
            # E.7-C.1 — CSV-07: resumo_por_ubs.csv
            # Base: df_users agrupado por UBS (Participantes, PHQ-9, GAD-7, Taxa Conclusão). Sem RAW, sem PII direta.
            st.caption("⚠️ Exportação para uso interno autorizado. Dashboard NÃO OPERACIONAL.")
            st.download_button(
                "⬇️ CSV — Resumo por UBS",
                resumo.to_csv(index=False).encode("utf-8"),
                "resumo_por_ubs.csv",
                "text/csv",
                key="dl_resumo",
            )

        # E.7-C.1 — CSV-01: resumo_municipios.csv
        # Base: df_users (aderentes com filtros aplicados) agrupado por cidade. Sem RAW, sem PII direta.
        resumo_mun = (
            df_users.groupby("ubs_city")
            .agg(
                Participantes=("user_id", "nunique"),
                UBSs=("ubs_name", "nunique"),
                PHQ9_media=("phq_score", "mean"),
                GAD7_media=("gad_score", "mean"),
            )
            .reset_index()
            .rename(columns={"ubs_city": "Município"})
        )
        resumo_mun["PHQ-9 Média"] = resumo_mun["PHQ9_media"].round(1)
        resumo_mun["GAD-7 Média"] = resumo_mun["GAD7_media"].round(1)
        resumo_mun = resumo_mun[
            ["Município", "Participantes", "UBSs", "PHQ-9 Média", "GAD-7 Média"]
        ].sort_values("Participantes", ascending=False)
        with st.expander("Resumo por Município", expanded=False):
            st.dataframe(resumo_mun, width="stretch", hide_index=True)
            st.caption("Denominador: participantes aderentes (df_main_users) com filtros de cidade/UBS aplicados.")
            st.caption("⚠️ Exportação para uso interno autorizado. Dashboard NÃO OPERACIONAL.")
            st.download_button(
                "⬇️ CSV — Resumo por Município",
                resumo_mun.to_csv(index=False).encode("utf-8"),
                "resumo_municipios.csv",
                "text/csv",
                key="dl_mun",
            )

    with tab_b:
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Taxa de Conclusão por UBS")
            comp_ubs = (
                dff.groupby("ubs_name")["isCompleted"]
                .apply(lambda x: x.mean() * 100 if x.count() > 0 else 0.0)
                .reset_index(name="Taxa (%)")
                .rename(columns={"ubs_name": "UBS"})
            )
            fig3 = px.bar(
                comp_ubs.sort_values("Taxa (%)"),
                x="Taxa (%)",
                y="UBS",
                orientation="h",
                color="Taxa (%)",
                color_continuous_scale="Greens",
            )
            fig3.update_layout(showlegend=False, coloraxis_showscale=False, height=380)
            st.plotly_chart(fig3, width="stretch")
            # E.7-C.1 — CSV-04: taxa_conclusao_por_ubs.csv
            # Base: dff (sessões aderentes filtradas) agrupado por UBS. Sem RAW, sem PII direta.
            st.caption("⚠️ Exportação para uso interno autorizado. Dashboard NÃO OPERACIONAL.")
            st.download_button(
                "⬇️ CSV — Taxa de Conclusão por UBS",
                comp_ubs.to_csv(index=False).encode("utf-8"),
                "taxa_conclusao_por_ubs.csv",
                "text/csv",
                key="dl_comp_ubs",
            )

        with col4:
            st.subheader("Distribuição de Gênero")
            # Beta-E: usa normalize_gender para cobrir valores do mart curado
            # (FEMININO/MASCULINO/NAO_INFORMADO) e do raw (F/M).
            gender_counts = (
                df_users["gender"]
                .apply(normalize_gender)
                .value_counts()
                .reset_index()
            )
            gender_counts.columns = ["Gênero", "Contagem"]
            fig4 = px.pie(
                gender_counts,
                names="Gênero",
                values="Contagem",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig4.update_layout(height=380)
            st.plotly_chart(fig4, width="stretch")
            # E.7-C.1 — CSV-05: distribuicao_genero.csv
            # Base: df_users (aderentes). Sem RAW, sem PII direta.
            st.caption("⚠️ Exportação para uso interno autorizado. Dashboard NÃO OPERACIONAL.")
            st.download_button(
                "⬇️ CSV — Distribuição de Gênero",
                gender_counts.to_csv(index=False).encode("utf-8"),
                "distribuicao_genero.csv",
                "text/csv",
                key="dl_gender",
            )

        st.divider()
        st.subheader("Distribuição por Faixa Etária")

        age_order = ["< 18", "18–29", "30–39", "40–49", "50–59", "60–69", "70–79", "80+", "Não informado"]
        age_data = (
            df_users["age"]
            .apply(age_group)
            .value_counts()
            .reindex(age_order, fill_value=0)
            .reset_index()
        )
        age_data.columns = ["Faixa Etária", "Participantes"]
        fig5 = px.bar(
            age_data,
            x="Faixa Etária",
            y="Participantes",
            color="Participantes",
            color_continuous_scale="Purples",
        )
        fig5.update_layout(showlegend=False, coloraxis_showscale=False, height=360)
        st.plotly_chart(fig5, width="stretch")
        # E.7-C.1 — CSV-06: distribuicao_faixa_etaria.csv
        # Base: df_users (aderentes). Sem RAW, sem PII direta.
        st.caption("⚠️ Exportação para uso interno autorizado. Dashboard NÃO OPERACIONAL.")
        st.download_button(
            "⬇️ CSV — Distribuição por Faixa Etária",
            age_data.to_csv(index=False).encode("utf-8"),
            "distribuicao_faixa_etaria.csv",
            "text/csv",
            key="dl_ages",
        )

        st.caption("Calculado apenas sobre participantes aderentes (df_main_users).")

        # -----------------------------------------------------------------------
        # E.7-C.3 — Exportações dependentes de nova fonte canônica (placeholders)
        # CSV-08, CSV-09, CSV-11, CSV-12, CSV-15
        # Não implementar enquanto depender de RAW sem contrato canônico validado.
        # Fontes ausentes: journeys_raw_latest, patient_feedback_raw_latest
        # -----------------------------------------------------------------------
        with st.expander("📤 Exportações pendentes de fonte canônica (E.7-C.3)", expanded=False):
            st.info(
                "Exportação preservada. Conteúdo pendente de fonte canônica validada."
            )
            st.caption("Dashboard NÃO OPERACIONAL.")
            st.caption(
                "Fontes ausentes na Fase E: `journeys_raw_latest`, `patient_feedback_raw_latest`. "
                "Não implementar enquanto depender de RAW sem contrato canônico."
            )
            _c1, _c2, _c3 = st.columns(3)
            # CSV-08: jornadas_por_tipo.csv — depende de journeys_raw_latest
            _c1.download_button(
                "⬇️ Jornadas por Tipo (indisponível)",
                data=b"",
                file_name="jornadas_por_tipo.csv",
                mime="text/csv",
                key="dl_jtype",
                disabled=True,
            )
            # CSV-09: jornadas_por_ubs.csv — depende de journeys_raw_latest
            _c2.download_button(
                "⬇️ Jornadas por UBS (indisponível)",
                data=b"",
                file_name="jornadas_por_ubs.csv",
                mime="text/csv",
                key="dl_jubs",
                disabled=True,
            )
            # CSV-11: feedback_por_tipo.csv — depende de patient_feedback_raw_latest
            _c3.download_button(
                "⬇️ Feedback por Tipo (indisponível)",
                data=b"",
                file_name="feedback_por_tipo.csv",
                mime="text/csv",
                key="dl_ftype",
                disabled=True,
            )
            _c4, _c5, _c6 = st.columns(3)
            # CSV-12: feedback_por_fonte.csv — depende de patient_feedback_raw_latest
            _c4.download_button(
                "⬇️ Feedback por Fonte (indisponível)",
                data=b"",
                file_name="feedback_por_fonte.csv",
                mime="text/csv",
                key="dl_fsource",
                disabled=True,
            )
            # CSV-15: feedback_{id}.csv por participante — depende de patient_feedback_raw_latest
            _c5.download_button(
                "⬇️ Feedback por Participante (indisponível)",
                data=b"",
                file_name="feedback_participante.csv",
                mime="text/csv",
                key="dl_pfb_placeholder",
                disabled=True,
            )
            # CSV-17 completo: sessoes_por_paciente.csv (versão completa) — depende de journeys_raw_latest
            _c6.download_button(
                "⬇️ Sessões por Paciente — completo (indisponível)",
                data=b"",
                file_name="sessoes_por_paciente_completo.csv",
                mime="text/csv",
                key="dl_sessoes_completo",
                disabled=True,
            )

        # -----------------------------------------------------------------------
        # E.7-C.4 — Exportações condicionadas a decisão explícita do professor
        # CSV-10, CSV-13, CSV-16
        # Motivo: user_id por linha, patientId, patientWhatsAppId, PHQ crítico, IGI atual.
        # -----------------------------------------------------------------------
        with st.expander("🔒 Exportações pendentes de deliberação (E.7-C.4)", expanded=False):
            st.warning(
                "Exportação condicionada à decisão do professor sobre dados sensíveis."
            )
            st.caption(
                "Campos sensíveis envolvidos: `user_id` por linha, `patientId`, `patientWhatsAppId`, PHQ crítico, IGI atual."
            )
            st.caption(
                "Nenhum código será escrito, nenhuma query executada, nenhum campo incluído "
                "até que a deliberação formal seja registrada em `Docs/fase-e7c-incorporacao-csv-dashboard.md`."
            )
            _d1, _d2, _d3 = st.columns(3)
            # CSV-10: jornadas_detalhes.csv — user_id por linha + timestamp acesso
            _d1.download_button(
                "⬇️ Jornadas Detalhes (deliberação pendente)",
                data=b"",
                file_name="jornadas_detalhes.csv",
                mime="text/csv",
                key="dl_jdetails",
                disabled=True,
            )
            # CSV-13: feedbacks_recentes.csv — patientId, patientWhatsAppId
            _d2.download_button(
                "⬇️ Feedbacks Recentes (deliberação pendente)",
                data=b"",
                file_name="feedbacks_recentes.csv",
                mime="text/csv",
                key="dl_freq",
                disabled=True,
            )
            # CSV-16: formulario_web_por_paciente.csv — PHQ crítico, IGI atual
            _d3.download_button(
                "⬇️ Formulário Web por Paciente (deliberação pendente)",
                data=b"",
                file_name="formulario_web_por_paciente.csv",
                mime="text/csv",
                key="dl_forms_web",
                disabled=True,
            )

# ---------------------------------------------------------------------------
# Governança — Monitoramento do grupo "Não Aderiu"
#
# Seção separada para acompanhamento agregado (sem PII) de usuários que não
# aderiram plenamente ao protocolo clínico de inclusão/entrada do CONEMO.
# Ref: Docs/nota-decisoria-nao-aderiu-dashboard.md
# ---------------------------------------------------------------------------
if page == "🔍 Governança — Não Aderiu":
    st.title("Governança — Não Aderiu")
    _status_caption("Governança (Não Aderiu)")
    st.divider()

    with st.expander("🔍 Governança — Qualidade de Dados (Não Aderiu)", expanded=True):
        st.caption("Esta página é de governança e usa o domínio Não Aderiu. Ela não compõe o denominador analítico principal das métricas por UBS.")
        st.markdown(
            """
            **Nota de Governança:**
            
            Usuários classificados como "Não Aderiu" não aderiram plenamente ao 
            protocolo clínico de inclusão/entrada do CONEMO. Eles são monitorados 
            apenas para governança e qualidade dos dados. **Não compõem os 
            indicadores principais do dashboard** (que exibe 132 participantes aderentes).
            """
        )
        
        st.markdown("---")
        
        if df_governance_nao_aderiu.empty:
            st.info("Nenhum usuário registrado no grupo 'Não Aderiu'.")
        else:
            # Métricas agregadas (sem PII, apenas contagens)
            col_g1, col_g2, col_g3 = st.columns(3)
            
            total_nao_aderiu = df_governance_nao_aderiu["user_id"].nunique()
            total_aderiu = df_analysis_users["user_id"].nunique()
            total_geral = total_aderiu + total_nao_aderiu
            pct_nao_aderiu = (total_nao_aderiu / total_geral * 100) if total_geral > 0 else 0
            
            col_g1.metric("Total — Não Aderiu", total_nao_aderiu)
            col_g2.metric("% do Total Interno", f"{pct_nao_aderiu:.1f}%")
            
            # Breakdown: com/sem score
            nao_aderiu_com_score = (
                df_governance_nao_aderiu[
                    (df_governance_nao_aderiu["phq_score"].notna()) | (df_governance_nao_aderiu["gad_score"].notna())
                ]["user_id"].nunique()
            )
            nao_aderiu_sem_score = total_nao_aderiu - nao_aderiu_com_score
            col_g3.metric("Sem Score PHQ/GAD", nao_aderiu_sem_score)
            
            col_g4, col_g5 = st.columns(2)
            col_g4.metric("Com algum Score PHQ/GAD", nao_aderiu_com_score)
            
            # Critério de classificação: health_unit_key
            nao_aderiu_unk_uhs = (
                df_governance_nao_aderiu[df_governance_nao_aderiu["health_unit_key"] == "UNK_UHS"]["user_id"].nunique()
            )
            col_g5.metric("health_unit_key = UNK_UHS", nao_aderiu_unk_uhs)
            
            st.markdown("---")
            
            # Distribuição temporal (agregado por mês)
            st.subheader("Distribuição Temporal — Entrada de Não Aderentes")
            if "created_at" in df_governance_nao_aderiu.columns:
                df_temporal = df_governance_nao_aderiu.copy()
                df_temporal["created_at"] = pd.to_datetime(df_temporal["created_at"], errors="coerce")
                df_temporal["mes_entrada"] = df_temporal["created_at"].dt.strftime("%Y-%m")
                temporal_agg = df_temporal.groupby("mes_entrada")["user_id"].nunique().reset_index()
                temporal_agg.columns = ["Mês", "Contagem"]
                temporal_agg = temporal_agg.sort_values("Mês")
                
                fig_temporal = px.bar(
                    temporal_agg,
                    x="Mês",
                    y="Contagem",
                    color="Contagem",
                    color_continuous_scale="Blues",
                    title="Entrada de Usuários — Não Aderiu",
                )
                fig_temporal.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig_temporal, width="stretch")
            
            st.markdown("---")
            
            # Status territorial (agregado)
            st.subheader("Status Territorial — Não Aderentes")
            if "ubs_status" in df_governance_nao_aderiu.columns:
                ubs_status_counts = df_governance_nao_aderiu["ubs_status"].value_counts().reset_index()
                ubs_status_counts.columns = ["Status", "Contagem"]
                fig_ubs_status = px.pie(
                    ubs_status_counts,
                    names="Status",
                    values="Contagem",
                    hole=0.4,
                    title="Distribuição — Status Territorial",
                )
                fig_ubs_status.update_layout(height=300)
                st.plotly_chart(fig_ubs_status, width="stretch")
            
            st.markdown("---")
            
            # Intervalo de data
            if "created_at" in df_governance_nao_aderiu.columns:
                df_temporal_check = df_governance_nao_aderiu.copy()
                df_temporal_check["created_at"] = pd.to_datetime(df_temporal_check["created_at"], errors="coerce")
                data_min = df_temporal_check["created_at"].min()
                data_max = df_temporal_check["created_at"].max()
                st.info(
                    f"**Intervalo de Entrada:** {data_min.strftime('%d/%m/%Y %H:%M') if pd.notna(data_min) else 'N/D'} "
                    f"até {data_max.strftime('%d/%m/%Y %H:%M') if pd.notna(data_max) else 'N/D'}"
                )

# ---------------------------------------------------------------------------
# Visão individual por participante
# ---------------------------------------------------------------------------
if page == "👤 Consulta auxiliar":
    st.title("Consulta auxiliar por participante")
    _status_caption("Consulta auxiliar")
    st.divider()

    with st.expander("👤 Consulta individual por participante (visão auxiliar)", expanded=True):
        st.subheader("Estatísticas por Participante")
        # Consulta auxiliar padrão restrita ao domínio analítico (Aderiu).
        df_aux_users = df_analysis_users.copy()
        df_aux_events = df_analysis_events.copy()

        user_ids = sorted(df_aux_users["user_id"].dropna().unique())
        selected_id = st.selectbox("Selecione o ID do participante", user_ids)

        df_user = df_aux_events[df_aux_events["user_id"] == selected_id]
        if df_user.empty:
            st.warning("Participante não encontrado.")
        else:
            row = df_user.iloc[0]
            st.markdown("---")
            st.subheader("Perfil")

            gender_label = normalize_gender(row.get("gender", ""))
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

            # Scores Atuais
            st.markdown("---")
            st.subheader("Scores de Saúde Mental (Representação Atual)")
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

            # Histórico Longitudinal (Fase D.4)
            st.markdown("---")
            st.subheader("📜 Histórico Longitudinal PHQ/GAD")
            
            # Carrega histórico apenas se estiver em modo BigQuery
            if st.session_state.get("bq_success", False):
                df_history = load_history_from_bigquery(selected_id)
                if not df_history.empty:
                    st.dataframe(
                        df_history[["instrument", "score", "data_avaliacao", "status_score", "contexto"]].rename(
                            columns={
                                "instrument": "Instrumento",
                                "score": "Score",
                                "data_avaliacao": "Data da Avaliação",
                                "status_score": "Status",
                                "contexto": "Origem/Contexto"
                            }
                        ),
                        width='stretch',
                        hide_index=True
                    )
                else:
                    st.info("Nenhum histórico adicional encontrado para este participante.")
            else:
                st.info("Histórico longitudinal disponível apenas na conexão BigQuery (Modo Canônico).")

            # Progresso das Sessões
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

            # E.7-C.2 — CSV-14: sessoes_{id}.csv
            # Base: sessões do participante selecionado, da consulta auxiliar canônica.
            # Finalidade: acompanhamento clínico por equipe da UBS.
            # PII permitida (finalidade assistencial autorizada). Controle por perfil e log
            # de exportações serão implementados antes da operacionalização.
            with st.expander("Ver tabela de sessões e exportar"):
                tbl_sessions_csv = sessions[["Sessão", "Status", "completedDate"]].rename(
                    columns={"completedDate": "Data de conclusão"}
                )
                st.dataframe(tbl_sessions_csv, width="stretch", hide_index=True)
                st.caption(
                    "⚠️ Exportação clínico-operacional para uso interno autorizado. "
                    "Finalidade: acompanhamento de sessões por equipe clínica da UBS. Dashboard NÃO OPERACIONAL."
                )
                st.caption("Controle por perfil e log de exportações serão implementados antes da operacionalização.")
                st.download_button(
                    "⬇️ CSV — Sessões deste participante",
                    tbl_sessions_csv.to_csv(index=False).encode("utf-8"),
                    f"sessoes_{selected_id}.csv",
                    "text/csv",
                    key="dl_sessions",
                )

        # E.7-C.2 — CSV-17 parcial: sessoes_por_paciente.csv (versão parcial sem jornadas RAW)
        # Base: df_main (aderentes). Resumo de sessões por participante sem fonte RAW nova.
        # Finalidade: acompanhamento clínico agregado por UBS.
        # Controle por perfil e log de exportações serão implementados antes da operacionalização.
        with st.expander("📋 Resumo de sessões — todos os participantes aderentes (E.7-C.2)", expanded=False):
            st.caption(
                "Exportação parcial (sem dados de jornadas RAW). "
                "Versão completa pendente de fonte canônica (`journeys_raw_latest`). Dashboard NÃO OPERACIONAL."
            )
            sessoes_por_pac = (
                df_main.groupby("user_id")
                .agg(
                    UBS=("ubs_name", "first"),
                    Cidade=("ubs_city", "first"),
                    Total_Sessoes=("sessionNumber", "nunique"),
                    Sessoes_Concluidas=("isCompleted", lambda x: int(x.sum())),
                )
                .reset_index()
                .rename(columns={"user_id": "Participante"})
            )
            sessoes_por_pac["Taxa_Conclusao_pct"] = (
                sessoes_por_pac["Sessoes_Concluidas"] / sessoes_por_pac["Total_Sessoes"] * 100
            ).round(1)
            st.dataframe(sessoes_por_pac, width="stretch", hide_index=True)
            st.caption(
                "⚠️ Exportação clínico-operacional para uso interno autorizado. "
                "Finalidade assistencial/operacional CONEMO."
            )
            st.caption("Controle por perfil e log de exportações serão implementados antes da operacionalização.")
            st.download_button(
                "⬇️ CSV — Sessões por Participante (parcial)",
                sessoes_por_pac.to_csv(index=False).encode("utf-8"),
                "sessoes_por_paciente.csv",
                "text/csv",
                key="dl_sessoes",
            )
