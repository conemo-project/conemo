# Correção controlada — Publicação das views curadas da Fase 2 no BigQuery

**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-08  
**Projeto:** CONEMO  
**Repositório:** `conemo-project/conemo` (clone institucional)  
**Branch desta etapa:** `fase-correcao-publicacao-views-curadas`  
**Modo principal:** Integração de fontes → auditoria e reconciliação → validação técnica → documentação técnica/handoff

---

## 1. Objetivo desta execução

Remover o bloqueio técnico específico que impedia a retomada da validação da Fase 3.2: a ausência operacional das views curadas `cur_*` no BigQuery do projeto `conemo-412202`.

Este bloqueio foi registrado formalmente na auditoria da Fase 3.2, que concluiu que os scripts SQL das marts estavam corretos conceitualmente, mas a ausência das views de que dependem tornava impossível qualquer execução ou dry-run real.

**Esta execução não representa reabertura da Fase 2 nem retomada da Fase 3.2.** É uma correção controlada de infraestrutura/integração, com escopo restrito e documentado.

---

## 2. Estado validado antes desta execução

Os seguintes pontos foram considerados vinculantes antes do início:

1. Dataset `firestore_curated` já existia em `conemo-412202` (criado na Etapa 1 preparatória).
2. Localização `southamerica-east1` compatível com `firestore_export` (confirmada na Etapa 2).
3. Etapa 2 (checkpoint operacional final) aprovada formalmente.
4. Fase 3.2 auditada como **não concluída** — bloqueio: ausência das views `cur_*` no BigQuery.
5. A Fase 3.3 **não está autorizada**.
6. A Fase 4 **não está autorizada**.

---

## 3. Fontes obrigatórias lidas antes da execução

### 3.1 Canônicas
1. `Docs/RULES.md` (workspace canônico)
2. `Docs/Workflow-Projeto.md` (workspace canônico)
3. `Docs/Plano-implementacao-dashboard.md`
4. Plano Operacional de Pré-processamento de Dados aprovado (referenciado em Fase 0/Fase 1)

### 3.2 Base de fases anteriores
1. `Docs/fase-camada-sql-compartilhada-bigquery-sgbd.md` (Fase 0)
2. `Docs/fase-1-contrato-minimo-camada-compartilhada.md` (Fase 1)
3. `Docs/fase-2-verificacao-tecnica-bigquery.md` (Fase 2)
4. `Docs/fase-2-nota-tecnica-implementacao.md` (Fase 2)

### 3.3 Base da Fase 3
1. `Docs/fase-3-limites-herdados.md`
2. `Docs/fase-3-nota-decisoria-dataset-destino-2026-04-07.md`
3. `Docs/fase-3-preparacao-dataset-destino.md`
4. `Docs/fase-3-checkpoint-operacional-dataset-destino.md`
5. `Docs/fase-3-parecer-auditoria-2026-04-07.md`
6. `Docs/fase-3-parecer-auditoria-etapa-2-2026-04-07.md`
7. `Docs/fase-3-relatorio-conclusao.md`

### 3.4 Scripts SQL da Fase 2 (revisados antes da publicação)
1. `sql/fase2_cur_participant_current_v1.sql` — entidade central dos participantes
2. `sql/fase2_cur_health_unit_v1.sql` — dimensão de UBS
3. `sql/fase2_cur_journey_current_v1.sql` — jornadas terapêuticas
4. `sql/fase2_cur_session_current_v1.sql` — sessões terapêuticas
5. `sql/fase2_cur_score_current_v1.sql` — escores clínicos

---

## 4. Decisões e parâmetros operacionais

- **Dataset de destino:** `conemo-412202.firestore_curated`
- **Localização:** `southamerica-east1`
- **Projeto GCP:** `conemo-412202`
- **Ferramenta de execução:** `bq query --use_legacy_sql=false --location=southamerica-east1`
- **Modo de entrada do SQL:** pipe de stdin (`cat arquivo.sql | bq query ...`)

**Justificativa do modo de entrada (stdin pipe):**  
A tentativa inicial via `bq query "$(cat arquivo.sql)"` falhou com `FATAL Flags parsing error`, porque as crases que envolvem os nomes de tabela BigQuery no SQL (`` `projeto.dataset.tabela` ``) são interpretadas pelo shell como delimitadores de subshell, corrompendo o argumento. O pipe de stdin evita a interpolação do shell e é o modo correto para DDL extenso.

**Ajuste técnico registrado:**  
- Tentativa 1: `bq query "$(cat ...)"` → FALHOU (shell interpola crases)
- Tentativa 2: `cat arquivo.sql | bq query ...` → SUCESSO

Não houve alteração em nenhum dos scripts `fase2_cur_*.sql`.

---

## 5. Execução: Etapa 1 — Publicação das views curadas

As cinco views foram publicadas em ordem lógica (dimensão territorial → entidade central → fatos dependentes).

### VIEW 1/5 — `cur_health_unit_v1`

| Campo | Valor |
|-------|-------|
| Script de origem | `sql/fase2_cur_health_unit_v1.sql` |
| Destino | `conemo-412202.firestore_curated.cur_health_unit_v1` |
| Comando | `cat sql/fase2_cur_health_unit_v1.sql \| bq query --use_legacy_sql=false --location=southamerica-east1 --project_id=conemo-412202` |
| Job ID | `bqjob_r3752b68861d8b74f_0000019d6b189a18_1` |
| Resultado | ✅ `Created conemo-412202.firestore_curated.cur_health_unit_v1` |
| Ajuste técnico | Nenhum |

### VIEW 2/5 — `cur_participant_current_v1`

| Campo | Valor |
|-------|-------|
| Script de origem | `sql/fase2_cur_participant_current_v1.sql` |
| Destino | `conemo-412202.firestore_curated.cur_participant_current_v1` |
| Comando | `cat sql/fase2_cur_participant_current_v1.sql \| bq query --use_legacy_sql=false --location=southamerica-east1 --project_id=conemo-412202` |
| Job ID | `bqjob_r478ec7e536fe904a_0000019d6b18da4e_1` |
| Resultado | ✅ `Created conemo-412202.firestore_curated.cur_participant_current_v1` |
| Ajuste técnico | Nenhum |

### VIEW 3/5 — `cur_journey_current_v1`

| Campo | Valor |
|-------|-------|
| Script de origem | `sql/fase2_cur_journey_current_v1.sql` |
| Destino | `conemo-412202.firestore_curated.cur_journey_current_v1` |
| Comando | `cat sql/fase2_cur_journey_current_v1.sql \| bq query --use_legacy_sql=false --location=southamerica-east1 --project_id=conemo-412202` |
| Job ID | `bqjob_r717aec39f74b235a_0000019d6b19116c_1` |
| Resultado | ✅ `Created conemo-412202.firestore_curated.cur_journey_current_v1` |
| Ajuste técnico | Nenhum |

### VIEW 4/5 — `cur_session_current_v1`

| Campo | Valor |
|-------|-------|
| Script de origem | `sql/fase2_cur_session_current_v1.sql` |
| Destino | `conemo-412202.firestore_curated.cur_session_current_v1` |
| Comando | `cat sql/fase2_cur_session_current_v1.sql \| bq query --use_legacy_sql=false --location=southamerica-east1 --project_id=conemo-412202` |
| Job ID | `bqjob_r3c0bdce8c758f801_0000019d6b194083_1` |
| Resultado | ✅ `Created conemo-412202.firestore_curated.cur_session_current_v1` |
| Ajuste técnico | Nenhum |

### VIEW 5/5 — `cur_score_current_v1`

| Campo | Valor |
|-------|-------|
| Script de origem | `sql/fase2_cur_score_current_v1.sql` |
| Destino | `conemo-412202.firestore_curated.cur_score_current_v1` |
| Comando | `cat sql/fase2_cur_score_current_v1.sql \| bq query --use_legacy_sql=false --location=southamerica-east1 --project_id=conemo-412202` |
| Job ID | `bqjob_r7f2181d16ec85ce4_0000019d6b19b4c5_1` |
| Resultado | ✅ `Created conemo-412202.firestore_curated.cur_score_current_v1` |
| Ajuste técnico | Nenhum |

---

## 6. Resumo da publicação

| View | Script | Resultado | Ajuste técnico |
|------|--------|-----------|----------------|
| `cur_health_unit_v1` | `fase2_cur_health_unit_v1.sql` | ✅ SUCESSO | Nenhum |
| `cur_participant_current_v1` | `fase2_cur_participant_current_v1.sql` | ✅ SUCESSO | Nenhum |
| `cur_journey_current_v1` | `fase2_cur_journey_current_v1.sql` | ✅ SUCESSO | Nenhum |
| `cur_session_current_v1` | `fase2_cur_session_current_v1.sql` | ✅ SUCESSO | Nenhum |
| `cur_score_current_v1` | `fase2_cur_score_current_v1.sql` | ✅ SUCESSO | Nenhum |

**Total:** 5/5 views publicadas com sucesso, sem alteração dos scripts originais.

---

## 7. Segurança e governança

Cuidados adotados:

1. nenhum conteúdo de chave JSON foi impresso ou exposto;
2. nenhum segredo foi versionado;
3. nenhuma mart foi criada nesta execução;
4. nenhuma view da Fase 3.2 foi criada ou alterada;
5. nenhum dado bruto foi alterado;
6. execução restrita ao repositório institucional e branch dedicada;
7. nenhum script `fase2_cur_*.sql` foi modificado;
8. as contagens das fontes brutas antes e depois da execução são idênticas.

---

## 8. Preservação do contrato lógico

Verificado que:
- nenhuma regra de negócio foi alterada;
- os scripts publicados são os mesmos aprovados na Fase 2;
- os limites herdados (D1, D2, N4, N7) permanecem documentados em `Docs/fase-3-limites-herdados.md`;
- o mapeamento de IDs (D1: `participant_master_id = document_id`) não foi alterado;
- os filtros de teste (organizações com cidade 'FAKE CITY', 'TEST', 'TESTE') permanecem como na Fase 2.

---

## 9. Achado: bug pré-existente em `mart_dashboard_export_v1`

Durante a validação das dependências da Fase 3.2 (dry-run das marts), foi identificado:

- **`mart_ubs_monitoring_v1`**: dry-run ✅ PASSOU (bloqueio removido)
- **`mart_project_management_v1`**: dry-run ✅ PASSOU (bloqueio removido)
- **`mart_dashboard_export_v1`**: dry-run ❌ FALHOU com erro de tipo SQL pré-existente

**Erro exato:**
```
Error in query string: Column 1 in UNION ALL has incompatible types: STRING, INT64, INT64, INT64 at [257:3]
```

**Causa raiz diagnosticada:**  
No `all_metric_rows` CTE, o UNION ALL entre `ubs_metric_rows`, `city_metric_rows`, `global_metric_rows` e `unavailable_metric_rows` tem incompatibilidade de tipo na primeira coluna (`health_unit_key`):
- `ubs_metric_rows`: STRING (derivada de campo string real)
- demais CTEs: `NULL` sem CAST → BigQuery infere INT64

**Origem do bug:** pré-existente no script `sql/fase3_mart_dashboard_export_v1.sql` desde a Fase 3.2. Estava oculto pelo erro "Table not found: cur_health_unit_v1" (que ocorria antes do UNION ALL ser avaliado). Com as views disponíveis, o validador BigQuery avança e encontra o bug de tipo.

**Ação tomada:** NENHUMA — a correção deste bug está fora do escopo desta execução (arquivo `fase3_mart_*` não está na lista de arquivos autorizados). O bug deve ser corrigido como parte da retomada da Fase 3.2, mediante autorização formal.

**Impacto:** somente a mart `mart_dashboard_export_v1` está bloqueada por esse bug. As outras duas marts (`mart_ubs_monitoring_v1` e `mart_project_management_v1`) têm dry-run aprovado.

---

## 10. Situação após esta execução

| Item | Status |
|------|--------|
| Dataset `firestore_curated` | ✅ Existente e com 5 views |
| Views `cur_*` publicadas | ✅ 5/5 publicadas |
| Dados brutos (`firestore_export`) | ✅ Intactos |
| Contrato lógico da Fase 2 | ✅ Preservado |
| Fase 3.2 | ⚠️ Pronto com ressalvas — ver seção 9 |
| Fase 3.3 | 🚫 Não autorizada |
| Fase 4 | 🚫 Não autorizada |

---

*Documento registrado em conformidade com `Docs/RULES.md` e `Docs/Workflow-Projeto.md`.  
Qualquer avanço além desta execução depende de nova autorização formal.*
