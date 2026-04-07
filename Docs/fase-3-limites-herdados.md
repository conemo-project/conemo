# Fase 3 — Documentação de limites herdados e pressupostos de validação

**Data:** 2026-04-07  
**Status:** Registro explícito de restrições, divergências e pressupostos operacionais  
**Autor:** Ricardo Ceneviva

---

## 1) Objetivo

Documento que registra **explicitamente**:

1. **Limites estruturais herdados** da Fase 0, 1 e 2 que afetam implementação na Fase 3
2. **Pressuposição ZERO de homologação em produção** das views da Fase 2
3. **Campos indisponíveis** e seu impacto em métricas
4. **Decisões e proxies** adotados para contornar limitações

Este documento é a **prova de que nenhum limite foi "resolvido silenciosamente"**.

---

## 2) Divergências materiais da Fase 2 que impactam Fase 3

### 2.1 **D1: `respondent_id` completamente ausente**

**Fonte:** Docs/fase-2-verificacao-tecnica-bigquery.md, Divergência D1

**Status:** Material | Documentado | Sem resolução | Pendência formal

**O que foi feito na Fase 2:**
- Campo `respondent_id` foi procurado em:
  - Coluna top-level de `users_raw_latest` ❌ Não existe
  - JSON de `users_raw_latest.DATA` ❌ Não existe
- Estratégia de reconciliação de chaves mestre (Fase 1) era: `respondent_id` (T1) → `userId` (T2) → `document_id` (T3)
- **Resultado:** Fase 2 usou `document_id` para todos, com `source_respondent_id = NULL` e `id_reconciliation_status = 'RESOLVED_DOCUMENT'`

**Impacto em Fase 3:**
- Todas as métricas usam `participant_master_id = document_id` (único ID disponível)
- Nenhuma possibilidade de validar ou reconciliar contra `respondent_id` no BigQuery
- Se futuro `respondent_id` for adicionado à fonte bruta, será necessário **remapear todos os IDs da Fase 2 em diante**
- Pressuposição: `document_id = userId = participant_master_id` é suficiente para esta versão v1

**Decisão requerida:**
- [ ] Aceitar `document_id` como identificador único da v1
- [ ] OU incorporar `respondent_id` em futuro export de dados brutos e reprocessar Fases 2–3

**Nota em cada script SQL da Fase 3:**
```sql
-- NOTA D1: participant_master_id usa exclusivamente document_id (respondent_id indisponível).
-- Se respondent_id for adicionado à fonte, será necessário reprocessar os marts.
```

---

### 2.2 **D2: `userId` não é coluna top-level** (RESOLVIDO)

**Fonte:** Docs/fase-2-verificacao-tecnica-bigquery.md, Divergência D2

**Status:** Nominal | Resolvido | Sem impacto operacional

**O que foi feito na Fase 2:**
- Contrato Fase 1 mencionava "userId"
- Verificação física constatou: `userId` não existe como coluna top-level em `users_raw_latest`
- **Resolução:** `document_id = JSON_VALUE(DATA, '$.id')` (mesmo valor)
- Status em Fase 2: `source_user_id = JSON_VALUE(DATA, '$.id')`

**Impacto em Fase 3:**
- ✅ Zero impacto — `document_id` já substitui `userId` completamente
- Nenhuma métrica depende de `userId` como campo separado

**Decisão:** Nenhuma — resolvido internamente.

---

## 3) Notas técnicas (menores) que afetam Fase 3

### 3.1 **N4: `health_unit_key` — localização corrigida**

**Fonte:** Docs/fase-2-nota-tecnica-implementacao.md, Nota N4

**Status:** Estrutural | Corrigido | Sem impacto em métricas

**O que foi feito na Fase 2:**
- Contrato Fase 1: `health_unit_key` seria de `path_params`
- Verificação física: `path_params` vazio para usuários
- **Realidade:** `health_unit_key = JSON_VALUE(DATA, '$.organization.id')`
- Fase 2 corrigiu internamente: `cur_participant_current_v1.health_unit_key = organization.id`

**Impacto em Fase 3:**
- ✅ Nenhum — integração com `cur_health_unit_v1` via este campo funciona corretamente

---

### 3.2 **N7: `event_timestamp` em sessões não implementado**

**Fonte:** Docs/fase-2-nota-tecnica-implementacao.md, Nota N7

**Status:** Estrutural | Não implementado | **Impacto ALTO em métricas de tempo**

**O que foi feito na Fase 2:**
- Campo `event_timestamp` (timestamp de início da sessão) procurado em:
  - `sessions_raw_latest.DATA` ❌ Não encontrado
  - Potencial fonte: `completedDate` em JSON ⚠️ Formato incerto
- **Decisão Fase 2:** `event_timestamp = NULL` na view (marcado para futuro)

**Impacto em Fase 3:**
- ❌ **Métricas de tempo não podem ser calculadas com precisão:**
  - `avg_days_web_to_app` será **proxy** (usando `journey_updated_at`)
  - `avg_days_per_session` será **indisponível** (não há duração de sessão)
  - Tempos de progresso serão **aproximados**

**Workaround aplicado em Fase 3:**
```sql
-- AVISO N7: Timestamps precisos de evento não disponíveis.
-- Proxy usado: journey_updated_at (último acesso à jornada).
-- Valores de tempo são APROXIMADOS até que event_timestamp seja disponibilizado.
SELECT
  EXTRACT(WEEK FROM DATE(p.created_at)) AS week_created,
  EXTRACT(WEEK FROM DATE(j.journey_updated_at)) AS week_first_access,
  DATE_DIFF(DATE(j.journey_updated_at), DATE(p.created_at), DAY) AS approx_days_to_journey,
  -- Nota: Este é um proxy. Não representa tempo real de resposta.
FROM cur_participant_current_v1 p
LEFT JOIN cur_journey_current_v1 j
  USING (participant_master_id)
```

**Decisão requerida:**
- [ ] Aceitar proxies de tempo com esta ressalva
- [ ] OU investigar alternativa de fonte de timestamp (ex: logs de aplicativo, contatos mensageria)

---

### 3.3 **N-IGI: Campo IGI não encontrado em fonte bruta**

**Status:** Observabilidade | Indisponível | Métrica não pode ser implementada

**O que foi constatado:**
- Contrato Fase 1 inclui IGI (Índice de Gravidade de Insônia)
- Verificação de dados brutos (CSV de 8.940 registros) ❌ Campo não identificado
- Possibilidades:
  - IGI em campo JSON aninhado não explorado
  - IGI não coletado na fase atual do projeto
  - IGI em tabela separada não incluída no Firestore export

**Impacto em Fase 3:**
- ❌ **Métrica `igi_distribution_ubs` não pode ser implementada**
- Requisito 6.3 do Plano-implementacao-dashboard.md (IGI distribution) será marcado como "Indisponível — não encontrado em dados brutos"

**Decisão requerida:**
- [ ] Confirmar se IGI está em campo oculto dos JSONs
- [ ] Confirmar se IGI não foi coletado nesta coorte
- [ ] Se coletado em futuro, reprocessar marts

**Nota em scripts SQL:**
```sql
-- AVISO: IGI não encontrado em fontes brutas verificadas.
-- Métrica igi_distribution_ubs não será implementada nesta v1.
-- Veja: Docs/fase-3-limites-herdados.md, seção 3.3.
```

---

## 4) Campos indisponíveis (fora do escopo Fase 2) que afetam Fase 3

### 4.1 Eventos de notificação

**Status:** Fora de escopo | Indisponível | Múltiplas métricas impactadas

**O que era esperado (Fase 1, seção 3.2):**
- `fact_notification_event` — eventos de notificação enviada/recebida/aberta
- Métricas: `notifications_sent_ubs`, `notification_delivery_rate`

**O que Fase 2 entrega:**
- Views curadas focam em: participante, saúde, jornada, sessão, escore
- Eventos de notificação não estão em `sessions_raw_latest` ou `journeys_raw_latest`
- Presumivelmente estão em coleção Firestore separada não incluída no escopo Fase 2

**Impacto em Fase 3:**
- ❌ Métricas de notificação não podem ser implementadas
- Requisitos 6.4, 6.9 do Plano-implementacao-dashboard.md serão marcados como "Indisponíveis"

---

### 4.2 Eventos de chatbot

**Status:** Fora de escopo | Indisponível | Múltiplas métricas impactadas

**O que era esperado (Fase 1, seção 3.2):**
- `fact_chatbot_event` — interações com chatbot
- Métricas: `chatbot_interactions_ubs`, `chatbot_response_rate`

**O que Fase 2 entrega:**
- Idem notificações: não capturado em escopo de camada curada mínima

**Impacto em Fase 3:**
- ❌ Métricas de chatbot não podem ser implementadas

---

### 4.3 Pedidos de ajuda / Help requests

**Status:** Fora de escopo | Indisponível | Operacional

**O que era esperado:**
- `fact_help_request` — registros de participante pedindo ajuda
- Métrica: `help_requests_ubs`

**Impacto em Fase 3:**
- ❌ Métrica não implementada

---

## 5) Pressuposição ZERO de homologação em produção das views da Fase 2

### 5.1 Estado de validação das views da Fase 2

| View | Código escrito | Testado em sandbox | Rodado em produção | Status |
|---|---|---|---|---|
| `cur_participant_current_v1` | ✅ Sim | ❓ Não verificado | ❌ Não | Proposto, não validado |
| `cur_health_unit_v1` | ✅ Sim | ❓ Não verificado | ❌ Não | Proposto, não validado |
| `cur_journey_current_v1` | ✅ Sim | ❓ Não verificado | ❌ Não | Proposto, não validado |
| `cur_session_current_v1` | ✅ Sim | ❓ Não verificado | ❌ Não | Proposto, não validado |
| `cur_score_current_v1` | ✅ Sim | ❓ Não verificado | ❌ Não | Proposto, não validado |

**Implicações:**
- Todos os números de Fase 3 são **derivações de código não testado em produção**
- Possíveis problemas de implementação:
  - Sintaxe SQL incompatível com BigQuery real
  - Tipo de dados incompatível
  - Lógica de join incorreta descoberta apenas na execução
  - Performance inaceitável

### 5.2 Obrigação de marca em cada script SQL

**Cada script SQL de mart da Fase 3 começará com:**

```sql
-- ============================================================================
-- AVISO CRÍTICO DE VALIDAÇÃO
-- ============================================================================
-- Esta mart é derivada de views da Fase 2 que NÃO FORAM EXECUTADAS EM 
-- PRODUÇÃO E NÃO TIVERAM SEUS DADOS VALIDADOS CONTRA CRITÉRIOS DE NEGÓCIO REAIS.
--
-- Quando a Fase 2 for implantada em BigQuery real:
-- 1. Execute as 5 views da Fase 2 antes dessa mart
-- 2. Valide as contagens e distribuições contra expectativas de negócio
-- 3. Só então execute esta mart
-- 4. Valide esta mart contra os critérios de Etapa 3.3
--
-- ATÉ LÁ, TODOS OS NÚMEROS DESTA MART SÃO PROVISÓRIOS.
-- ============================================================================
```

---

## 6) Decisões tomadas em Fase 3 para contornar limitações

### 6.1 Uso de `document_id` como `participant_master_id` (D1 contorno)

**Justificativa:** Única chave disponível; compatível com contrato Fase 1 v1.

**Risco:** Se `respondent_id` for adicionado, haverá descontinuidade histórica.

**Mitigação:** Documentação clara; decisão formal requerida para futuro.

---

### 6.2 Uso de `journey_updated_at` como proxy para `event_timestamp` (N7 contorno)

**Justificativa:** Campo disponível; aproximação aceitável para agregações de nível UBS.

**Risco:** Métricas de tempo underestimate (mostram tempo mínimo, não tempo real).

**Mitigação:** Marcação clara; validação cruzada contra dados esperados.

---

### 6.3 Exclusão de métricas indisponíveis (IGI, notificações, chatbot, ajuda)

**Justificativa:** Dados não estão na camada curada mínima v1.

**Risco:** Dashboard não terá visão completa que o Plano-implementacao-dashboard.md desejava.

**Mitigação:** Documentação em `fase-3-validacao-requisitos-marts.md` marca como "Indisponível"; não é "Não implementado" (que sugeriria escolha).

---

## 7) Impacto consolidado em cada métrica

| Métrica | Afetada por | Impacto | Decisão Fase 3 |
|---|---|---|---|
| `participant_count_ubs` | D1 (OK – só usa document_id), views não validadas | Mínimo | Implementar com aviso |
| `active_participants_ubs` | Views não validadas | Mínimo | Implementar com aviso |
| `phq9_score_avg_ubs` | Views não validadas | Mínimo | Implementar com aviso |
| `avg_days_web_to_app` | N7 (proxy), views não validadas | **Alto** | Implementar como proxy; marcar WARN |
| `avg_days_per_session` | N7 (indisponível) | **Crítico** | Não implementar — indisponível |
| `igi_distribution_ubs` | N-IGI (não encontrado) | **Crítico** | Não implementar — indisponível |
| `notifications_sent_ubs` | Fora escopo Fase 2 | **Crítico** | Não implementar — indisponível |
| `chatbot_interactions_ubs` | Fora escopo Fase 2 | **Crítico** | Não implementar — indisponível |
| `help_requests_ubs` | Fora escopo Fase 2 | **Crítico** | Não implementar — indisponível |

---

## 8) Quadro resumido de restrições

### 8.1 Restrições de identificador

✅ **Resolvido internamente:** `userId` → `document_id`  
⚠️ **Pendente:** `respondent_id` (D1)  
✅ **Impacto aceitável:** Usar `document_id` como `participant_master_id`

### 8.2 Restrições de timestamp

❌ **Não resolvido:** `event_timestamp` (N7)  
✅ **Contorno:** Proxy com `journey_updated_at`  
❌ **Impacto alto:** Métricas de tempo serão aproximadas/underestimated

### 8.3 Restrições de cobertura de domínio

❌ **Indisponível:** IGI (N-IGI)  
❌ **Indisponível:** Eventos de notificação  
❌ **Indisponível:** Eventos de chatbot  
❌ **Indisponível:** Pedidos de ajuda

### 8.4 Restrições de validação

⚠️ **Crítico:** Views da Fase 2 não foram rodadas em produção  
⚠️ **Crítico:** Nenhuma contagem foi validada contra dados reais  
⚠️ **Crítico:** Possíveis erros de sintaxe/tipo descobertos apenas na execução

---

## 9) Checklist obrigatório para Etapa 3.2–3.4

Antes de finalizar implementação dos marts:

- [ ] Cada script SQL contém aviso de "Pressuposição ZERO de produção"
- [ ] Cada script SQL marca limitações herdadas (D1, N7, N-IGI, etc.)
- [ ] Métricas indisponíveis estão **documentadas como indisponíveis**, não silenciosamente omitidas
- [ ] Proxies (ex: `journey_updated_at` para tempo) estão **claramente marcados como proxies**
- [ ] Nenhuma decisão de contorno silenciosa foi tomada
- [ ] Documentação permite que revisor humano entenda completamente todas as limitações

---

## 10) Próxima etapa

Fase 3 prossegue com **implementação dos marts (Etapa 3.2)** conhecendo **explicitamente** todos estes limites. Não há "surpresas" — tudo foi documentado.

**Revisão crítica em Etapa 3.5:** Antes de relatório final, revisor humano valida se todos os limites foram comunicados corretamente aos stakeholders.

---

**Data de aprovação deste documento:** [a preencher]  
**Aprovador:** [Professor/Revisor]

