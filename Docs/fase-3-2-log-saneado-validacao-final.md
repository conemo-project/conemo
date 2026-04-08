# Log saneado — Retomada técnica final da Fase 3.2

**Data:** 2026-04-08  
**Branch:** `fase-3-2-retomada-validacao-tecnica-final`  
**Projeto:** CONEMO

## 1) Comandos executados

1. `cat sql/fase3_mart_ubs_monitoring_v1.sql | bq query --use_legacy_sql=false --location=southamerica-east1 --project_id=conemo-412202 --dry_run`
2. `cat sql/fase3_mart_project_management_v1.sql | bq query --use_legacy_sql=false --location=southamerica-east1 --project_id=conemo-412202 --dry_run`
3. `cat sql/fase3_mart_dashboard_export_v1.sql | bq query --use_legacy_sql=false --location=southamerica-east1 --project_id=conemo-412202 --dry_run`
4. `bq ls --project_id=conemo-412202 firestore_curated`
5. buscas de verificação em `sql/fase3_mart_*.sql` para confirmar ausência de dependência direta de `firestore_export` e parse JSON

## 2) Resultados

- `mart_ubs_monitoring_v1`: **PASSOU** (`Query successfully validated`)
- `mart_project_management_v1`: **PASSOU** (`Query successfully validated`)
- `mart_dashboard_export_v1`: **PASSOU** (`Query successfully validated`)
- dependências `cur_*`: **resolvidas** (5 views listadas em `firestore_curated`)
- erro remanescente de tipagem em `UNION ALL`: **não identificado** nesta execução

## 3) Decisão de gate

**Fase 3.2 = TECNICAMENTE CONCLUÍDA** (sem erro impeditivo de dry-run).

## 4) Escopo preservado

- nenhuma alteração em regras de negócio;
- nenhuma criação de nova mart;
- nenhuma abertura de Fase 3.3;
- nenhuma abertura de Fase 4.
