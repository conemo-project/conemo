# Fase 2 — Etapa 2.1: Verificação técnica controlada de aderência física no BigQuery
# Autor: Ricardo Ceneviva
# Data: 2026-04-07
# Branch: fase-2-implementacao-camada-curada-minima


## 1) Status e propósito

- **Status**: verificação concluída — aderência **parcial** com divergências documentadas.
- **Etapa**: 2.1 (pré-implementação obrigatória).
- **Propósito**: confirmar aderência entre o contrato lógico aprovado na Fase 1 e a estrutura física real do BigQuery antes de qualquer implementação SQL.
- **Caráter**: confirmatório e documental. Não autoriza alteração silenciosa do contrato lógico.

---

## 2) Fontes canônicas utilizadas nesta etapa

1. `Docs/RULES.md` — lido integralmente.
2. `Docs/Workflow-Projeto.md` — lido integralmente.
3. `Docs/fase-1-contrato-minimo-camada-compartilhada.md` — contrato lógico de referência.
4. `Docs/fase-camada-sql-compartilhada-bigquery-sgbd.md` — Fase 0 aprovada.
5. `Code/PY/teste_02_bigquery.py` — queries reais ao BigQuery (fonte primária de nomes físicos).
6. `Code/PY/users_dataframe_analise_exploratoria.py` — queries e parse de campos JSON.
7. `Code/PY/proj_conemo_relatório_dash_27_03_2026.py` — queries das três tabelas brutas.
8. `Data/CSV/conemo_dados_consolidados_raw.csv` — export consolidado do BigQuery (inspeção de schema e JSON).

---

## 3) Inventário das fontes físicas verificadas no BigQuery

### 3.1 Ambiente BigQuery

| Parâmetro | Valor confirmado |
|---|---|
| Project ID | `conemo-412202` |
| Dataset (fontes brutas) | `firestore_export` |
| Dataset proposto para curadoria | `firestore_curated` (a criar) |

### 3.2 Tabelas brutas disponíveis

| Tabela física | Papel no projeto | Status de verificação |
|---|---|---|
| `conemo-412202.firestore_export.users_raw_latest` | Participantes, perfil, organização, formulários, escores | ✅ Confirmada — código e CSV |
| `conemo-412202.firestore_export.sessions_raw_latest` | Sessões por participante × jornada | ✅ Confirmada — código e CSV |
| `conemo-412202.firestore_export.journeys_raw_latest` | Jornadas por participante | ✅ Confirmada — código e CSV |

Observação: o código de consulta utiliza a referência completa `conemo-412202.firestore_export.<tabela>`, confirmando project e dataset.

---

## 4) Inventário dos campos físicos relevantes

### 4.1 `users_raw_latest`

#### Colunas físicas de nível superior (BigQuery)

| Coluna física | Tipo observado | Observação |
|---|---|---|
| `document_name` | STRING | Caminho completo Firestore: `projects/.../users/{id}` |
| `document_id` | STRING | ID único do documento no Firestore = UID do usuário |
| `path_params` | STRING (JSON) | Vazio (`{}`) para a coleção raiz de usuários |
| `DATA` | STRING (JSON) | Coluna principal — alias `json_data` nos scripts |

#### Campos dentro de `DATA` (JSON) — verificados via CSV e código

| Caminho JSON | Tipo observado | Conteúdo / Exemplos |
|---|---|---|
| `$.id` | STRING | Mesmo valor de `document_id` |
| `$.name` | STRING | Nome completo — **PII** |
| `$.email` | STRING | E-mail — **PII** |
| `$.cpf` | STRING | CPF — **PII** |
| `$.gender` | STRING | Valores: `"F"`, `"M"` (letras únicas) |
| `$.risk` | STRING | Nível de risco operacional |
| `$.group` | STRING | Grupo de intervenção |
| `$.source` | STRING | Origem do cadastro |
| `$.createdAt._seconds` | INT64 | Timestamp de criação (Unix seconds) |
| `$.updatedAt._seconds` | INT64 | Timestamp de atualização |
| `$.birthDate._seconds` | INT64 | Data de nascimento — **PII** |
| `$.termsOfConsent` | BOOLEAN | Aceite de termos |
| `$.termsOfConsentDate` | OBJECT | Timestamp do aceite |
| `$.organization.id` | STRING | ID da UBS |
| `$.organization.name` | STRING | Nome da UBS |
| `$.organization.city` | STRING | Cidade da UBS |
| `$.forms[0].date._seconds` | INT64 | Timestamp do primeiro formulário |
| `$.forms[0].scores[].type` | STRING | Tipo de escore: `"PHQ"`, `"GAD"` |
| `$.forms[0].scores[].score` | STRING/NUMBER | Valor do escore |

**Nota sobre `userId`**: NÃO existe como coluna top-level em `users_raw_latest`. O identificador do usuário é `document_id` e `$.id` (mesmo valor). O campo `user_id` aparece no CSV consolidado como alias de `document_id`. Ver Divergência D2.

**Nota sobre `respondent_id`**: NÃO existe como coluna top-level nem como chave JSON em `users_raw_latest`. Ver Divergência D1.

---

### 4.2 `sessions_raw_latest`

#### Colunas físicas de nível superior

| Coluna física | Tipo observado | Observação |
|---|---|---|
| `document_name` | STRING | Caminho completo Firestore |
| `document_id` | STRING | ID da sessão |
| `path_params` | STRING (JSON) | `{"userId": "...", "journeyId": "GAD"/"DEPRESSION"}` |
| `DATA` | STRING (JSON) | Alias `json_data_session` no CSV |

#### Campos dentro de `DATA` (JSON)

| Caminho JSON | Tipo observado | Conteúdo / Exemplos |
|---|---|---|
| `$.sessionNumber` | STRING | Número da sessão (requer SAFE_CAST para INT64) |
| `$.isCompleted` | STRING | Valores: `"true"`, `"false"` |
| `$.name` | STRING | Nome/título da sessão |
| `$.daily` | OBJECT | Estrutura diária da sessão |
| `$.steps` | ARRAY | Passos dentro da sessão |

#### Campos de `path_params` (vínculo de join)

| Chave JSON | Tipo observado | Uso |
|---|---|---|
| `$.userId` | STRING | Vínculo com `users_raw_latest.document_id` |
| `$.journeyId` | STRING | Vínculo com `journeys_raw_latest.document_id` |

---

### 4.3 `journeys_raw_latest`

#### Colunas físicas de nível superior

| Coluna física | Tipo observado | Observação |
|---|---|---|
| `document_name` | STRING | Caminho completo Firestore |
| `document_id` | STRING | ID da jornada (ex: `"GAD"`, `"DEPRESSION"`) |
| `path_params` | STRING (JSON) | `{"userId": "..."}` |
| `DATA` | STRING (JSON) | Alias `json_data_journey` no CSV |

#### Campos dentro de `DATA` (JSON)

| Caminho JSON | Tipo observado | Conteúdo / Exemplos |
|---|---|---|
| `$.type` | STRING | Tipo da jornada: `"GAD"`, `"DEPRESSION"` |
| `$.enabled` | STRING | `"true"` / `"false"` |
| `$.lastSession` | STRING/INT | Número da última sessão acessada |
| `$.lastAccess._seconds` | INT64 | Timestamp do último acesso |
| `$.score` | NUMBER | Escore agregado da jornada |

#### Campos de `path_params`

| Chave JSON | Uso |
|---|---|
| `$.userId` | Vínculo com `users_raw_latest.document_id` |

---

## 5) Tabela de correspondência: nomes lógicos × nomes físicos

### 5.1 `cur_participant_current_v1`

| Campo lógico (Fase 1) | Fonte física (BigQuery) | Status |
|---|---|---|
| `participant_master_id` | `users_raw_latest.document_id` | ✅ Confirmado (ver D2) |
| `source_document_id` | `users_raw_latest.document_id` | ✅ Confirmado |
| `source_user_id` | `users_raw_latest.DATA.$.id` (= document_id) | ✅ Confirmado — nominal (ver D2) |
| `source_respondent_id` | **AUSENTE** na fonte física | ❌ Divergência D1 |
| `id_reconciliation_status` | Derivado | ✅ Derivado (valor: RESOLVED_DOCUMENT) |
| `gender` | `users_raw_latest.DATA.$.gender` | ✅ Confirmado — normalização necessária (`"F"` → `"FEMININO"`) |
| `risk` | `users_raw_latest.DATA.$.risk` | ✅ Confirmado — normalização necessária |
| `health_unit_key` | `users_raw_latest.DATA.$.organization.id` | ⚠️ Nota N4 — localização difere do contrato |
| `is_test_record` | Derivado via `$.organization.city` | ✅ Derivado |
| `record_quality_flag` | Derivado | ✅ Derivado |

### 5.2 `cur_health_unit_v1`

| Campo lógico (Fase 1) | Fonte física (BigQuery) | Status |
|---|---|---|
| `health_unit_key` | `users_raw_latest.DATA.$.organization.id` | ⚠️ Nota N4 |
| `ubs_name` | `users_raw_latest.DATA.$.organization.name` | ✅ Confirmado |
| `ubs_city` | `users_raw_latest.DATA.$.organization.city` | ✅ Confirmado |
| `health_unit_status` | Derivado | ✅ Derivado |

### 5.3 `cur_journey_current_v1`

| Campo lógico (Fase 1) | Fonte física (BigQuery) | Status |
|---|---|---|
| `participant_master_id` | `journeys_raw_latest.path_params.$.userId` | ✅ Confirmado |
| `journey_id` | `journeys_raw_latest.document_id` | ✅ Confirmado |
| `journey_type` | `journeys_raw_latest.DATA.$.type` | ✅ Confirmado — normalização necessária |
| `journey_status` | Derivado de `DATA.$.enabled` | ✅ Confirmado — normalização necessária |
| `journey_updated_at` | `journeys_raw_latest.DATA.$.lastAccess._seconds` | ⚠️ Nota N2 |

### 5.4 `cur_session_current_v1`

| Campo lógico (Fase 1) | Fonte física (BigQuery) | Status |
|---|---|---|
| `participant_master_id` | `sessions_raw_latest.path_params.$.userId` | ✅ Confirmado |
| `journey_id` | `sessions_raw_latest.path_params.$.journeyId` | ✅ Confirmado |
| `session_number` | `sessions_raw_latest.DATA.$.sessionNumber` | ✅ Confirmado — requer SAFE_CAST INT64 |
| `is_completed` | `sessions_raw_latest.DATA.$.isCompleted` | ✅ Confirmado — requer booleanização |
| `session_status` | Derivado | ✅ Derivado |
| `event_timestamp` | Não confirmado explicitamente em sessions | ⚠️ Nota N7 |

### 5.5 `cur_score_current_v1`

| Campo lógico (Fase 1) | Fonte física (BigQuery) | Status |
|---|---|---|
| `participant_master_id` | `users_raw_latest.document_id` (forms) / `path_params.$.userId` (journeys) | ✅ Confirmado |
| `score_type` | `users_raw_latest.DATA.$.forms[0].scores[].type` / `journeys_raw_latest.DATA.$.type` | ✅ Confirmado |
| `score_value` | `users_raw_latest.DATA.$.forms[0].scores[].score` / `journeys_raw_latest.DATA.$.score` | ✅ Confirmado |
| `score_reference_date` | `users_raw_latest.DATA.$.forms[0].date._seconds` / `journeys_raw_latest.DATA.$.lastAccess._seconds` | ✅ Confirmado (via timestamp) |
| `score_quality_flag` | Derivado | ✅ Derivado |

---

## 6) Divergências encontradas

### D1 — `respondent_id` ausente na fonte física

| Atributo | Descrição |
|---|---|
| **Elemento divergente** | Campo `respondent_id` / `source_respondent_id` |
| **Definido no contrato lógico (Fase 1)** | `source_respondent_id` de `users_raw_latest.respondent_id`; tier 1 da hierarquia de reconciliação |
| **Situação física** | Campo `respondent_id` **não existe** em `users_raw_latest` — nem como coluna top-level nem como chave JSON em `DATA` |
| **Fonte da verificação** | Inspeção dos campos JSON via CSV export (8.940 registros) e código de queries existente |
| **Tipo de divergência** | **Estrutural — campo ausente da fonte** |
| **Impacto sobre a implementação** | O tier 1 da hierarquia de reconciliação não pode ser implementado como definido. A hierarquia `respondent_id > userId > document_id` torna-se `document_id` apenas, nesta implementação |
| **Decisão da implementação** | Ponto interrompido conforme cláusula de governança. `source_respondent_id = NULL` com `missing_code = NULL_TECH` na view implementada. Atualização do contrato lógico depende de decisão formal |
| **Ação necessária** | Decisão formal do professor/revisor sobre: (a) incorporar `respondent_id` em exportação futura; ou (b) simplificar a hierarquia para `document_id` como chave única |

---

### D2 — `userId` não é coluna top-level em `users_raw_latest`

| Atributo | Descrição |
|---|---|
| **Elemento divergente** | Referência a `users_raw_latest.userId` no contrato lógico |
| **Definido no contrato lógico (Fase 1)** | `source_user_id` de `users_raw_latest.userId` |
| **Situação física** | Não existe coluna `userId` em `users_raw_latest`. O identificador do usuário é `document_id` (= `$.id` dentro de `DATA`) |
| **Tipo de divergência** | **Nominal/Estrutural — conceito mapeado em campo diferente** |
| **Impacto sobre a implementação** | `source_user_id = JSON_VALUE(DATA, '$.id')` (idêntico a `document_id`) — sem perda de informação |
| **Decisão da implementação** | Resolvido na implementação. `source_user_id` deriva de `DATA.$.id`. Sem impacto funcional, pois `document_id = $.id` em todos os registros verificados |
| **Ação necessária** | Confirmação formal que `document_id = $.id` é invariante. Sem bloqueio de implementação |

---

## 7) Notas de aderência (não-bloqueantes)

### N1 — Nome da coluna JSON (`DATA` em maiúscula)
- **Descrição**: BigQuery usa `DATA` (maiúscula) como nome da coluna. Aliases nos scripts existentes: `json_data`, `json_data_user`, etc.
- **Tipo**: Nominal.
- **Impacto**: Nenhum — aliasing via `DATA AS json_data` já praticado em todos os scripts.

### N2 — `journey_updated_at` → `lastAccess._seconds`
- **Descrição**: O contrato define `journey_updated_at` como "última atualização conhecida da jornada". O campo físico é `DATA.$.lastAccess._seconds`. Não há campo `updatedAt` explícito em journeys.
- **Tipo**: Nominal — conceito mapeado em campo diferente.
- **Resolução na implementação**: `journey_updated_at = TIMESTAMP_SECONDS(SAFE_CAST(JSON_VALUE(DATA, '$.lastAccess._seconds') AS INT64))`.

### N3 — `path_params` é STRING JSON, não coluna estruturada
- **Descrição**: `path_params` é uma STRING contendo JSON (ex: `{"userId":"...", "journeyId":"..."}`). Requer `JSON_VALUE(path_params, '$.userId')` para extração.
- **Tipo**: Estrutural menor — já conhecido e tratado nos scripts existentes.
- **Impacto**: Nenhum — tratado normalmente via `JSON_VALUE`.

### N4 — `health_unit_key` vem de `organization.id`, não de `path_params`
- **Descrição**: O contrato Fase 1 menciona `health_unit_key` de `users_raw_latest.data.path_params`. Fisicamente, o ID da organização está em `DATA.$.organization.id`, não em `path_params` (que é vazio para usuários).
- **Tipo**: Estrutural menor — campo existe mas em localização diferente da mencionada no contrato.
- **Resolução na implementação**: `health_unit_key = JSON_VALUE(DATA, '$.organization.id')`.

### N5 — Escore de jornada vs. escores de formulário
- **Descrição**: `journeys_raw_latest.DATA.$.score` é um valor agregado da jornada (distinto dos escores PHQ/GAD em `users_raw_latest.forms[0].scores`). São métricas diferentes.
- **Tipo**: Estrutural — distinção de conceito.
- **Resolução na implementação**: ambos incluídos em `cur_score_current_v1` com `score_type` explícito para distingui-los (`PHQ`, `GAD` vs. `PHQ_JOURNEY`, `GAD_JOURNEY`).

### N6 — Valores de gênero em código de letra única
- **Descrição**: `$.gender` contém `"F"`, `"M"` (não `"Feminino"`, `"Masculino"`).
- **Tipo**: Nominal — normalização prevista e implementada.
- **Resolução na implementação**: mapeamento explícito `F → FEMININO`, `M → MASCULINO`.

### N7 — `event_timestamp` em sessões não confirmado
- **Descrição**: O contrato define `event_timestamp` em `cur_session_current_v1` como "tempo de referência da sessão". O campo `DATA.$.completedDate` existe no CSV (`completedDate`), mas é uma STRING que requer parse. Não há timestamp de evento de início de sessão confirmado.
- **Tipo**: Estrutural — campo existe mas não uniforme.
- **Resolução na implementação v1**: `event_timestamp` derivado de `completedDate` quando disponível. Marcado como `NULL_TECH` quando ausente. Campo incluído como opcional na view v1.

---

## 8) Conclusão da verificação técnica

### Diagnóstico de aderência

| Dimensão | Status |
|---|---|
| Fontes físicas verificadas | ✅ 3 tabelas confirmadas em `conemo-412202.firestore_export` |
| Campos físicos principais | ✅ Confirmados via código de produção e CSV export |
| Aderência do contrato lógico | **PARCIAL** |
| Divergências materiais | **1 (D1)** — `respondent_id` ausente |
| Divergências nominais/menores | **1 (D2)** + 5 notas (N1–N7) |
| Bloqueio de implementação total | **NÃO** |
| Bloqueio de ponto específico | **SIM** — tier `respondent_id` da hierarquia de chaves |

### Decisão sobre continuidade

A verificação identificou **aderência parcial**:
- A grande maioria dos campos e entidades está confirmada e pode ser implementada.
- **D1 bloqueia especificamente o tier `respondent_id`** da hierarquia de reconciliação. A implementação v1 adota `document_id` como identificador único, registrando `source_respondent_id = NULL` e `id_reconciliation_status = 'RESOLVED_DOCUMENT'` em todos os registros.
- **D2 é resolvida internamente**: `source_user_id = DATA.$.id = document_id`.
- As demais notas (N1–N7) são tratadas na implementação sem impacto funcional material.

A implementação da camada curada mínima (Etapa 2.2) prossegue com as seguintes condições documentadas:

1. **D1 permanece aberta**: `source_respondent_id` não implementado na fonte física. Registro de pendência formal exigido. Nenhuma alteração silenciosa do contrato lógico.
2. **Contrato lógico v1 preservado**: a arquitetura de 5 entidades, a segregação PII/analítica e os domínios canônicos são preservados integralmente.
3. **Ressalva herdada da Fase 1 preservada**: o contrato mínimo não deve ser tratado como modelo completo do SGBD.
4. **Ressalva herdada da Fase 0 preservada**: divergência entre workspace canônico e clone institucional permanece registrada sem resolução nesta fase.

---

## 9) Produtos desta etapa

- [x] Inventário das fontes físicas verificadas (seção 3).
- [x] Inventário dos campos físicos relevantes (seção 4).
- [x] Tabela de correspondência nomes lógicos × físicos (seção 5).
- [x] Lista de divergências com diagnóstico completo (seção 6).
- [x] Notas de aderência não-bloqueantes (seção 7).
- [x] Conclusão formal de aderência (seção 8).
- [x] Autorização documentada para continuidade à Etapa 2.2 com ressalvas.

---

## 10) Registro de rastreabilidade

- **Branch**: `fase-2-implementacao-camada-curada-minima`
- **Data**: 2026-04-07
- **Fontes inspecionadas**: 3 tabelas BigQuery; código Python existente; 8.940 registros no CSV consolidado
- **Divergências materiais**: D1 (bloqueio parcial) documentada e não resolvida silenciosamente
- **Próximo passo**: Etapa 2.2 — Implementação SQL das 5 entidades curadas mínimas v1
