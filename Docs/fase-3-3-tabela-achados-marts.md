# Fase 3.3 — Tabela de achados (validação cruzada dos marts)

**Data:** 2026-04-08  
**Projeto:** CONEMO

| ID | Mart | Verificação | Resultado | Classificação | Evidência numérica |
|---|---|---|---|---|---|
| A1 | `mart_ubs_monitoring_v1` | Cardinalidade por UBS | OK | sem ressalvas | esperado 10, mart 10, mismatch 0 |
| A2 | `mart_ubs_monitoring_v1` | Limites de consistência interna | OK | sem ressalvas | baseline>participants 0; active>participants 0; abandoned>participants 0 |
| A3 | `mart_ubs_monitoring_v1` | Faixa plausível de escores médios | OK | sem ressalvas | PHQ fora [0,27] = 0; GAD fora [0,21] = 0 |
| A4 | `mart_project_management_v1` | Cardinalidade CITY (com bucket nulo) | OK | sem ressalvas | esperado 3, mart 3, mismatch 0 |
| A5 | `mart_project_management_v1` | Reconciliação global de participantes | OK | sem ressalvas | esperado 458, mart 458, mismatch 0 |
| A6 | `mart_project_management_v1` | Soma CITY vs GLOBAL | OK | sem ressalvas | soma CITY 458, GLOBAL 458, mismatch 0 |
| A7 | `mart_project_management_v1` | Limites percentuais e contagens | OK | sem ressalvas | active>participants 0; abandoned>participants 0; percentuais fora [0,100] = 0 |
| A8 | `mart_dashboard_export_v1` | Cardinalidade total esperada da export mart | OK | sem ressalvas | esperado 59, mart 59, mismatch 0 |
| A9 | `mart_dashboard_export_v1` | Reconciliação `participant_count_global` | OK | sem ressalvas | mismatch_count 0 |
| A10 | `mart_dashboard_export_v1` | Métricas indisponíveis explícitas | OK | sem ressalvas | linhas INDISPONIVEL = 4 (esperado 4) |

## Síntese final

- **Sem erro material identificado.**
- **Sem achado com ressalva técnica impeditiva.**
- **Status consolidado da Fase 3.3: validada.**
