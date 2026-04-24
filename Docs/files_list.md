# Inventário completo do repositório `_clone_oficial_conemo`

**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-08  
**Critério:** inventário de arquivos e pastas do repositório (excluindo metadados internos de `.git`).  
**Objetivo:** apoiar decisão de limpeza antes do Pull Request.

## Legenda da coluna de decisão
- **Manter**: deve permanecer no repositório para rastreabilidade/execução.
- **Descartar**: pode ser removido antes do PR (arquivo temporário/sistema/apoio não essencial).

| Caminho | Tipo | Descrição breve | Manter/Descartar antes do PR |
|---|---|---|---|
| . | Pasta (raiz) | Raiz do repositório institucional | Manter |
| .DS_Store | Arquivo sistema | Metadado do macOS na raiz | Descartar |
| .gitignore | Arquivo configuração | Regras de exclusão de arquivos no Git | Manter |
| Code | Pasta | Código-fonte do projeto | Manter |
| Code/.DS_Store | Arquivo sistema | Metadado do macOS em `Code/` | Descartar |
| Code/PY | Pasta | Scripts Python do projeto | Manter |
| Code/PY/dashboard_conemo.py | Arquivo Python | Aplicação/dashboard principal | Manter |
| Code/PY/inspect_conemo2.py | Arquivo Python | Script auxiliar de inspeção local | Descartar |
| Code/README.md | Arquivo Markdown | Guia da pasta de código | Manter |
| Data | Pasta | Dados de trabalho do projeto | Manter |
| Data/PARQUET | Pasta | Artefatos em Parquet usados na análise | Manter |
| Data/PARQUET/conemo_dados_consolidados_raw_04_03_2026.parquet | Arquivo Parquet | Snapshot consolidado de dados | Manter |
| Data/PARQUET/conemo_dados_consolidados_raw.parquet | Arquivo Parquet | Base consolidada local sem sufixo de data | Manter |
| Docs | Pasta | Documentação técnica e de governança | Manter |
| Docs/fase-1-contrato-minimo-camada-compartilhada.md | Arquivo Markdown | Contrato mínimo da fase 1 | Manter |
| Docs/fase-2-nota-tecnica-implementacao.md | Arquivo Markdown | Nota técnica de implementação da fase 2 | Manter |
| Docs/fase-2-verificacao-tecnica-bigquery.md | Arquivo Markdown | Verificação técnica de BigQuery | Manter |
| Docs/fase-3-2-log-saneado-validacao-final.md | Arquivo Markdown | Log saneado de validação final da 3.2 | Manter |
| Docs/fase-3-2-retomada-validacao-tecnica-final.md | Arquivo Markdown | Retomada e validação técnica final da 3.2 | Manter |
| Docs/fase-3-3-log-saneado-validacao-cruzada.md | Arquivo Markdown | Log saneado da validação cruzada 3.3 | Manter |
| Docs/fase-3-3-parecer-auditoria-2026-04-08.md | Arquivo Markdown | Parecer de auditoria da fase 3.3 | Manter |
| Docs/fase-3-3-tabela-achados-marts.md | Arquivo Markdown | Tabela de achados dos marts | Manter |
| Docs/fase-3-3-validacao-cruzada-marts.md | Arquivo Markdown | Documento de validação cruzada dos marts | Manter |
| Docs/fase-3-checkpoint-operacional-dataset-destino.md | Arquivo Markdown | Checkpoint operacional do dataset destino | Manter |
| Docs/fase-3-construcao-marts-minimos-dashboard.md | Arquivo Markdown | Plano/construção dos marts mínimos | Manter |
| Docs/fase-3-limites-herdados.md | Arquivo Markdown | Registro de limites herdados da fase 3 | Manter |
| Docs/fase-3-log-saneado-dataset-destino.md | Arquivo Markdown | Log saneado de dataset destino | Manter |
| Docs/fase-3-nota-decisoria-dataset-destino-2026-04-07.md | Arquivo Markdown | Nota decisória do dataset destino | Manter |
| Docs/fase-3-parecer-auditoria-2026-04-07.md | Arquivo Markdown | Parecer de auditoria da fase 3 | Manter |
| Docs/fase-3-parecer-auditoria-etapa-2-2026-04-07.md | Arquivo Markdown | Parecer de auditoria da etapa 2 da fase 3 | Manter |
| Docs/fase-3-precheck-operacional-etapa-3-2.md | Arquivo Markdown | Precheck operacional da etapa 3.2 | Manter |
| Docs/fase-3-precheck-operacional-log-saneado.md | Arquivo Markdown | Precheck com log saneado | Manter |
| Docs/fase-3-preparacao-dataset-destino.md | Arquivo Markdown | Preparação do dataset destino | Manter |
| Docs/fase-3-regras-metricas.md | Arquivo Markdown | Regras e métricas da fase 3 | Manter |
| Docs/fase-3-relatorio-conclusao.md | Arquivo Markdown | Relatório de conclusão da fase 3 | Manter |
| Docs/fase-3-relatorio-etapa-3-1.md | Arquivo Markdown | Relatório da etapa 3.1 | Manter |
| Docs/fase-3-validacao-requisitos-marts.md | Arquivo Markdown | Validação de requisitos dos marts | Manter |
| Docs/fase-4-backlog-tecnico-sgbd.md | Arquivo Markdown | Backlog técnico de aderência SGBD | Manter |
| Docs/fase-4-matriz-aderencia-sgbd.md | Arquivo Markdown | Matriz de aderência ao modelo SGBD | Manter |
| Docs/fase-4-nota-aderencia-sgbd.md | Arquivo Markdown | Nota técnica de aderência SGBD | Manter |
| Docs/fase-4-parecer-auditoria-2026-04-08.md | Arquivo Markdown | Parecer de auditoria da fase 4 | Manter |
| Docs/fase-5-nota-tecnica-integracao-dashboard.md | Arquivo Markdown | Nota técnica de integração com dashboard | Manter |
| Docs/fase-5-parecer-auditoria-2026-04-08.md | Arquivo Markdown | Parecer de auditoria da fase 5 | Manter |
| Docs/fase-5-prova-conceito-bigquery-dashboard.md | Arquivo Markdown | Prova de conceito de integração BigQuery | Manter |
| Docs/fase-5-tabela-compatibilidade-dashboard-esquema.md | Arquivo Markdown | Compatibilidade dashboard x esquema | Manter |
| Docs/fase-6-checklist-qualidade.md | Arquivo Markdown | Checklist final de qualidade da fase 6 | Manter |
| Docs/fase-6-checklist-seguranca-pii.md | Arquivo Markdown | Checklist final de segurança/PII | Manter |
| Docs/fase-6-handoff-final.md | Arquivo Markdown | Handoff final da rodada | Manter |
| Docs/fase-6-parecer-auditoria-2026-04-08.md | Arquivo Markdown | Parecer formal de encerramento fase 6 | Manter |
| Docs/fase-6-relatorio-conclusao-rodada.md | Arquivo Markdown | Relatório de conclusão da rodada | Manter |
| Docs/fase-camada-sql-compartilhada-bigquery-sgbd.md | Arquivo Markdown | Documento-base da fase 0/arquitetura | Manter |
| Docs/fase-correcao-publicacao-views-curadas.md | Arquivo Markdown | Registro de correção de publicação curada | Manter |
| Docs/fase-dashboard-executiva-1.md | Arquivo Markdown | Minuta executiva da frente dashboard | Manter |
| Docs/fase-validacao-tecnica-views-curadas.md | Arquivo Markdown | Validação técnica das views curadas | Manter |
| Docs/fechamento-rodada-preparacao-pr.md | Arquivo Markdown | Documento de preparação para PR institucional | Manter |
| Docs/Plano-implementacao-dashboard.md | Arquivo Markdown | Plano canônico do dashboard | Manter |
| README.md | Arquivo Markdown | README institucional do projeto | Manter |
| sql | Pasta | Scripts SQL da camada curada e marts | Manter |
| sql/fase2_cur_health_unit_v1.sql | Arquivo SQL | View curada de unidade de saúde | Manter |
| sql/fase2_cur_journey_current_v1.sql | Arquivo SQL | View curada de jornadas | Manter |
| sql/fase2_cur_participant_current_v1.sql | Arquivo SQL | View curada de participantes | Manter |
| sql/fase2_cur_score_current_v1.sql | Arquivo SQL | View curada de escores | Manter |
| sql/fase2_cur_session_current_v1.sql | Arquivo SQL | View curada de sessões | Manter |
| sql/fase2_validacao_contagens.sql | Arquivo SQL | Script de validação de contagens | Manter |
| sql/fase3_mart_dashboard_export_v1.sql | Arquivo SQL | Mart de exportação para dashboard | Manter |
| sql/fase3_mart_project_management_v1.sql | Arquivo SQL | Mart de gestão do projeto | Manter |
| sql/fase3_mart_ubs_monitoring_v1.sql | Arquivo SQL | Mart de monitoramento por UBS | Manter |

## Resumo de decisão pré-PR

- **Descartar:** `.DS_Store`, `Code/.DS_Store`, `Code/PY/inspect_conemo2.py`.
- **Manter:** todos os demais itens inventariados.
