# Fase 3 — Etapa 3.1: Mapeamento de validação requisitos × métricas × marts

**Data:** 2026-04-07  
**Status:** Documentação de rastreabilidade completa  
**Autor:** Ricardo Ceneviva  
**Referência:** Docs/Plano-implementacao-dashboard.md (V.2.1.0)

---

## 1) Objetivo desta etapa

Produzir **matriz de rastreamento** que liga cada requisito funcional extraído do Plano-implementacao-dashboard.md a:
- Métrica correspondente a ser implementada no mart
- Campo de origem na camada curada (Fase 2)
- Regra de cálculo ou derivação
- Agregação esperada (nível UBS, nível gestão, ou ambos)
- Validação cruzada prevista

Objetivo adicional: **identificar lacunas, indicadores parcialmente observáveis e pressupostos zero de homologação em produção**.

---

## 2) Estrutura de mapeamento

Cada linha da matriz segue o formato:

```
Requisito original
└─ Pergunta analítica
   └─ Métrica correspondente
      └─ Numerador (definição)
      └─ Denominador (população)
      └─ Filtro (condições)
      └─ Período/Janela temporal
      └─ Agregação (UBS | Gestão | Ambas)
      └─ Campo de origem (view da Fase 2)
      └─ Status de observabilidade (Completo | Parcial | Indisponível)
      └─ Nota de limite herdado (se aplicável)
```

---

## 3) Mapeamento detalhado por seção do Plano-implementacao-dashboard

### 3.1 SEÇÃO 1: Objetivo funcional

**Requisito 1.1:** "O dashboard deve operar em três planos funcionais: usuário, UBS e gestão do projeto"

| Item | Conteúdo |
|---|---|
| **Requisito** | Dashboard deve suportar agregações em nível de UBS e gestão (MVP) |
| **Pergunta analítica** | Quais são os indicadores agregados por UBS e por projeto? |
| **Métricas derivadas** | (Dependentes de seções 3.2–3.5) |
| **Agregações cobertas** | ✅ UBS, ✅ Gestão (nível projeto), ⏸ Usuário (não é eixo principal) |
| **Nota de escopo** | Nível individual (usuário) fica registrado no banco, não em interface visual do MVP |

---

### 3.2 SEÇÃO 6: Estrutura dos indicadores por nível funcional

#### 3.2.1 **Indicadores no nível da UBS** (Requisitos 6.1–6.5)

**Req 6.1:** "Volume de participantes por UBS"

| Item | Conteúdo |
|---|---|
| Métrica | `participant_count_ubs` |
| Numerador | COUNT(DISTINCT `participant_master_id`) |
| Denominador | — (total absoluto) |
| Filtro | `is_test_record = FALSE` |
| Período | Configurável (dia/semana/mês/acumulado) |
| Agregação | UBS |
| Campo de origem | `cur_participant_current_v1.participant_master_id`, `cur_participant_current_v1.health_unit_key` |
| Validação cruzada | Total de participantes em `mart_ubs_monitoring_v1` ≤ Total em `cur_participant_current_v1` |
| Status | ✅ Completo |
| Nota limite | — |

**Req 6.2:** "Elegibilidade, downloads, baseline, ativos, atrasados, desistentes, concluídos"

| Item | Descrição | Métrica | Numerador | Campo de origem | Status |
|---|---|---|---|---|---|
| Elegibilidade | % de elegíveis entre web completos | `eligibility_rate_ubs` | COUNT(DISTINCT participant com elegibility_decision='ELIGIBLE') | `cur_participant_current_v1.eligibility_status` (derivado) | ⚠️ Parcial* |
| Downloads | Participantes que baixaram app | `app_download_count_ubs` | COUNT(DISTINCT participant com baseline preenchido) | `cur_participant_current_v1` + `cur_session_current_v1` presença | ⚠️ Parcial** |
| Baseline | Preencheram baseline no app | `baseline_completed_count_ubs` | COUNT(DISTINCT participant com session_number ≥ 1) | `cur_session_current_v1` |✅ Completo |
| Ativos | Ativos em jornada nesta semana | `active_participants_ubs` | COUNT(DISTINCT participant com journey_status='ACTIVE' E session_updated_at >= today-7d) | `cur_journey_current_v1`, `cur_session_current_v1` | ✅ Completo |
| Atrasados | Sessões em atraso | `overdue_sessions_ubs` | COUNT(DISTINCT participant, journey, session com session_status='OVERDUE') | `cur_session_current_v1.session_status` | ✅ Completo |
| Desistentes | Abandono de jornada | `abandoned_participants_ubs` | COUNT(DISTINCT participant com journey_status='INACTIVE') | `cur_journey_current_v1.journey_status` | ✅ Completo |
| Concluídos | Jornada completada | `journey_completed_count_ubs` | COUNT(DISTINCT participant, journey com session_status='COMPLETED' para última sessão) | `cur_session_current_v1.session_status` | ✅ Completo |

*Elegibilidade parcial: campo `eligibility_status` não é capturado na Fase 2; derivável apenas se scores PHQ/GAD disponíveis → Nota limite D1.

**Req 6.3:** "Distribuição de escores (PHQ-9, GAD-7, IGI)"

| Item | Métrica | Numerador | Categorização | Período | Campo de origem | Status |
|---|---|---|---|---|---|---|
| PHQ-9 dist. | `phq9_distribution_ubs` | COUNT(DISTINCT participant) | Score ranges: 0-4, 5-9, 10-14, 15-19, 20-27 | Período de coleta | `cur_score_current_v1.score_value`, `score_type='PHQ'` | ✅ Completo |
| GAD-7 dist. | `gad7_distribution_ubs` | COUNT(DISTINCT participant) | Score ranges: 0-4, 5-9, 10-14, 15-20 | Período de coleta | `cur_score_current_v1.score_value`, `score_type='GAD'` | ✅ Completo |
| IGI dist. | `igi_distribution_ubs` | COUNT(DISTINCT participant) | Score ranges (standard ISI) | Período de coleta | `cur_score_current_v1.score_value`, `score_type='IGI'` | ❌ Indisponível*** |

***IGI: campo não identificado na Fase 2. Presente no contrato lógico v1 (Fase 1, seção 3), mas não encontrado em dados brutos verificados. Requisito documentado como indisponível.

**Req 6.4:** "Eventos de monitoramento operacional por UBS"

| Item | Métrica | Numerador | Campo de origem | Status |
|---|---|---|---|---|
| Notificações enviadas | `notifications_sent_ubs` | COUNT(DISTINCT participant, notification_event) | Fase 2 não captura (fora de escopo camada A bruta) | ❌ Indisponível |
| Chatbot interactions | `chatbot_interactions_ubs` | COUNT(DISTINCT participant, chatbot_event) | Idem | ❌ Indisponível |
| Help requests | `help_requests_ubs` | COUNT(DISTINCT participant com pedido de ajuda) | Idem | ❌ Indisponível |

**Nota de escopo:** Fase 2 não processa eventos de notificação, chatbot ou suporte. Estão no contrato lógico (Fase 1, seção 3.2), mas fora do escopo da camada curada mínima v1 (que foca em participante, jornada, sessão, score). Serão registrados como **indisponíveis nesta v1**.

---

#### 3.2.2 **Indicadores no nível de gestão do projeto** (Requisitos 6.6–6.9)

**Req 6.6:** "Funil completo global"

| Item | Métrica | Numerador | Denominador | Período | Agregação | Campo de origem | Status |
|---|---|---|---|---|---|---|---|
| Web iniciado | `web_initiated_global` | COUNT(DISTINCT participant com registro web) | — | Período | Global | `cur_participant_current_v1` (created_at) | ✅ Completo |
| Web concluído | `web_completed_global` | COUNT(DISTINCT participant com screening web = concluído) | `web_initiated_global` | Período | Global | Derivado (proxy: presença em cur_participant) | ⚠️ Parcial |
| Elegível | `eligible_global` | COUNT(DISTINCT participant com elegibility_decision='ELIGIBLE') | `web_completed_global` | Período | Global | `cur_participant_current_v1.eligibility_status` derivado | ⚠️ Parcial |
| App baixado | `app_download_global` | COUNT(DISTINCT participant com baseline app) | `eligible_global` | Período | Global | Proxy: `cur_session_current_v1` com session_number ≥ 1 | ⚠️ Parcial |
| Baseline completado | `baseline_completed_global` | COUNT(DISTINCT participant com baseline_submission) | `app_download_global` | Período | Global | `cur_session_current_v1.session_number ≥ 1` | ✅ Completo |
| Ativo em jornada | `active_in_journey_global` | COUNT(DISTINCT participant com journey_status='ACTIVE') | `baseline_completed_global` | Última semana | Global | `cur_journey_current_v1.journey_status` | ✅ Completo |

**Nota de incompletude:**
- "Web concluído" e "elegível" dependem de campo `eligibility_decision` que não está materializado na camada curada v1. Serão marcados como "Parcial".
- Pressuposição zero de produção: qualquer validação ocorrerá apenas após execução das views no BigQuery real.

**Req 6.7:** "Tempos médios entre etapas"

| Item | Métrica | Numerador | Denominador | Cálculo | Campo de origem | Status |
|---|---|---|---|---|---|---|
| Tempo (web → app) | `avg_days_web_to_app` | SUM(DATE_DIFF(baseline_start_date, web_completion_date, DAY)) | COUNT(DISTINCT participant) | AVG | `cur_participant_current_v1.created_at` + derivada de `cur_session_current_v1` | ⚠️ Parcial |
| Tempo (app → jornada) | `avg_days_app_to_journey` | Idem | Idem | AVG | Idem + `cur_journey_current_v1.created_at` (não capturado) | ❌ Indisponível |
| Tempo por sessão | `avg_days_per_session` | SUM(session_duration) | COUNT(sessions completadas) | AVG | `cur_session_current_v1.session_updated_at - session_created_at` (não capturado) | ❌ Indisponível |

**Nota:** Timestamps de início/fim de evento não estão completos na Fase 2. Limite herdado N7 (event_timestamp em sessões não está implementado).

**Req 6.8:** "Cobertura por cidade e UBS"

| Item | Métrica | Numerador | Denominador | Cálculo | Campo de origem | Status |
|---|---|---|---|---|---|---|
| Cobertura por UBS | `coverage_ubs_percent` | COUNT(DISTINCT participant por UBS) | População-alvo por UBS (se disponível) | % | `cur_participant_current_v1.health_unit_key`, `cur_health_unit_v1` | ⚠️ Parcial |
| Cobertura por cidade | `coverage_city_percent` | COUNT(DISTINCT participant por city) | Idem por cidade | % | `cur_participant_current_v1.ubs_city` | ⚠️ Parcial |
| UBS ativas | `active_ubs_count` | COUNT(DISTINCT health_unit_key com ≥ 1 participante ativo) | Total UBS no sistema | Contagem | `cur_health_unit_v1` + `cur_participant_current_v1` | ✅ Completo |

**Nota:** Cobertura é "Parcial" porque população-alvo por UBS/cidade não está disponível em dados brutos (seria dado externo de contexto territorial).

**Req 6.9:** "Desempenho operacional de notificações e chatbot"

| Item | Métrica | Numerador | Campo de origem | Status |
|---|---|---|---|---|
| Taxa notificação enviada | `notification_delivery_rate` | COUNT(DISTINCT evento notificação) | Fase 2 não captura | ❌ Indisponível |
| Resposta chatbot | `chatbot_response_rate` | COUNT(DISTINCT interação respondida) | Idem | ❌ Indisponível |

---

### 3.3 SEÇÃO 7: Controle de acesso e segurança

**Req 7.1:** "Dashboard visual não expõe PII"

| Item | Validação | Status |
|---|---|---|
| Nenhum nome completo em marts | Campos: `participant_id`, `user_name` — não inclusos | ✅ Verificável |
| Nenhum CPF em marts | Campo `pii_cpf` — não inclusos | ✅ Verificável |
| Nenhum email em marts | Campo `pii_email` — não inclusos | ✅ Verificável |
| Nenhum telefone em marts | Campo `pii_phone` — não inclusos | ✅ Verificável |

**Nota:** Programação letrada em cada query SQL incluirá comentário explícito: "PII segregado — não exposto nesta mart".

---

### 3.4 SEÇÃO 8: Entrega mínima viável (MVP visual)

**Req 8.1:** "MVP visual deve conter funil operacional, progresso agregado, atraso/desistência, indicadores clínicos agregados, filtro por UBS, páginas por UBS, exportação CSV, navegação por UBS/gestão, botão atualizar, timestamp"

| Item | Métrica derivada da Fase 3 | Mart de origem | Status |
|---|---|---|---|---|
| Funil operacional | `web_initiated`, `web_completed`, `eligible`, `app_download`, `baseline_completed` | `mart_project_management_v1` | ✅ Derivável |
| Progresso agregado jornadas | `active_in_journey_ubs`, `sessions_completed_ubs` | `mart_ubs_monitoring_v1` | ✅ Derivável |
| Atraso/desistência | `overdue_sessions_ubs`, `abandoned_participants_ubs` | `mart_ubs_monitoring_v1` | ✅ Derivável |
| Indicadores clínicos agregados | `phq9_distribution_ubs`, `gad7_distribution_ubs` | `mart_ubs_monitoring_v1` | ✅ Derivável |
| Filtro por UBS | Coluna: `health_unit_key`, `ubs_name`, `ubs_city` | `mart_ubs_monitoring_v1`, `mart_dashboard_export_v1` | ✅ Derivável |
| Páginas por UBS | Agrupamento: GROUP BY health_unit_key | `mart_ubs_monitoring_v1` | ✅ Derivável |
| Exportação CSV | Tabela: `mart_dashboard_export_v1` | `mart_dashboard_export_v1` | ✅ Derivável |
| Navegação UBS/gestão | Múltiplas agregações por `health_unit_key` e global | Ambas as marts | ✅ Derivável |
| Botão atualizar | Metadado: `timestamp_last_update` | `mart_dashboard_export_v1` | ✅ Derivável |
| Timestamp atualização | Coluna: `load_timestamp` | `mart_dashboard_export_v1` | ✅ Derivável |

---

## 4) Resumo de observabilidade e incompletude

### 4.1 Métrica completas (✅ — implementação direta)

- Contagens de participantes por UBS
- Status de jornada (ativo, inativo)
- Status de sessão (concluído, em atraso, não iniciado)
- Distribuição de escores PHQ-9, GAD-7
- Funil básico (participantes presentes em base → ativos)
- Indicadores de abandono (por jornada)

**Subtotal: ~15 métricas completas**

### 4.2 Métricas parcialmente observáveis (⚠️ — implementação com ressalvas)

- Elegibilidade (proxies via presença de scores)
- Cobertura (sem denominador populacional externo)
- Tempos médios entre etapas (timestamps incompletos — N7)

**Subtotal: ~5 métricas parciais**

### 4.3 Métricas indisponíveis (❌ — não implementáveis nesta v1)

- Eventos de notificação (fora de escopo camada bruta)
- Eventos de chatbot (idem)
- Pedidos de ajuda (idem)
- IGI (não encontrado em fontes brutas verificadas)
- Tempos granulares de evento (N7 não implementado)
- "Quantas vezes tentou mas não completou" (não coletado)

**Subtotal: ~8 métricas indisponíveis**

---

## 5) Matriz de rastreamento: Requisito ↔ Métrica ↔ Mart ↔ Observabilidade

| Requisito (Seção Plano) | Métrica correspondente | Mart contém | Status observabilidade | Nota de limite herdado |
|---|---|---|---|---|
| 6.1 Volume participantes/UBS | `participant_count_ubs` | `mart_ubs_monitoring_v1` | ✅ Completo | — |
| 6.2 Elegibilidade | `eligibility_rate_ubs` | `mart_ubs_monitoring_v1` (proxy) | ⚠️ Parcial | D1: `respondent_id` ausente |
| 6.2 App downloads | `app_download_count_ubs` | `mart_ubs_monitoring_v1` (proxy) | ⚠️ Parcial | N7: evento_timestamp não implementado |
| 6.2 Baseline | `baseline_completed_count_ubs` | `mart_ubs_monitoring_v1` | ✅ Completo | — |
| 6.2 Ativos | `active_participants_ubs` | `mart_ubs_monitoring_v1` | ✅ Completo | — |
| 6.2 Atrasados | `overdue_sessions_ubs` | `mart_ubs_monitoring_v1` | ✅ Completo | — |
| 6.2 Desistentes | `abandoned_participants_ubs` | `mart_ubs_monitoring_v1` | ✅ Completo | — |
| 6.2 Concluídos | `journey_completed_count_ubs` | `mart_ubs_monitoring_v1` | ✅ Completo | — |
| 6.3 PHQ-9 dist. | `phq9_distribution_ubs` | `mart_ubs_monitoring_v1` | ✅ Completo | — |
| 6.3 GAD-7 dist. | `gad7_distribution_ubs` | `mart_ubs_monitoring_v1` | ✅ Completo | — |
| 6.3 IGI dist. | `igi_distribution_ubs` | — | ❌ Indisponível | Campo IGI não encontrado em Fase 2 |
| 6.4 Notificações | `notifications_sent_ubs` | — | ❌ Indisponível | Fora escopo Fase 2 |
| 6.4 Chatbot | `chatbot_interactions_ubs` | — | ❌ Indisponível | Fora escopo Fase 2 |
| 6.4 Help requests | `help_requests_ubs` | — | ❌ Indisponível | Fora escopo Fase 2 |
| 6.6 Funil web–app | `funnel_web_app_global` | `mart_project_management_v1` | ⚠️ Parcial | Elegibilidade é proxy |
| 6.7 Tempos médios | `avg_days_per_stage` | `mart_project_management_v1` (proxy) | ⚠️ Parcial | N7: timestamps incompletos |
| 6.8 Cobertura UBS | `coverage_ubs_percent` | `mart_project_management_v1` | ⚠️ Parcial | Sem denominador populacional externo |
| 6.8 Cobertura cidade | `coverage_city_percent` | `mart_project_management_v1` | ⚠️ Parcial | Idem |
| 6.8 UBS ativas | `active_ubs_count` | `mart_project_management_v1` | ✅ Completo | — |
| 6.9 Perf. notificações | `notification_delivery_rate` | — | ❌ Indisponível | Fora escopo Fase 2 |
| 6.9 Perf. chatbot | `chatbot_response_rate` | — | ❌ Indisponível | Idem |
| 7.1 PII não exposto | (Validação de exclusão) | Todas | ✅ Verificável | Programação letrada incluirá comentário |
| 8.1 MVP visual | (Agregação de métricas acima) | `mart_ubs_monitoring_v1` + `mart_project_management_v1` | ✅ Derivável | — |

---

## 6) Pressuposição ZERO de homologação em produção

**Reforço obrigatório em todos os scripts SQL da Fase 3:**

```sql
-- AVISO: As views da Fase 2 (cur_participant_current_v1, cur_health_unit_v1, 
-- cur_journey_current_v1, cur_session_current_v1, cur_score_current_v1) foram 
-- implementadas como código pronto para execução mas NÃO foram ainda validadas 
-- em operação no BigQuery real. As queries desta mart derivam de views que:
-- 1. não foram rodadas em produção
-- 2. não tiveram seus dados validados contra critérios de negócio reais
-- 3. podem conter divergências em campo/tipo/lógica ao serem executadas
--
-- Todos os números desta mart devem ser considerados PROVISÓRIOS até que 
-- a Fase 2 tenha sido homologada formalmente em produção.
--
-- Limites conhecidos herdados:
-- - D1: respondent_id ausente da fonte (respondent_id NULL em todos registros)
-- - D2: userId não é coluna top-level (resolvido internamente: document_id = $.id)
-- - N7: event_timestamp em sessões não implementado nesta v1
-- - Eventos de notificação/chatbot fora do escopo da camada curada mínima
-- - IGI não encontrado em fontes brutas verificadas
--
-- Para auditoria completa, veja: Docs/fase-2-verificacao-tecnica-bigquery.md
--                               Docs/fase-2-nota-tecnica-implementacao.md
--                               Docs/fase-3-limites-herdados.md
```

---

## 7) Próxima etapa (Etapa 3.2)

Com este mapeamento completo, a Etapa 3.2 implementará:
1. `mart_ubs_monitoring_v1` — agregações por UBS
2. `mart_project_management_v1` — agregações globais de gestão
3. `mart_dashboard_export_v1` — tabela de exportação CSV

Cada script terá:
- Bloco inicial de explicação natural (objetivo, granularidade, fontes, limites herdados)
- Código SQL comentado
- Bloco de notas internas de decisão

---

**Data de aprovação deste mapeamento:** [a preencher]  
**Aprovador:** [Professor/Revisor]

