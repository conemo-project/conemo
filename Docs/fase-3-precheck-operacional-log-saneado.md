# Fase 3 — Log saneado do pré-check operacional (antes da Etapa 3.2)

**Data:** 2026-04-07  
**Escopo:** autenticação, autorização, visibilidade de datasets/objetos, prontidão de ambiente BigQuery  
**Segurança:** sem conteúdo da chave JSON, sem dados sensíveis, sem escrita em objetos de produção

---

## Evidências resumidas

### [T1] Credencial local
- `GOOGLE_APPLICATION_CREDENTIALS` inicialmente não definida.
- Arquivo no caminho autorizado encontrado.

### [T2] Ferramentas
- `gcloud` disponível.
- `bq` disponível.

### [T3] Autenticação e projeto
- Conta ativa: `ricardo-ceneviva@conemo-412202.iam.gserviceaccount.com`
- Projeto ativo: `conemo-412202`

### [T4] Query de conectividade
- `SELECT 1` em BigQuery: sucesso.

### [T5] Datasets
- Dataset visível: `firestore_export`
- Dataset esperado de destino (`firestore_curated`): não encontrado.

### [T6] Leitura de fontes mínimas
- Leitura de `users_raw_latest`: sucesso.
- Leitura de `sessions_raw_latest`: sucesso.
- Leitura de `journeys_raw_latest`: sucesso.

### [T7] IAM
- Papéis detectados para conta ativa no projeto:
  - `roles/bigquery.admin`
  - `roles/firebase.admin`

### [T8] Dry-run DDL no destino esperado
- Falha: dataset de destino inexistente / incompatibilidade de localização reportada.

---

## Resultado operacional do log

- Autenticação: **OK**
- Leitura das fontes: **OK**
- Projeto alvo: **OK**
- Destino para continuidade da fase: **pendente**
- Escrita efetiva em objetos: **não realizada**

Classificação final: **apto com ressalvas**
