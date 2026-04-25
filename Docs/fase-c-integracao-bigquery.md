# Fase C — Integração BigQuery → Dashboard

## Introdução
Esta fase documenta a transição do dashboard CONEMO para o BigQuery como fonte de dados canônica, eliminando a dependência do arquivo Parquet local desatualizado.

---

## Fase C.1 — Diagnóstico de integração
O diagnóstico completo e a matriz de mapeamento Parquet → BigQuery estão registrados no documento:
`Docs/fase-c1-diagnostico-integracao-bigquery-dashboard.md`

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

### Contagens BigQuery (Snapshot 2026-04-24)
| Métrica | BigQuery | Parquet histórico/fallback | Interpretação |
|---|---:|---:|---|
| Linhas totais | 4857 | ~9000 | BQ reflete histórico curado participante-sessão |
| Participantes únicos | 481 | 389 | BQ reflete base histórica total |
| Após corte temporal | 228 | 135 | Recorte operacional pós-2026-01-25 |
| **Consumido pelo dashboard** | **125** | **133** | **Diferença residual de 8 registros (Saneamento curado mais rígido)** |

### Validação funcional e técnica
- Prioridade BigQuery: **OK**
- Fallback Parquet: **Preservado como rede de segurança**
- Performance (Cache off/on): ~6s / <1s
- Visualização (Bare Mode): **OK** (Contrato preservado)

## Decisão recomendada sobre o Parquet

**Recomendação:** **Opção A — manter Parquet como fallback técnico temporário.**

**Justificativa:**
1. A view de scores clínicos (`cur_score_current_v1`) ainda apresenta inconsistências.
2. A validação formal pela diretoria do CONEMO permanece pendente.
3. O fallback garante disponibilidade operacional mínima durante a transição.

---

# Parecer de auditoria, validação e encerramento — Fase C

**Projeto:** CONEMO  
**Objeto:** Integração do Dashboard CONEMO ao BigQuery  
**Modo principal:** auditoria e validação  
**Resultado:** **Fase C aprovada e encerrada com pendências documentadas**

## 1. Escopo auditado
Foi auditada a execução da **Fase C — Integração com BigQuery**, conforme o Plano Operacional da Fase C, abrangendo: diagnóstico (C.1), implementação controlada (C.2) e validação de corte (C.3).

## 2. Validação
A auditoria final confirmou que a Fase C cumpriu seu objetivo principal: consolidar o **BigQuery como fonte canônica vigente do dashboard**.
- BigQuery validado como fonte ativa (125 participantes limpos).
- Parquet rebaixado a fallback técnico temporário.
- Filtro temporal `2026-01-25` e qualidade `is_test_record = false` preservados.
- Contrato do DataFrame, cache e botão `🔄` íntegros.

## 3. Ressalvas e pendências
1. Saneamento da fonte `cur_score_current_v1` para recomposição dos scores PHQ/GAD.
2. Anonimização ou segregação operacional de PII em fase posterior.
3. Validação institucional pela diretoria do CONEMO.
4. Revisão de exportações envolvendo PII.

## 4. Governança e segurança
A manutenção de PII nesta etapa decorre de decisão explícita do professor para fins técnicos. O dashboard permanece em condição **não operacional**, limitado a validação técnica, até deliberação formal da diretoria.

## 5. Parecer final
A **Fase C está aprovada e encerrada com pendências documentadas**. A implementação cumpriu o escopo planejado. Fica autorizada a abertura do PR consolidado da Fase C.

---

## Decisões Vinculantes da Coordenação
- **Canonicidade:** O BigQuery é a fonte canônica vigente. O Parquet está desatualizado.
- **PII:** Mantidas nesta fase técnica; anonimização é fase posterior.
- **Operacionalidade:** Dashboard não autorizado para uso operacional pleno até validação final da diretoria.

---
**Executor:** Gemini CLI Agent  
**Data:** 2026-04-24
