# Fase C.1 — Diagnóstico de Integração BigQuery-Dashboard

**Data:** 2026-04-24  
**Status:** Concluído  
**Branch:** `fase-c1-diagnostico-integracao-bigquery-dashboard`

## 1. Objetivo
Mapear o contrato atual de dados do dashboard (`dashboard_conemo.py`) e avaliar a viabilidade de substituição da fonte Parquet local pelas tabelas curadas do BigQuery, preservando as regras operacionais vigentes.

## 2. Modo da Tarefa
**H. Documentação e handoff** (Tipo Diagnóstico e Especificação)

## 3. Fontes Consultadas
- `Code/PY/dashboard_conemo.py`
- `conemo-412202.firestore_curated.*` (INFORMATION_SCHEMA e Schema via BQ CLI)
- `conemo-412202.firestore_export.users_raw_latest`
- `Docs/correcao-pre-merge-pr2-filtro-usuarios-ativos-2026-01-25.md`

## 4. Ambiente Git Confirmado
- Repositório: `conemo-project/conemo`
- Branch: `fase-c1-diagnostico-integracao-bigquery-dashboard`
- Ponto de partida: `main` (pós-merge PR #2)

## 5. Contrato Atual do Dashboard (Parquet/Python)

O dashboard consome um arquivo Parquet denormalizado onde cada linha representa uma interação participante-sessão.

### Campos Consumidos:
| Campo | Origem/Transformação | Tipo esperado |
| :--- | :--- | :--- |
| `user_id` | Direto do Parquet | String |
| `sessionNumber` | Direto (Normalizado numeric) | Integer |
| `isCompleted` | Direto (Normalizado bool) | Boolean |
| `completedDate` | Direto | Timestamp/String |
| `ubs_name` | JSON `data.organization.name` | String (Upper) |
| `ubs_city` | JSON `data.organization.city` | String (Title) |
| `gender` | JSON `data.gender` | String |
| `age` | Calculado de `data.birthDate` | Integer |
| `phq_score` | JSON `data.forms[0].scores` | Float |
| `gad_score` | JSON `data.forms[0].scores` | Float |
| `created_at_seconds`| JSON `data.createdAt._seconds` | Float (Seconds) |
| `email` | Direto (Mascara em Python) | String |
| `user_name` | JSON `data.name` | String |
| **Flags Teste** | `isTest`, `isTestUser`, `invalid`, `testEnvironment` | Boolean |

## 6. Matriz de Compatibilidade: Parquet → BigQuery

| Campo Dashboard | Equivalente BigQuery | Fonte Recomendada | Status | Transformação |
| :--- | :--- | :--- | :--- | :--- |
| `user_id` | `participant_master_id` | `cur_participant_current_v1` | OK | N/A |
| `sessionNumber` | `session_number` | `cur_session_current_v1` | OK | N/A |
| `isCompleted` | `is_completed` | `cur_session_current_v1` | OK | N/A |
| `ubs_name` | `ubs_name` | `cur_health_unit_v1` | OK | Join por `health_unit_key` |
| `ubs_city` | `ubs_city` | `cur_health_unit_v1` | OK | Join por `health_unit_key` |
| `gender` | `gender` | `cur_participant_current_v1` | OK | N/A |
| `age` | `birthDate` (Parsing JSON) | `users_raw_latest` | **LACUNA** | Parsing em SQL ou Python |
| `phq_score` | `score_value` | `cur_score_current_v1` | OK | Join + Filtro `score_type='PHQ'` |
| `gad_score` | `score_value` | `cur_score_current_v1` | OK | Join + Filtro `score_type='GAD'` |
| `created_at` | `created_at` | `cur_participant_current_v1` | OK | Timestamp vs Seconds |
| `flags_teste` | `is_test_record` | `cur_participant_current_v1` | OK | Unificação das 4 flags |

## 7. Validação da Regra `createdAt >= 2026-01-25`

É perfeitamente possível aplicar a regra no BigQuery utilizando:
`WHERE created_at >= '2026-01-25 00:00:00 UTC'` na tabela `cur_participant_current_v1`.

## 8. Contagens Diagnósticas (Snapshot 2026-04-24)

- **BigQuery Bruto (`users_raw_latest`):** 482
- **BigQuery Curado (`cur_participant_current_v1`):** 481
- **Subconjunto Pós-Corte (`>= 2026-01-25`):** 228
- **Parquet Local (Fase B):** 133 (participantes únicos após filtros de data + flags de teste)

**Divergência:** A diferença entre 228 (BigQuery) e 133 (Parquet) deve-se provavelmente às flags de teste e limpeza de dados (PII/Invalid) que o Parquet já sofreu e que a camada curada pode estar refletindo de forma diferente ou contendo mais registros brutos ainda não filtrados pela regra de negócio do dashboard.

## 9. Lacunas e Riscos

1. **Campos Ausentes na Camada Curada:** `age` (via `birthDate`), `user_name` e `email`. 
    - *Impacto:* A visão individual perderá esses dados se usar apenas `cur_*`.
    - *Solução:* Join com `users_raw_latest.data` (parsing do JSON) para campos não sensíveis (`age`) ou manter máscara rigorosa para PII (`email`, `user_name`).
2. **Denormalização:** O dashboard espera um DataFrame denormalizado. 
    - *Risco:* Performance ao realizar múltiplos Joins (`participant` x `session` x `score` x `health_unit`) em cada `load_data()`.
3. **Flags de Teste:** A view `cur_participant_current_v1.is_test_record` precisa ser validada se realmente captura as 4 flags usadas no dashboard (`isTest`, `isTestUser`, `invalid`, `testEnvironment`).

## 10. Recomendação Técnica para Fase C.2

**Recomendação:** Implementação de uma **View de Integração Dashboard** (ou Query consolidada) no BigQuery.

**Justificativa:** 
Substituir o Parquet por uma query que unifique as tabelas curadas preserva a arquitetura de dados e reduz a complexidade do Python. 
- Usar `cur_participant_current_v1` como base.
- Join com `cur_session_current_v1` para granularidade de sessões.
- Join com `cur_health_unit_v1` para nomes de UBS e cidades.
- Subquery ou CTE para pivotar scores de PHQ e GAD de `cur_score_current_v1`.
- Parsing cirúrgico de `users_raw_latest.data` apenas para o campo `birthDate` (idade).

**A Fase C.2 deve implementar essa query/view e configurar o conector BigQuery no Streamlit.**

## 11. Confirmações Finais
- [x] Nenhum código foi alterado.
- [x] Nenhum SQL/mart foi alterado.
- [x] Nenhum objeto BigQuery foi alterado.
- [x] Nenhuma nova fase foi iniciada.

---
**Executor:** Gemini CLI Agent  
**Data:** 2026-04-24
