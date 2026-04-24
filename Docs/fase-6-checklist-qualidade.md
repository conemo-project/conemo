# Fase 6 — Checklist de qualidade

**Data:** 2026-04-08  
**Projeto:** CONEMO  
**Escopo:** fechamento de rodada (qualidade, segurança e handoff), sem reimplementação de `cur_*`, marts ou refatoração de dashboard.

---

## 1) Fontes obrigatórias lidas e usadas

- Normativas: `Docs/RULES.md`, `Docs/Workflow-Projeto.md`.
- Base de plano/contrato: `Docs/Plano-implementacao-dashboard.md`, `Docs/fase-camada-sql-compartilhada-bigquery-sgbd.md`, `Docs/fase-1-contrato-minimo-camada-compartilhada.md`.
- Verificação/implementação técnica: `Docs/fase-2-verificacao-tecnica-bigquery.md`, `Docs/fase-2-nota-tecnica-implementacao.md`.
- Encerramentos de validação: Fase 3.3, Fase 4 e Fase 5 (notas, tabelas, logs e pareceres).
- SQLs curados/marts: `sql/fase2_cur_*.sql` e `sql/fase3_mart_*.sql`.

✅ **Status:** concluído.

---

## 2) Checklist de qualidade consolidada

## 2.1 Governança e rastreabilidade

- [x] Execução aderente às normativas (ordem de leitura e precedência documental).
- [x] Trilhas de decisão e pareceres formais preservados até Fase 5.
- [x] Sem abertura indevida de nova fase durante o fechamento.

**Resultado:** aprovado.

## 2.2 Integridade estrutural da camada curada (`cur_*`)

- [x] `cur_participant_current_v1` mantém chave operacional e marca limitação D1 explicitamente.
- [x] `cur_health_unit_v1` preserva dimensão UBS/cidade para agregação.
- [x] `cur_journey_current_v1`, `cur_session_current_v1` e `cur_score_current_v1` preservam domínios e flags de qualidade.
- [x] Limitações conhecidas (D1, N7, IGI/eventos ausentes) não foram ocultadas.

**Resultado:** aprovado com limitações herdadas documentadas.

## 2.3 Qualidade dos marts mínimos

- [x] `mart_ubs_monitoring_v1` previamente validada sem ressalva material.
- [x] `mart_project_management_v1` previamente validada sem ressalva material.
- [x] `mart_dashboard_export_v1` previamente validada sem ressalva material.
- [x] Métricas indisponíveis explicitadas em `metric_status='INDISPONIVEL'`.

**Resultado:** aprovado (conforme Fase 3.3 + parecer).

## 2.4 Coerência dashboard × camada BigQuery

- [x] Viabilidade parcial confirmada para modo agregado UBS/gestão.
- [x] Incompatibilidades do modo individual explicitadas (sem maquiagem técnica).
- [x] Sem refatoração ampla fora de escopo na Fase 5.

**Resultado:** aprovado com restrição de escopo (integração parcial).

## 2.5 Qualidade documental da rodada

- [x] Encerramentos anteriores mantidos consistentes.
- [x] Taxonomia de cobertura padronizada em Fase 4 (`coberta`, `parcialmente coberta`, `pendente`).
- [x] Conclusões técnicas e de auditoria não conflitantes entre fases.

**Resultado:** aprovado.

---

## 3) Não conformidades críticas

Nenhuma não conformidade crítica nova foi identificada na Fase 6.

---

## 4) Riscos residuais (não bloqueadores do fechamento da rodada)

1. **D1**: ausência de `respondent_id` na fonte exportada.
2. **N7**: ausência de `event_timestamp` robusto para sessão (uso de proxy).
3. **Cobertura funcional incompleta** para IGI/notificações/chatbot/help.
4. **Dashboard completo “as is”** ainda não substitui totalmente o Parquet local.

---

## 5) Pendências condicionadas (decisão humana)

1. Deliberação sobre estratégia definitiva de chave mestre (`document_id` vs evolução com `respondent_id`).
2. Deliberação sobre escopo de integração do dashboard (apenas agregado ou expansão controlada).
3. Priorização institucional do backlog técnico de aderência plena ao núcleo SGBD.

---

## 6) Veredito do checklist de qualidade

> **Checklist de qualidade: APROVADO COM RISCOS RESIDUAIS DOCUMENTADOS.**

A rodada pode ser encerrada na Fase 6 sem reabrir fases anteriores, mantendo operação controlada e auditável.