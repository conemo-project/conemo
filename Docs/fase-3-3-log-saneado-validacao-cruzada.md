# Log saneado — Fase 3.3 validação cruzada dos marts

**Data:** 2026-04-08  
**Branch:** `fase-3-3-validacao-cruzada-marts-minimos`  
**Projeto:** CONEMO

## 1) Operações executadas

1. Criação da branch dedicada da fase.
2. Materialização operacional das views:
   - `mart_ubs_monitoring_v1`
   - `mart_project_management_v1`
   - `mart_dashboard_export_v1`
3. Listagem de objetos no dataset `firestore_curated` para confirmação de presença de `cur_*` e `mart_*`.
4. Execução de queries de validação cruzada por mart (cardinalidade, totais globais e limites de plausibilidade).

## 2) Resultado saneado por mart

- `mart_ubs_monitoring_v1`: **PASSOU**
  - reconciliação de linhas: OK (10 vs 10)
  - violações de limites: 0

- `mart_project_management_v1`: **PASSOU**
  - recorte CITY: OK (3 vs 3, incluindo bucket de cidade nula)
  - global e soma por cidade: OK (458)
  - violações de limites: 0

- `mart_dashboard_export_v1`: **PASSOU**
  - cardinalidade total: OK (59 vs 59)
  - métrica global de participantes: OK
  - métricas indisponíveis explícitas: 4 (OK)

## 3) Classificação de fase

**Fase 3.3 = VALIDADA (sem ressalvas materiais)**.

## 4) Escopo preservado

- sem modificação de SQL dos marts;
- sem início de Fase 4;
- sem reabertura de fases anteriores (não houve bloqueador material).
