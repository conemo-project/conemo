# Fase 4 — Matriz de aderência da camada compartilhada ao núcleo do SGBD

**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-08  
**Projeto:** CONEMO  
**Branch:** `fase-4-alinhamento-explicito-modelo-sgbd`  
**Modo principal:** Modelagem de dados  
**Sequência:** Auditoria e reconciliação → Documentação técnica e handoff

---

## 1) Objetivo desta matriz

Mapear explicitamente os objetos já implementados nas Fases 2 e 3 (`cur_*` e marts mínimas) para os eixos centrais do núcleo do SGBD, classificando a aderência como:

- **coberta**
- **parcialmente coberta**
- **pendente**

Esta matriz não reimplementa camada curada, não reimplementa marts e não reabre fases anteriores.

### Eixos centrais do núcleo do SGBD

Os eixos centrais considerados nesta Fase 4, sempre na mesma ordem, são:

1. participante
2. unidade de saúde
3. triagem/elegibilidade
4. avaliação longitudinal
5. escore derivado
6. uso do app

### Relação com os demais artefatos da Fase 4

- Esta matriz faz o mapeamento estrutural entre objetos implementados e eixos do núcleo do SGBD.
- A nota de aderência consolida o julgamento de cobertura resultante deste mapeamento.
- O backlog técnico traduz as lacunas identificadas em pendências técnicas e decisórias.

---

## 2) Fontes efetivamente usadas

1. `Docs/RULES.md` (workspace canônico)
2. `Docs/Workflow-Projeto.md` (workspace canônico)
3. `Docs/Plano-implementacao-dashboard.md`
4. `Docs/fase-camada-sql-compartilhada-bigquery-sgbd.md`
5. `Docs/fase-1-contrato-minimo-camada-compartilhada.md`
6. `Docs/fase-2-verificacao-tecnica-bigquery.md`
7. `Docs/fase-2-nota-tecnica-implementacao.md`
8. `Docs/fase-3-2-retomada-validacao-tecnica-final.md`
9. `Docs/fase-3-2-log-saneado-validacao-final.md`
10. `Docs/fase-3-3-validacao-cruzada-marts.md`
11. `Docs/fase-3-3-log-saneado-validacao-cruzada.md`
12. `Docs/fase-3-3-tabela-achados-marts.md`
13. `Docs/fase-3-3-parecer-auditoria-2026-04-08.md`
14. `sql/fase2_cur_participant_current_v1.sql`
15. `sql/fase2_cur_health_unit_v1.sql`
16. `sql/fase2_cur_journey_current_v1.sql`
17. `sql/fase2_cur_session_current_v1.sql`
18. `sql/fase2_cur_score_current_v1.sql`
19. `sql/fase3_mart_ubs_monitoring_v1.sql`
20. `sql/fase3_mart_project_management_v1.sql`
21. `sql/fase3_mart_dashboard_export_v1.sql`

**Nota de fonte:** não há arquivo dedicado com o título exato “Plano Operacional de Pré-processamento de Dados aprovado” no clone; o plano está referenciado formalmente nos documentos de fase.

---

## 3) Critério de classificação adotado

- **coberta**: eixo com objeto(s) implementado(s), granularidade útil ao SGBD e validação técnica já documentada.
- **parcialmente coberta**: eixo com base implementada, porém com limites estruturais/documentais reconhecidos (ex.: D1, N7, ausência de eventos).
- **pendente**: eixo sem objeto implementado adequado na camada atual.

---

## 4) Matriz objeto implementado → eixo do núcleo do SGBD

| Objeto implementado | Entidade/eixo SGBD relacionado | Tipo de aderência | Observações técnicas |
|---|---|---|---|
| `cur_participant_current_v1` | participante | coberta | Chave `participant_master_id` operacional; PII segregado da camada analítica |
| `cur_health_unit_v1` | unidade de saúde | coberta | Dimensão de UBS/cidade padronizada e usada como base de agregação |
| `cur_journey_current_v1` | avaliação longitudinal; uso do app | parcialmente coberta | Estado de jornada e progresso; sem trilha longitudinal completa de eventos clínicos |
| `cur_session_current_v1` | avaliação longitudinal; uso do app | parcialmente coberta | Sessões e status operacionais; `event_timestamp` permanece nulo (N7; ver backlog 3.2.4) |
| `cur_score_current_v1` | triagem/elegibilidade; escore derivado | parcialmente coberta | PHQ/GAD (FORM_INITIAL) + score de jornada; IGI indisponível (ver backlog 3.2.2); elegibilidade não materializada como decisão explícita (ver backlog 3.1.1) |
| `mart_ubs_monitoring_v1` | unidade de saúde; escore derivado; uso do app | coberta | Métricas UBS validadas na Fase 3.3, com indisponibilidades explicitadas |
| `mart_project_management_v1` | triagem/elegibilidade; avaliação longitudinal; uso do app | parcialmente coberta | Funil e cobertura por proxy; tempos com proxy e sem eventos completos (ver backlog 3.2.4) |
| `mart_dashboard_export_v1` | integração externa de consumo | coberta | Estrutura de exportação auditável, com `metric_status='INDISPONIVEL'` preservando lacunas; ativo de integração, não eixo central do núcleo |
| `Docs/fase-3-3-validacao-cruzada-marts.md` + parecer | governança de aderência | coberta | Evidência de validação cruzada e encerramento da Fase 3.3 sem ressalvas materiais |

---

## 5) Classificação consolidada por eixo central do núcleo do SGBD

| Eixo central do núcleo SGBD | Classificação | Evidência objetiva |
|---|---|---|
| participante | **coberta** | `cur_participant_current_v1` implementada e utilizada por todos os objetos derivados; limitação D1 remete ao backlog 3.2.1 |
| unidade de saúde | **coberta** | `cur_health_unit_v1` + agregações de UBS nas marts validadas |
| triagem/elegibilidade | **parcialmente coberta** | Escores de triagem presentes; decisão formal de elegibilidade não materializada como entidade própria (ver backlog 3.1.1) |
| avaliação longitudinal | **parcialmente coberta** | Jornadas/sessões disponíveis; ausência de timeline clínica completa e de timestamp de evento robusto (ver backlog 3.1.2 e 3.2.4) |
| escore derivado | **parcialmente coberta** | PHQ/GAD e score de jornada disponíveis; IGI e cobertura ampliada ainda não presentes (ver backlog 3.2.2 e 3.1.3) |
| uso do app | **parcialmente coberta** | Progresso de sessão/jornada coberto; eventos de notificação/chatbot/help indisponíveis (ver backlog 3.2.3) |

---

## 6) Resultado da Etapa 1 (mapeamento estrutural)

- Objetos relevantes da camada compartilhada listados e mapeados.
- Matriz de aderência concluída com critério explícito.
- Cobertura classificada sem superestimar escopo.
- Nenhuma reabertura de Fase 1, 2 ou 3.
