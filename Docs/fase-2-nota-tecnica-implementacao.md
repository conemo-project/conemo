# Fase 2 — Nota técnica de implementação e validação
# Autor: Ricardo Ceneviva
# Data: 2026-04-07
# Branch: fase-2-implementacao-camada-curada-minima


## 1) Status e propósito

- **Status**: implementação concluída — aguardando execução das queries de validação no BigQuery e aprovação formal.
- **Propósito**: documentar as regras de transformação, filtros, exclusões, limites conhecidos e evidências de validação disponíveis da Fase 2.
- **Artefatos produzidos**: 5 views SQL curadas + queries de validação + esta nota técnica.
- **Ressalva herdada da Fase 1**: o contrato lógico mínimo não deve ser tratado como modelo completo do SGBD.
- **Ressalva herdada da Fase 0**: divergência entre workspace canônico e clone institucional permanece registrada.

---

## 2) Ambiente de destino

| Parâmetro | Valor |
|---|---|
| Project | `conemo-412202` |
| Dataset de origem (bruto) | `firestore_export` |
| Dataset de destino (curado) | `firestore_curated` (a criar no BigQuery antes da execução) |
| Tipo de objeto | `CREATE OR REPLACE VIEW` |

**Observação**: as views são instruções SQL prontas para execução. O dataset `firestore_curated` deve ser criado manualmente no BigQuery antes da primeira execução, se ainda não existir.

---

## 3) Artefatos SQL produzidos

| Arquivo | Entidade de destino | Granularidade |
|---|---|---|
| `sql/fase2_cur_participant_current_v1.sql` | `cur_participant_current_v1` | 1 linha por participante |
| `sql/fase2_cur_health_unit_v1.sql` | `cur_health_unit_v1` | 1 linha por UBS |
| `sql/fase2_cur_journey_current_v1.sql` | `cur_journey_current_v1` | 1 linha por participante × jornada |
| `sql/fase2_cur_session_current_v1.sql` | `cur_session_current_v1` | 1 linha por participante × jornada × sessão |
| `sql/fase2_cur_score_current_v1.sql` | `cur_score_current_v1` | 1 linha por participante × score_type × data |
| `sql/fase2_validacao_contagens.sql` | Todas as views | Queries de auditoria e contagem |

---

## 4) Regras de transformação aplicadas

### 4.1 Identificação de participantes (entidade `cur_participant_current_v1`)

| Regra | Descrição |
|---|---|
| `participant_master_id` | = `users_raw_latest.document_id`. Único identificador disponível nesta v1 (D1). |
| `id_reconciliation_status` | `RESOLVED_DOCUMENT` em todos os registros v1. Hierarquia superior (respondent_id) pendente de decisão formal (D1). |
| `source_respondent_id` | `NULL` — campo ausente da fonte física (D1 — ver Docs/fase-2-verificacao-tecnica-bigquery.md). |
| Filtragem de nulos | `document_id IS NOT NULL AND TRIM(document_id) != ''` — filtro mínimo de qualidade. |
| Deduplicação | `users_raw_latest` é tratada como tendo 1 linha por `document_id`. Verificação via V1.1. |

### 4.2 Normalização de gênero

| Valor físico | Valor curado |
|---|---|
| `"F"` | `FEMININO` |
| `"M"` | `MASCULINO` |
| `NULL`, `""`, `"N/A"` | `NAO_INFORMADO` |
| Outros | `OUTRO` |

### 4.3 Normalização de risco

| Valor físico | Valor curado |
|---|---|
| `"BAIXO"`, `"LOW"`, `"B"` | `BAIXO` |
| `"MODERADO"`, `"MODERATE"`, `"M"`, `"MED"` | `MODERADO` |
| `"ALTO"`, `"HIGH"`, `"A"`, `"H"` | `ALTO` |
| `NULL`, `""`, `"N/A"` | `NAO_CLASSIFICADO` |

**Nota**: mapeamentos baseados em valores observados no CSV. Valores físicos adicionais podem exigir extensão do CASE.

### 4.4 Exclusão de registros de teste

Registros de teste são identificados por `organization.city` no JSON de `users_raw_latest`.

**Cidades excluídas (v1)**: `FAKE CITY`, `TEST`, `TESTE`, `TESTCITY`, `TESTE CITY`.

Registros com `organization.city = NULL` ou vazio são **preservados** como `WARN` (podem ser registros legítimos com dado incompleto).

### 4.5 Normalização de tipo de jornada

| Valor físico | Valor curado |
|---|---|
| `"GAD"`, `"ANXIETY"` | `ANXIETY` |
| `"PHQ"`, `"DEPRESSION"`, `"DEPRESSAO"`, `"DEPRESSÃO"` | `DEPRESSION` |
| `NULL` ou `""` | `UNKNOWN` |
| Outros | Valor físico preservado (transparência) |

### 4.6 Normalização de status de jornada

Derivado de `DATA.$.enabled` (STRING):

| Valor físico | Valor curado |
|---|---|
| `"true"` | `ACTIVE` |
| `"false"` | `INACTIVE` |
| Outros/NULL | `UNKNOWN` |

### 4.7 Booleanização de `isCompleted` (sessões)

Valor físico: STRING `"true"`/`"false"`. Default conservativo: `FALSE` quando ausente.

### 4.8 Derivação de `session_status`

| Condição | Valor derivado |
|---|---|
| `is_completed = TRUE` | `COMPLETED` |
| `session_number IS NULL` | `UNKNOWN` |
| `session_number = 1 AND is_completed = FALSE` | `NOT_STARTED` |
| Demais casos | `IN_PROGRESS` |

### 4.9 `health_unit_key` (N4 — localização corrigida)

**Fonte real**: `DATA.$.organization.id` (não `path_params` como indicado no contrato Fase 1).
- Valor ausente → `UNK_UHS`.
- Integração com `cur_health_unit_v1` via `health_unit_key`.

### 4.10 Escores (`cur_score_current_v1`) — duas fontes

| Fonte | score_type | score_source | Natureza |
|---|---|---|---|
| `users_raw_latest.DATA.$.forms[0].scores[]` | `PHQ`, `GAD` | `FORM_INITIAL` | Escore de triagem inicial (T0) |
| `journeys_raw_latest.DATA.$.score` | `PHQ_JOURNEY`, `GAD_JOURNEY`, `OTHER_JOURNEY` | `JOURNEY_AGGREGATE` | Score de progresso operacional |

**Aviso de interpretação**: PHQ/GAD de `FORM_INITIAL` e `*_JOURNEY` não devem ser comparados diretamente sem contextualização analítica.

---

## 5) Tratamento de missingness

| Campo | Tratamento quando ausente |
|---|---|
| `participant_master_id` | Registro excluído (filtro WHERE) |
| `source_respondent_id` | `NULL` com status D1 documentado |
| `gender` | `NAO_INFORMADO` |
| `risk` | `NAO_CLASSIFICADO` |
| `health_unit_key` | `UNK_UHS` |
| `is_test_record` | `NULL` preservado (incerteza, não exclusão) |
| `journey_type` | `UNKNOWN` |
| `journey_status` | `UNKNOWN` |
| `session_number` | `NULL` — session_status = UNKNOWN |
| `is_completed` | Default `FALSE` (conservativo) |
| `event_timestamp` (sessões) | `NULL` — campo não implementado nesta v1 (N7) |
| `journey_updated_at` | `NULL` quando `lastAccess._seconds` ausente |
| `score_value` | Registro excluído da união de escores |
| `score_reference_date` | `score_quality_flag = WARN` |

---

## 6) Separação de domínios: identificável × clínico × operacional

### 6.1 Domínio identificável (PII) — **excluído da camada curada**

Campos presentes em `users_raw_latest` mas intencionalmente omitidos:
- `$.name` — nome completo
- `$.email` — e-mail
- `$.cpf` — CPF
- `$.birthDate` — data de nascimento
- `$.termsOfConsentDate` — data de aceite de termos

### 6.2 Domínio clínico — **na camada curada com restrições**

Campos analíticos com conteúdo clínico:
- `gender`, `risk` — atributos demográficos e de risco analítico
- `score_type`, `score_value` — escores PHQ e GAD de triagem
- `journey_type`, `journey_status` — tipo e estado da jornada terapêutica
- `is_completed`, `session_status` — adesão terapêutica

**Acesso**: restrito a perfis clínicos e de pesquisa conforme regras do SGBD (Fase futura).

### 6.3 Domínio operacional — **na camada curada para todos os perfis autorizados**

Campos operacionais sem conteúdo identificável ou clínico sensível:
- `participant_master_id`, `health_unit_key`, `id_reconciliation_status`
- `record_quality_flag`, `score_quality_flag`
- `ubs_name`, `ubs_city`, `health_unit_status`
- `journey_id`, `session_number`, `session_name`

---

## 7) Limites conhecidos desta implementação v1

| Limite | Descrição | Decisão necessária |
|---|---|---|
| D1 — `respondent_id` ausente | Tier superior da hierarquia de reconciliação não implementado. Todos os registros com `RESOLVED_DOCUMENT`. | Decisão sobre incorporação de `respondent_id` em exportações futuras |
| D2 — `userId` = `document_id` | Confirmado na prática. `source_user_id = DATA.$.id`. Sem impacto funcional. | Confirmação formal de invariância |
| N7 — `event_timestamp` nulo | Timestamp de evento de sessão não implementado. `event_timestamp = NULL` nesta v1. | Identificação da fonte de timestamp de início de sessão |
| gender único | Mapeamento baseado em "F"/"M" observados. Outros valores caem em OUTRO. | Levantamento de todos os valores reais no ambiente de produção |
| Normalização v1 de UBS | Apenas trim + uppercase + INITCAP. Sem dicionário de equivalências de abreviações. | Levantamento de variantes e construção de dicionário |
| `completedDate` não parseado | Campo existe em sessions mas formato STRING não confirmado. Não utilizado nesta v1. | Confirmação de formato e incorporação futura |
| Escopo limitado de scores | Apenas `forms[0]` (primeiro formulário). Reassessments e follow-ups não incluídos. | Decisão sobre escopo de scores em versão futura |
| Arquivo de validação pendente | `fase2_validacao_contagens.sql` está pronto mas resultados ainda não executados no BigQuery. | Execução manual das queries e registro dos resultados |

---

## 8) Queries de validação disponíveis (`sql/fase2_validacao_contagens.sql`)

O arquivo de validação contém 7 blocos de queries prontos para execução:

| Bloco | Conteúdo |
|---|---|
| 1 (V1.1–V1.6) | Contagem e distribuição de `cur_participant_current_v1` |
| 2 (V2.1–V2.2) | Auditoria de `cur_health_unit_v1` |
| 3 (V3.1–V3.4) | Distribuição e integridade de `cur_journey_current_v1` |
| 4 (V4.1–V4.3) | Sessões: contagem, status e progresso |
| 5 (V5.1–V5.2) | Escores: distribuição, qualidade e faixas |
| 6 (V6.1–V6.3) | Integridade referencial entre entidades |
| 7 (V7.1–V7.2) | Comparação bruto × curado e diagnóstico de exclusão de teste |

**Status de execução**: pendente de execução manual no BigQuery após criação do dataset `firestore_curated` e deploy das views.

---

## 9) Pendências formais da Fase 2

| Pendência | Tipo | Ação necessária |
|---|---|---|
| Execução das queries de validação | Técnica | Executar `fase2_validacao_contagens.sql` no BigQuery e registrar resultados |
| Decisão sobre D1 (`respondent_id`) | Governança | Decisão formal do professor sobre incorporação futura ou simplificação do contrato |
| Confirmação D2 (`userId = document_id`) | Técnica | Confirmação de invariância em todo o dataset de produção |
| Deploy do dataset `firestore_curated` | Operacional | Criação do dataset no BigQuery antes da execução das views |
| Confirmação N7 (`event_timestamp`) | Técnica | Identificação e validação do campo de timestamp de início de sessão |
| Normalização de UBS (dicionário) | Operacional | Levantamento e mapeamento de variantes ortográficas |

---

## 10) Registro de rastreabilidade

- **Branch**: `fase-2-implementacao-camada-curada-minima`
- **Commits desta fase**:
  - `6a121f9` — docs(fase-2): verificação técnica controlada (etapa 2.1)
  - `12975d6` — sql(fase-2): 5 views curadas mínimas v1 (etapa 2.2)
  - (commit desta nota técnica)
- **Fontes primárias utilizadas**: 3 tabelas BigQuery; 3 scripts Python existentes; CSV consolidado (8.940 linhas)
- **Contrato lógico de referência**: `Docs/fase-1-contrato-minimo-camada-compartilhada.md`
- **Verificação técnica de referência**: `Docs/fase-2-verificacao-tecnica-bigquery.md`
- **Próximo passo**: execução das queries de validação + aprovação formal da Fase 2
