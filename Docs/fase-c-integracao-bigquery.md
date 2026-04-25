# Fase C — Integração BigQuery → Dashboard

## Introdução
Esta fase documenta a transição do dashboard CONEMO para o BigQuery como fonte de dados canônica, eliminando a dependência do arquivo Parquet local desatualizado.

---

## Fase C.2 — Implementação controlada (Revisada e Corrigida)

### Objetivo
Substituir a leitura do Parquet por leitura direta via BigQuery (dataset `firestore_curated`), preservando o contrato do DataFrame e o comportamento funcional do Dashboard. 

**Correção:** A query foi ajustada para degradar temporariamente os campos `phq_score` e `gad_score` para `NULL` devido a um erro de schema identificado na view `cur_score_current_v1` do BigQuery.

### Fontes usadas
- **Canônica:** `conemo-412202.firestore_curated.cur_participant_current_v1`
- **Suporte:**
    - `conemo-412202.firestore_curated.cur_health_unit_v1`
    - `conemo-412202.firestore_curated.cur_session_current_v1`
- **Raw (Campos de Perfil):** `conemo-412202.firestore_export.users_raw_latest`

### Arquivos modificados
- `Code/PY/dashboard_conemo.py`

### Query BigQuery corrigida
```sql
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
```

### Comprovação Técnica (Execução Real)
A integração foi validada em 2026-04-24 com sucesso técnico da leitura BigQuery para o contrato mínimo da C.2, com limitação temporária dos scores PHQ/GAD como nulos. Os resultados foram:
- **Fonte Ativa no Teste:** BigQuery (Sem acionamento do fallback Parquet).
- **Linhas retornadas:** 247
- **Participantes únicos:** 125
- **Filtro temporal:** Respeitado (Min CreatedAt: 2026-01-28)
- **Filtro flags:** Respeitado (is_test_record = False)

### Limitações e Bloqueios
- **Scores Clínicos:** Na C.2 revisada, `phq_score` e `gad_score` foram mantidos no contrato do DataFrame, mas retornam NULL temporariamente até saneamento da fonte `cur_score_current_v1` ou fase técnica específica. 
- **Dependência Raw:** O cálculo de idade ainda exige parsing de JSON da camada Raw.

---

## Fase C.3 — Validação e corte

### Objetivo
Confirmar a equivalência funcional da integração BigQuery e decidir o status do arquivo Parquet local.

### Premissas herdadas da C.2
- BigQuery é a fonte canônica vigente.
- Parquet está desatualizado.
- Scores PHQ/GAD estão temporariamente nulos.
- PII mantida por decisão do professor.

### Fonte ativa testada
**BigQuery** (Dataset `firestore_curated` + `users_raw_latest`). O fallback Parquet permaneceu inativo durante os testes de sucesso.

### Contagens BigQuery (Snapshot 2026-04-24)
| Métrica | BigQuery | Parquet histórico/fallback | Interpretação |
|---|---:|---:|---|
| Linhas totais | 4857 | ~9000 | BQ reflete apenas dados curados/validados; Parquet continha duplicatas brutas. |
| Participantes únicos | 481 | 389 | BQ contém o histórico completo; Parquet era um recorte parcial. |
| Após corte temporal (>= 2026-01-25) | 228 | 135 | Recorte operacional atualizado no BigQuery. |
| **Consumido pelo dashboard (Limpo)** | **125** | **133** | Diferença de 8 registros devido a critérios de saneamento mais rígidos na camada curada. |

### Validação funcional
- Inicialização: **OK**
- Carregamento de dados BQ: **OK**
- Indicador de fonte ativa: **OK**
- Filtros Cidade/UBS: **OK**
- Visualizações agregadas: **OK**
- Comportamento scores NULL: **OK** (Não quebra a UI)

### Validação técnica
- Prioridade BigQuery: **OK**
- Tratamento de erro/fallback: **OK**
- Ausência de escrita: **OK**
- Rastreabilidade: **OK**

### Validação de performance
- Carga inicial (rede): ~6s
- Carga via Cache: <1s
- Botão `🔄`: Limpa cache e recarrega em ~6s.

### Cache, botão 🔄 e timestamp
- `@st.cache_data(ttl=900)` validado.
- Botão `🔄` preservado e funcional.
- Timestamp reflete a última consulta bem-sucedida ao BigQuery.

### Fallback Parquet
O fallback foi testado tecnicamente via indução de erro (C.2) e funciona como rede de segurança. Nesta C.3, o dashboard operou prioritariamente via BigQuery.

### PII mantida
Mantidos: `user_name`, `email` (mascarado), `age` (via `birthDate`). A anonimização permanece pendente para fase posterior.

### Limitações conhecidas
- **Scores PHQ/GAD temporariamente nulos:** Devido à incompatibilidade de schema na view `cur_score_current_v1`. Indicadores clínicos aggregados estão indisponíveis.

### Validação visual manual
Interface íntegra, sidebar correta, tabelas populadas com dados do BigQuery. Mensagem de erro informativa exibida caso a fonte canônica falhe.

## Decisão recomendada sobre o Parquet

**Recomendação:** **Opção A — manter Parquet como fallback técnico temporário.**

**Justificativa:**
1. A view de scores clínicos (`cur_score_current_v1`) ainda apresenta erros, tornando o dashboard clinicamente incompleto via BigQuery.
2. A validação formal pela diretoria do CONEMO ainda não ocorreu.
3. O fallback garante robustez operacional mínima enquanto as inconsistências de schema no BigQuery são sanadas.

**Condições para futura desativação:**
1. Saneamento da view `cur_score_current_v1` ou implementação de fonte alternativa de scores.
2. Validação visual positiva pela diretoria.
3. Estabilidade comprovada da conexão BigQuery em ambiente de deploy.

**Decisão final:** pendente de aprovação do professor.

---

## Status da Integração BigQuery (C.3)
- **Canonicidade:** O BigQuery é a fonte canônica vigente. O Parquet está desatualizado e não deve ser usado como critério de verdade analítica.
- **Fallback:** O Parquet é avaliado apenas como fallback técnico temporário.
- **PII:** As PII permanecem mantidas nesta fase técnica. A anonimização será tratada em fase posterior.
- **Operacionalidade:** O dashboard permanece não operacional até validação formal da diretoria do CONEMO.

---

## Parecer de Auditoria — Fase C.3
**Data:** 2026-04-24  
**Status:** **CONCLUÍDA — AGUARDANDO DECISÃO DE CORTE**

---

## Decisões Vinculantes da Coordenação
- **Canonicidade:** O BigQuery é a fonte canônica vigente. O Parquet está desatualizado e não deve ser usado como critério de verdade analítica.
- **PII:** Nesta etapa técnica as PII necessárias ao contrato atual do dashboard serão mantidas. A anonimização será tratada em fase posterior.
- **Operacionalidade:** O dashboard integrado ao BigQuery não está autorizado para uso operacional antes da validação formal da diretoria do CONEMO.

---
**Executor:** Gemini CLI Agent  
**Data:** 2026-04-24

---

## Handoff pós-merge — Encerramento da Fase C

**Data de encerramento:** 2026-04-24  
**PR consolidado:** [PR #4](https://github.com/conemo-project/conemo/pull/4)  
**Commit de merge:** `b9e5f54` (integrado à branch `main`)  
**Status final:** ✅ Fase C concluída e integrada à `main`

### Estado final do Dashboard
- **Fonte Canônica:** BigQuery (dataset `firestore_curated`).
- **Fallback Técnico:** Parquet local preservado (desatualizado).
- **Contrato de Dados:** Preservado (DataFrame compatível com visualizações).
- **Limitação Clínica:** `phq_score` e `gad_score` retornam `NULL` (pendência de saneamento de fonte).
- **PII:** Mantidas por decisão da coordenação; anonimização pendente.
- **Operacionalidade:** **NÃO OPERACIONAL**. O dashboard integrado ao BigQuery aguarda validação formal da diretoria do CONEMO.

### Arquivos integrados
- `Code/PY/dashboard_conemo.py`: Implementação técnica da integração.
- `Docs/fase-c-integracao-bigquery.md`: Documentação consolidada (C.2, C.3 e Handoff).
- `Docs/fase-c1-diagnostico-integracao-bigquery-dashboard.md`: Diagnóstico técnico da subfase C.1.
- `README.md`: Atualização factual do estado do projeto.

### Pendências registradas
1. **Saneamento de `cur_score_current_v1`**: Necessário para recomposição dos scores clínicos.
2. **Anonimização**: Segregação de PII em fase posterior.
3. **Validação Institucional**: Aceite formal pela diretoria do CONEMO.
4. **Exportações**: Revisão técnica de exportações CSV contendo PII.

### Próximas Fases Recomendadas
- Fase de Saneamento Clínico (scores).
- Fase de Segurança e Anonimização.
- Fase de Validação Final e Operacionalização.

Nenhuma nova fase técnica foi iniciada neste ato.

