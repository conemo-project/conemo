# Validação técnica mínima — Views curadas publicadas (`cur_*`)

**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-08  
**Projeto:** CONEMO  
**Repositório:** `conemo-project/conemo` (clone institucional)  
**Branch:** `fase-correcao-publicacao-views-curadas`  
**Documento complementar:** `Docs/fase-correcao-publicacao-views-curadas.md`

---

## 1. Objetivo desta validação

Confirmar a disponibilidade operacional das cinco views curadas publicadas na Etapa 1 desta correção controlada e emitir o gate explícito sobre a possibilidade de retomar tecnicamente a validação da Fase 3.2.

---

## 2. Testes executados

### V1 — Listagem do dataset `firestore_curated`

**Comando:**
```bash
bq ls --project_id=conemo-412202 firestore_curated
```

**Resultado:**
```
           tableId             Type
 ---------------------------- ------
  cur_health_unit_v1           VIEW
  cur_journey_current_v1       VIEW
  cur_participant_current_v1   VIEW
  cur_score_current_v1         VIEW
  cur_session_current_v1       VIEW
```

**Conclusão:** ✅ As 5 views estão listadas como VIEW no dataset `firestore_curated`.

---

### V2 — `bq show` em cada view (confirmação de esquema)

**Comando:**
```bash
bq show --project_id=conemo-412202 firestore_curated.<view>
```

| View | Tipo | Esquema (colunas principais) | Resultado |
|------|------|------------------------------|-----------|
| `cur_health_unit_v1` | VIEW | health_unit_key, ubs_name, ubs_city, health_unit_status | ✅ OK |
| `cur_participant_current_v1` | VIEW | participant_master_id, source_document_id, gender, risk, health_unit_key, is_test_record, created_at | ✅ OK |
| `cur_journey_current_v1` | VIEW | participant_master_id, journey_id, journey_type, journey_status, last_session_number, journey_updated_at | ✅ OK |
| `cur_session_current_v1` | VIEW | participant_master_id, journey_id, session_document_id, session_number, is_completed, session_status | ✅ OK |
| `cur_score_current_v1` | VIEW | participant_master_id, score_type, score_value, score_reference_date, score_source, score_quality_flag | ✅ OK |

**Conclusão:** ✅ Esquemas confirmados conforme contrato lógico da Fase 1.

---

### V3 — Dry-run de SELECT em cada view

**Comando (por view):**
```bash
echo "SELECT COUNT(*) FROM `conemo-412202.firestore_curated.<view>`" | \
  bq query --use_legacy_sql=false --location=southamerica-east1 --project_id=conemo-412202 --dry_run
```

| View | Bytes estimados | Resultado |
|------|-----------------|-----------|
| `cur_health_unit_v1` | 4.637.034 | ✅ `Query successfully validated` |
| `cur_participant_current_v1` | 7.241.721 | ✅ `Query successfully validated` |
| `cur_journey_current_v1` | 1.871.099 | ✅ `Query successfully validated` |
| `cur_session_current_v1` | 8.025.261 | ✅ `Query successfully validated` |
| `cur_score_current_v1` | 9.112.820 | ✅ `Query successfully validated` |

**Conclusão:** ✅ Todas as 5 views são consultáveis sem erro.

---

### V4 — Contagens reais de leitura

**Comando:**
```bash
echo "SELECT COUNT(*) AS total FROM `conemo-412202.firestore_curated.<view>`" | \
  bq query --use_legacy_sql=false --location=southamerica-east1 --project_id=conemo-412202 --format=csv
```

| View | Registros retornados | Comparação com bruto | Resultado |
|------|---------------------|----------------------|-----------|
| `cur_health_unit_v1` | **16** UBSs distintas | — (dimensão derivada) | ✅ OK |
| `cur_participant_current_v1` | **458** participantes | 459 raw (1 excluído: teste ou vazio) | ✅ OK |
| `cur_journey_current_v1` | **547** jornadas | 899 raw (filtro: userId presente) | ✅ OK |
| `cur_session_current_v1` | **4.521** sessões | 7.714 raw (filtro: userId presente) | ✅ OK |
| `cur_score_current_v1` | **982** escores | — (2 fontes × participantes com scores) | ✅ OK |

**Nota sobre as contagens:** as diferenças entre a contagem bruta e a curada são esperadas e documentadas:
- 1 registro excluído de `cur_participant_current_v1`: record com `document_id` nulo/vazio (filtro do PASSO 1) ou registrado como teste.
- Diferença em jornadas/sessões: filtro `userId IS NOT NULL AND TRIM(userId) != ''` elimina registros sem vínculo com participante.
- `cur_score_current_v1` com 982 linhas: gerado por UNION ALL de PHQ + GAD de forms[0] (2 linhas por participante com forms) e scores de jornadas.

---

### V5 — Verificação de dependências para Fase 3.2 (dry-run das marts)

**Objetivo:** confirmar que o bloqueio central da Fase 3.2 — ausência das views `cur_*` — foi removido.

**Comando:**
```bash
cat sql/fase3_mart_<nome>.sql | \
  bq query --use_legacy_sql=false --location=southamerica-east1 --project_id=conemo-412202 --dry_run
```

| Mart | Resultado |
|------|-----------|
| `mart_ubs_monitoring_v1` | ✅ `Query successfully validated` — 0 bytes (DDL CREATE VIEW) |
| `mart_project_management_v1` | ✅ `Query successfully validated` — 0 bytes (DDL CREATE VIEW) |
| `mart_dashboard_export_v1` | ❌ `Error in query string: Column 1 in UNION ALL has incompatible types: STRING, INT64, INT64, INT64 at [257:3]` |

**Diagnóstico do erro em `mart_dashboard_export_v1`:**
- Bug pré-existente no script `sql/fase3_mart_dashboard_export_v1.sql` (Fase 3.2).
- Causa raiz: colunas como `health_unit_key` são `NULL` sem CAST em `city_metric_rows`, `global_metric_rows` e `unavailable_metric_rows`. BigQuery infere INT64 para `NULL` não tipado; conflita com STRING derivada de campo real em `ubs_metric_rows`.
- O bug estava oculto pelo erro anterior `Table not found: cur_health_unit_v1`, que ocorria antes de o validador chegar ao UNION ALL.
- Correção necessária: aplicar `CAST(NULL AS STRING)` nas colunas STRING que recebem NULL nessas CTEs (health_unit_key, ubs_name, metric_denominator quando aplicável).
- **Ação desta execução:** nenhuma — arquivo não autorizado para modificação nesta correção controlada.

---

### V6 — Integridade dos dados brutos

**Objetivo:** confirmar que nenhum dado bruto foi alterado durante esta execução.

**Comando:**
```bash
echo "SELECT COUNT(*) AS total FROM `conemo-412202.firestore_export.<table>`" | \
  bq query --use_legacy_sql=false --location=southamerica-east1 --project_id=conemo-412202 --format=csv
```

| Tabela | Contagem esperada (Etapa 2, 07/04/2026) | Contagem atual (08/04/2026) | Integridade |
|--------|-----------------------------------------|-----------------------------|-------------|
| `users_raw_latest` | 459 | **459** | ✅ INTACTA |
| `sessions_raw_latest` | 7.714 | **7.714** | ✅ INTACTA |
| `journeys_raw_latest` | 899 | **899** | ✅ INTACTA |

**Conclusão:** ✅ Dados brutos não foram alterados.

---

## 3. Resumo consolidado dos testes

| Validação | Descrição | Resultado |
|-----------|-----------|-----------|
| V1 — Listagem | 5 views visíveis em `firestore_curated` | ✅ PASSOU |
| V2 — Esquema | `bq show` confirma tipo VIEW e colunas corretas | ✅ PASSOU |
| V3 — Dry-run SELECT | 5/5 views consultáveis sem erro | ✅ PASSOU |
| V4 — Contagem real | 5/5 views retornam dados coerentes | ✅ PASSOU |
| V5 — Deps Fase 3.2 | 2/3 marts com dry-run aprovado; 1 com bug pré-existente | ⚠️ PARCIAL |
| V6 — Integridade | Contagens de dados brutos idênticas ao checkpoint anterior | ✅ PASSOU |

---

## 4. Gate explícito — retomada técnica da Fase 3.2

### Questão-chave

> As dependências imediatas para a revalidação técnica da Fase 3.2 foram satisfeitas?

### Resposta

**Pronto com ressalvas.**

#### O que está resolvido

- As 5 views `cur_*` estão publicadas e operacionais em `firestore_curated`.
- `mart_ubs_monitoring_v1` e `mart_project_management_v1` têm dry-run aprovado com as views disponíveis.
- O bloqueio central registrado na auditoria da Fase 3.2 (ausência das views `cur_*`) **foi removido**.

#### O que continua pendente

1. **Bug de tipo em `mart_dashboard_export_v1`** (arquivo `sql/fase3_mart_dashboard_export_v1.sql`, linha 257): UNION ALL com incompatibilidade `STRING vs INT64` em colunas nullable. Correção é trivial (aplicar `CAST(NULL AS STRING)`) mas requer autorização formal como parte da retomada da Fase 3.2.
2. **Publicação das marts** (DDL efetivo, não apenas dry-run): as três marts da Fase 3.2 ainda não foram publicadas no BigQuery. Isso depende de autorização formal para retomada da Fase 3.2.
3. **Validação cruzada (Fase 3.3)**: não iniciada e não autorizada.

#### Impacto operacional do bug

- O bug afeta **apenas** `mart_dashboard_export_v1` — o componente de exportação row-per-metric para o dashboard.
- `mart_ubs_monitoring_v1` e `mart_project_management_v1` estão prontas para publicação imediata.
- O bug é cirúrgico (correção de `NULL` para `CAST(NULL AS STRING)` em 3 CTEs) e pode ser corrigido como primeiro passo da retomada da Fase 3.2.

---

## 5. Pontos que exigem decisão humana

1. **Autorização para retomada da Fase 3.2**: publicação das 3 marts (incluindo correção do bug em `mart_dashboard_export_v1`) e validação cruzada.
2. **Definição do escopo da correção de `mart_dashboard_export_v1`**: se o bug deve ser corrigido como parte desta correção controlada ou como primeiro passo da Fase 3.2 retomada (recomendado).

---

## 6. Conclusão

**Esta fase emite o seguinte gate:**

> ⚠️ **Pronto com ressalvas** para retomar a validação técnica da Fase 3.2.

**Justificativa:**
- O bloqueio central (ausência de `cur_*` no BigQuery) foi **completamente removido**.
- As 5 views curadas estão publicadas, validadas e acessíveis.
- 2 das 3 marts têm dry-run aprovado com as novas dependências.
- 1 mart tem um bug SQL pré-existente descoberto durante esta validação — fora do escopo desta correção, mas com diagnóstico completo documentado.

**Próximo passo recomendado (sujeito a autorização formal):**  
Iniciar a retomada da Fase 3.2 com:
1. Correção do bug em `mart_dashboard_export_v1` (trivial, com autorização formal).
2. Publicação das 3 marts no BigQuery.
3. Execução de dry-run completo das 3 marts publicadas.
4. Avanço para as queries de validação cruzada (Fase 3.3) — quando autorizado.

---

*Documento registrado em conformidade com `Docs/RULES.md` e `Docs/Workflow-Projeto.md`.  
Não retome automaticamente a Fase 3.2. Aguarde nova autorização após auditoria desta correção.*
