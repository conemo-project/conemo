# Fase 3.2 — Retomada técnica final da validação

**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-08  
**Projeto:** CONEMO  
**Repositório:** `conemo-project/conemo` (clone institucional)  
**Branch desta execução:** `fase-3-2-retomada-validacao-tecnica-final`  
**Modo principal:** Validação técnica → auditoria e reconciliação → documentação técnica/handoff

---

## 1) Objetivo desta execução

Concluir a revalidação técnica da Fase 3.2 com base no estado já validado:

- views curadas `cur_*` publicadas e disponíveis no BigQuery;
- três marts implementadas em SQL;
- correção cirúrgica de tipagem em `mart_dashboard_export_v1` já aplicada.

---

## 2) Fontes obrigatórias lidas

### 2.1 Canônicas
1. `Docs/RULES.md` (workspace canônico)
2. `Docs/Workflow-Projeto.md` (workspace canônico)

### 2.2 Base obrigatória desta retomada
1. `Docs/Plano-implementacao-dashboard.md`
2. Plano Operacional de Pré-processamento de Dados aprovado *(referenciado em documentos de fase; não há arquivo dedicado com esse título no clone nesta data)*
3. `Docs/fase-camada-sql-compartilhada-bigquery-sgbd.md`
4. `Docs/fase-1-contrato-minimo-camada-compartilhada.md`
5. `Docs/fase-2-verificacao-tecnica-bigquery.md`
6. `Docs/fase-2-nota-tecnica-implementacao.md`
7. `Docs/fase-3-construcao-marts-minimos-dashboard.md`
8. `Docs/fase-3-regras-metricas.md`
9. `Docs/fase-3-validacao-requisitos-marts.md`
10. `Docs/fase-3-limites-herdados.md`
11. `Docs/fase-3-nota-decisoria-dataset-destino-2026-04-07.md`
12. `Docs/fase-3-preparacao-dataset-destino.md`
13. `Docs/fase-3-checkpoint-operacional-dataset-destino.md`
14. `Docs/fase-correcao-publicacao-views-curadas.md`
15. `Docs/fase-validacao-tecnica-views-curadas.md`
16. Auditoria da correção controlada de infraestrutura/integração *(não encontrada como arquivo dedicado no clone; base utilizada: pareceres formais e documentos de correção já versionados)*
17. Auditoria da correção cirúrgica de `sql/fase3_mart_dashboard_export_v1.sql` *(não encontrada como arquivo dedicado no clone; base utilizada: evidência técnica do commit e do dry-run aprovado)*

### 2.3 Scripts SQL lidos integralmente
- `sql/fase2_cur_participant_current_v1.sql`
- `sql/fase2_cur_health_unit_v1.sql`
- `sql/fase2_cur_session_current_v1.sql`
- `sql/fase2_cur_journey_current_v1.sql`
- `sql/fase2_cur_score_current_v1.sql`
- `sql/fase3_mart_ubs_monitoring_v1.sql`
- `sql/fase3_mart_project_management_v1.sql`
- `sql/fase3_mart_dashboard_export_v1.sql`

---

## 3) Etapa 1 — Revalidação técnica das três marts (dry-run)

### 3.1 `mart_ubs_monitoring_v1`

- Comando: `cat sql/fase3_mart_ubs_monitoring_v1.sql | bq query --use_legacy_sql=false --location=southamerica-east1 --project_id=conemo-412202 --dry_run`
- Resultado: `Query successfully validated`
- Classificação: **PASSOU**

### 3.2 `mart_project_management_v1`

- Comando: `cat sql/fase3_mart_project_management_v1.sql | bq query --use_legacy_sql=false --location=southamerica-east1 --project_id=conemo-412202 --dry_run`
- Resultado: `Query successfully validated`
- Classificação: **PASSOU**

### 3.3 `mart_dashboard_export_v1`

- Comando: `cat sql/fase3_mart_dashboard_export_v1.sql | bq query --use_legacy_sql=false --location=southamerica-east1 --project_id=conemo-412202 --dry_run`
- Resultado: `Query successfully validated`
- Classificação: **PASSOU**

### 3.4 Síntese da Etapa 1

| Mart | Resultado técnico | Classificação |
|---|---|---|
| `mart_ubs_monitoring_v1` | Dry-run válido | PASSOU |
| `mart_project_management_v1` | Dry-run válido | PASSOU |
| `mart_dashboard_export_v1` | Dry-run válido (erro de tipagem removido) | PASSOU |

---

## 4) Etapa 2 — Verificação mínima de prontidão operacional

### 4.1 Dependências `cur_*` resolvidas

- Verificação de dataset: `bq ls --project_id=conemo-412202 firestore_curated`
- Evidência: presença de `cur_health_unit_v1`, `cur_journey_current_v1`, `cur_participant_current_v1`, `cur_score_current_v1`, `cur_session_current_v1`
- Conclusão: dependências imediatas das marts estão resolvidas.

### 4.2 Aptidão para criação efetiva como views

Os três scripts de mart usam `CREATE OR REPLACE VIEW` e passaram no dry-run em `southamerica-east1`, portanto estão aptos tecnicamente para criação efetiva no dataset `firestore_curated` quando autorizado.

### 4.3 Dependência de bruto / parse estrutural

Foi verificado que as marts da Fase 3.2:
- consultam apenas `conemo-412202.firestore_curated.cur_*`;
- não consultam `firestore_export` diretamente;
- não usam parse estrutural (`JSON_VALUE`, `JSON_EXTRACT`, `path_params`) na camada de mart.

Conclusão: não há reintrodução de parse estrutural no consumo de dashboard via marts.

### 4.4 Coerência mínima com plano e limites

Coerência confirmada entre:
- nomes de colunas e granularidades das marts;
- fontes curadas (`cur_*`) previstas na Fase 3;
- limites herdados documentados (`D1`, `N7`, `N-IGI`, indisponibilidade de notificações/chatbot/help);
- regras de métricas documentadas na Etapa 3.1.

---

## 5) Gate técnico final da Fase 3.2

### Decisão

> **Fase 3.2: TECNICAMENTE CONCLUÍDA**.

### Justificativa

1. As 3 marts passaram no dry-run BigQuery.
2. Dependências `cur_*` estão publicadas e resolvidas.
3. Não há erro remanescente impeditivo de sintaxe/tipagem/schema/referência imediata.
4. Os scripts permanecem aderentes ao plano validado da Fase 3.
5. Nenhuma atividade fora do escopo foi executada nesta retomada.

---

## 6) Pendências fora do escopo desta execução

1. Publicação efetiva das marts como views no BigQuery (DDL real), se/quando autorizada.
2. Início da Fase 3.3 (validação cruzada) — **não autorizado nesta execução**.
3. Auditoria formal desta retomada técnica final antes de qualquer avanço de fase.

---

## 7) Confirmações de escopo e governança

- ✅ Execução ocorreu no repositório GitHub institucional (`conemo-project/conemo`).
- ✅ Branch dedicada criada para esta execução.
- ✅ Cláusula de governança incorporada e respeitada.
- ✅ Apenas a retomada técnica final da Fase 3.2 foi executada.
- ✅ Fase 3.3 não iniciada.
- ✅ Fase 4 não iniciada.
- ✅ Nenhuma mart nova foi criada nesta execução.
- ✅ Nenhuma regra de negócio foi alterada.

---

*Documento registrado em conformidade com `Docs/RULES.md` e `Docs/Workflow-Projeto.md`.  
Não iniciar Fase 3.3 sem nova autorização formal.*
