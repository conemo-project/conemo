# Fase 3 — Relatório de conclusão da Etapa 3.1 (fase em aberto)

**Data:** 2026-04-07  
**Status:** Etapa 3.1 aprovada com ressalvas documentadas; Fase 3 permanece em aberto  
**Autor:** Ricardo Ceneviva  
**Branch:** `fase-3-construcao-marts-minimos`

---

## Campo 1: Arquivos criados ou modificados

### Criados (5 documentos, 0 scripts SQL — Etapa 3.1 apenas)

| Arquivo | Tipo | Linhas | Propósito | Commit |
|---|---|---|---|---|
| `Docs/fase-3-construcao-marts-minimos-dashboard.md` | MD | 368 | Plano operacional geral da Fase 3 | 3a5f803 |
| `Docs/fase-3-validacao-requisitos-marts.md` | MD | 304 | Matriz de rastreamento requisitos ↔ métricas ↔ marts | 9847fbf |
| `Docs/fase-3-regras-metricas.md` | MD | 473 | Definições formais de cada métrica | f663e43 |
| `Docs/fase-3-limites-herdados.md` | MD | 356 | Documentação de limites e divergências | 6ad45fc |
| `Docs/fase-3-relatorio-etapa-3-1.md` | MD | 324 | Relatório executivo de Etapa 3.1 | 449835f |

**Total:** 5 documentos, ~1.825 linhas de especificação técnica.

### Modificados

Nenhum arquivo foi modificado — apenas criações.

---

## Campo 2: Branch criada e registrada

- ✅ **Branch:** `fase-3-construcao-marts-minimos`
- ✅ **Criada de:** `fase-2-implementacao-camada-curada-minima` (commit ffe10c8)
- ✅ **Estado:** Ativa, 5 commits novos, pronta para aprovação
- ✅ **Histórico de commits:**
  ```
  449835f (HEAD) docs(fase-3): relatorio-executivo-etapa-3-1-documentacao-completa-pronta-para-checkpoint
  6ad45fc docs(fase-3): registrar limites-herdados e pressupostos-zero-producao explicitamente
  f663e43 docs(fase-3): registrar regras de calculo de metricas com numeradores-denominadores-filtros
  9847fbf docs(fase-3): registrar matriz de rastreamento requisitos-metricas-marts com observabilidade
  3a5f803 docs(fase-3): registrar plano operacional com mapeamento preliminar de requisitos-metricas-marts
  ```

---

## Campo 3: Conteúdo principal implementado (Etapa 3.1)

### 3.1 Estrutura de execução (5 etapas planejadas)

| Etapa | Nome | Status | Artefatos |
|---|---|---|---|
| 3.1 | Documentação de requisitos e rastreabilidade | ✅ **Concluída e aprovada com ressalvas** | 5 documentos MD |
| 3.2 | Implementação SQL de 3 marts com programação letrada | ⏳ **Não iniciada** | 3 scripts SQL + comentários |
| 3.3 | Queries de validação cruzada | ⏳ **Não iniciada** | 1 script SQL de auditoria |
| 3.4 | Documentação de limites herdados (já integrada em 3.1) | ✅ **Concluída** | Documento dedicado |
| 3.5 | Relatório de conclusão da Fase 3 (final) | ⏳ Não iniciada | Relatório final |

### 3.2 Conteúdo de Etapa 3.1 (concluído)

**Plano operacional:** Objetivo, cláusula de governança, escopo, arquitetura de 3 marts, fontes canônicas, plano de implementação, critérios de validação, fora de escopo, estrutura de arquivos esperados.

**Matriz de rastreamento:** Cada requisito do Plano-implementacao-dashboard.md ligado a métrica correspondente, mart de origem, campo de fonte na camada curada, status de observabilidade, nota de limite.

**Regras de métricas:** Definição formal de 25+ métricas com numerador, denominador, filtros, período, agregação.

**Limites herdados:** Documentação explícita de D1, D2, N4, N7, N-IGI, campos indisponíveis, pressuposição ZERO de produção, decisões de contorno.

---

## Campo 4: Fontes efetivamente usadas

### Leitura obrigatória (pré-Fase 3)

1. ✅ `Docs/RULES.md` — 460 linhas (lido integralmente)
2. ✅ `Docs/Workflow-Projeto.md` — 653 linhas (lido integralmente)
3. ✅ `Docs/Plano-implementacao-dashboard.md` — V.2.1.0, ~800+ linhas (lido integralmente)
4. ✅ `Docs/fase-1-contrato-minimo-camada-compartilhada.md` — 247 linhas (lido integralmente)
5. ✅ `Docs/fase-2-verificacao-tecnica-bigquery.md` — 332 linhas (lido integralmente)
6. ✅ `Docs/fase-2-nota-tecnica-implementacao.md` — 241 linhas (lido integralmente)

### Fontes canônicas efetivamente incorporadas na Etapa 3.1

- **Plano-implementacao-dashboard.md:** Mapeamento de requisitos (seções 1, 6, 7, 8)
- **Fase-1 contrato:** Granularidade de entidades, campos, estratégia de IDs
- **Fase-2 documentação:** Divergências D1, D2, notas N4, N7, limites de cobertura
- **RULES.md:** Programação letrada, aderência procedural, literate programming
- **Workflow-Projeto.md:** Etapas de plano operacional, validação, checkpoint

---

## Campo 5: Marts produzidas (especificação v1)

**Número:** 3 marts mínimas especificadas (SQL pronto para Etapa 3.2)

### 5.1 `mart_ubs_monitoring_v1`

- **Granularidade:** 1 linha por (health_unit_key, periodo)
- **Propósito:** Indicadores operacionais e clínicos por UBS
- **Métricas incluídas:** 9 métricas (contagem, ativo, overdue, abandonment, escores)
- **Fonte:** Views cur_participant, cur_health_unit, cur_journey, cur_session, cur_score (Fase 2)
- **Status:** Especificação concluída, SQL a implementar em Etapa 3.2

### 5.2 `mart_project_management_v1`

- **Granularidade:** 1 linha por período (agregação global ou por city)
- **Propósito:** Visão executiva — funil, cobertura, tempos médios, desempenho operacional
- **Métricas incluídas:** 7 métricas (funil global, tempos, cobertura, qualidade)
- **Fonte:** Idem acima (agregação de todas as 5 views)
- **Status:** Especificação concluída, SQL a implementar em Etapa 3.2

### 5.3 `mart_dashboard_export_v1`

- **Granularidade:** 1 linha por combinação (participant + UBS + período + tipo_métrica)
- **Propósito:** Tabela estruturada para exportação CSV e consumo Streamlit
- **Estrutura:** Dimensões (period, health_unit_key, ubs_name, ubs_city, journey_type) + métricas + metadados
- **Fonte:** Idem acima
- **Status:** Estrutura definida, SQL a implementar em Etapa 3.2

**Nota:** Todas as 3 marts consultam a camada curada v1 (Fase 2), não JSON bruto. Sem reintrodução de parse estrutural no Streamlit.

---

## Campo 6: Regras de métricas documentadas

### 6.1 Cobertura de métricas

| Categoria | Métricas | Status | Observabilidade |
|---|---|---|---|
| Funil | web_initiated, baseline_completed, eligible, active_in_journey | ✅ Documentado | ✅ Completo / ⚠️ Parcial (eligibility proxy) |
| UBS agregadas | participant_count, active, overdue, abandoned, phq9_avg, gad7_dist | ✅ Documentado | ✅ Completo |
| Gestão global | funil_global, tempo_web_app, cobertura_ubs, ubs_ativas, qualidade_ok_pct | ✅ Documentado | ✅ Completo / ⚠️ Parcial (tempo é proxy) |
| Indisponíveis | IGI_dist, notifications, chatbot, help_requests | ✅ Documentado | ❌ Indisponível |

### 6.2 Documentação de cada métrica

**Padrão em `fase-3-regras-metricas.md`:**
- Definição em linguagem natural
- Numerador (SQL-ready)
- Denominador (quando aplicável)
- Filtros (condições)
- Período (janela temporal)
- Agregação (GROUP BY)
- Nota de interpretação

**Exemplo documentado:**
```
participant_count_ubs
- Definição: Número total de participantes por UBS no período
- Numerador: COUNT(DISTINCT participant_master_id) WHERE health_unit_key IS NOT NULL AND is_test_record = FALSE
- Período: Configurável (padrão acumulado)
- Agregação: GROUP BY health_unit_key
```

---

## Campo 7: Validações realizadas (até Etapa 3.1)

### 7.1 Validação de escopo (Etapa 3.1)

✅ Escopo autorizado respeitado:
- ✅ 3 marts mínimas descritas (não expandidas)
- ✅ Foco em UBS e gestão (não individual)
- ✅ Documentação de numeradores/denominadores/filtros realizada
- ✅ Camada curada preservada como base (sem parse Streamlit)
- ✅ Limites herdados registrados explicitamente
- ✅ Documentação técnica versionada no GitHub

### 7.2 Validação de aderência (Etapa 3.1)

✅ Aderência ao RULES.md:
- ✅ Tarefa classificada (Modo D — Indicadores e marts)
- ✅ Fontes canônicas consultadas em hierarquia correta
- ✅ Programação letrada obrigatória — documentos incluem explicação natural + matrizes
- ✅ Reprodutibilidade preservada (rastreamento a fontes)

✅ Aderência ao Workflow-Projeto.md:
- ✅ Etapa B (Plano) — documentação de plano operacional
- ✅ Etapa C (Validação) — pronto para revisor humano
- ✅ Etapa D (Autorização) — aguardando aprovação
- ✅ Sem execução prematura

### 7.3 Validação de requisitos (Etapa 3.1)

✅ Matriz de rastreamento:
- ✅ Cada requisito do Plano-implementacao-dashboard.md mapeado a métrica
- ✅ Observabilidade documentada (Completo/Parcial/Indisponível)
- ✅ Nenhuma lacuna silenciosa (métricas indisponíveis explicitamente marcadas)

### 7.4 Validação de limites herdados (Etapa 3.1)

✅ Documentação de restrições:
- ✅ D1 (respondent_id ausente) — documentado, decisão requerida
- ✅ D2 (userId não é coluna) — documentado, resolvido
- ✅ N7 (event_timestamp não implementado) — documentado, proxy proposto
- ✅ N-IGI (não encontrado) — documentado, indisponível
- ✅ Campos indisponíveis — notificações, chatbot, ajuda, todos documentados
- ✅ Pressuposição ZERO de produção — marca crítica a ser incluída em cada script

### 7.5 Verificações ainda pendentes (Etapa 3.2+)

❓ Sintaxe SQL (realizado em Etapa 3.2 — desenvolvimento)
❓ Teste lógico (realizado em Etapa 3.2 — testes)
❓ Execução em BigQuery real (pós-homologação Fase 2)
❓ Validação de contagem contra dados reais (pós-execução)

---

## Campo 8: Limites herdados da Fase 2 incorporados

### 8.1 Divergências materiais

| Divergência | Status na Fase 2 | Impacto em Fase 3 | Ação em Fase 3 |
|---|---|---|---|
| **D1: respondent_id ausente** | Documentado, NULL | Alto | Usar document_id como participant_master_id; decisão formal pendente |
| **D2: userId não é coluna** | Documentado, resolvido | Nenhum | Nenhuma ação — resolvido internamente |

### 8.2 Notas técnicas

| Nota | Status | Impacto | Ação |
|---|---|---|---|
| **N4: health_unit_key em organization.id** | Documentado, corrigido | Nenhum | Nenhuma ação — resolvido |
| **N7: event_timestamp não implementado** | Documentado | Alto em métricas de tempo | Proxy com journey_updated_at; marcar WARN |
| **N-IGI: não encontrado em fonte** | Documentado | Crítico | Métrica indisponível — documentar, não silenciar |

### 8.3 Campos indisponíveis

| Campo / Métrica | Causa | Impacto | Ação em Fase 3 |
|---|---|---|---|
| Eventos de notificação | Fora escopo Fase 2 | Crítico | Documentar como indisponível; requisito 6.4/6.9 incompleto |
| Eventos de chatbot | Idem | Crítico | Idem |
| Pedidos de ajuda | Idem | Crítico | Idem |

### 8.4 Pressuposição ZERO de produção

- ✅ Documentado em `fase-3-limites-herdados.md`
- ✅ Marca crítica a ser incluída em topo de cada script SQL de Etapa 3.2:
  ```sql
  -- AVISO: Views Fase 2 não rodadas em produção. 
  -- Todos os números são PROVISÓRIOS até homologação.
  ```

---

## Campo 9: Pendências (para continuidade da Fase 3)

### 9.1 Críticas (bloqueiam encerramento da Fase 3)

- [x] **Aprovação formal da Etapa 3.1** — Aprovada com ressalvas documentadas em parecer de auditoria (07/04/2026).
- [ ] **Implementação SQL das 3 marts mínimas** — `mart_ubs_monitoring_v1`, `mart_project_management_v1`, `mart_dashboard_export_v1`.
- [ ] **Queries de validação cruzada das marts** — comprovação técnica requisito ↔ métrica ↔ mart.
- [ ] **Verificação computacional de consumo sem parse estrutural adicional no dashboard**.
- [ ] **Consolidação final da Fase 3 (Etapa 3.5)** após implementação e validações técnicas.

### 9.2 Operacionais (podem executar em paralelo com Etapa 3.2)

- [ ] Validação de PII — revisor confirma zero PII nos marts?
- [ ] Checklist de programação letrada — código será legível?
- [ ] Teste lógico pré-BigQuery — queries rodáveis em SQL local/sandbox?

### 9.3 Pós-Etapa 3.4

- [ ] Execução de Fase 2 em BigQuery real (pré-requisito para validação dos marts)
- [ ] Homologação de contagens dos marts contra dados reais
- [ ] Aprovação de Fase 3 por revisor humano (checkpoint antes Fase 4)

---

## Campo 10: Pontos que exigem decisão humana

### 10.1 Decisão sobre D1 (`respondent_id`)

**Questão:** Fase 2 usou `document_id` como único ID. Campo `respondent_id` não existe em fonte bruta.

**Opções:**
A. Aceitar `document_id` como `participant_master_id` na v1 — continuar com implementação Fase 3 como está
B. Incorporar futuro `respondent_id` em exports de dados brutos — reprocessar Fases 2–3

**Recomendação:** Opção A (v1 com `document_id`); futura migração a `respondent_id` será nova fase.

**Requerido:** Aprovação formal do professor.

### 10.2 Decisão sobre N7 (`event_timestamp`)

**Questão:** Timestamps precisos de evento não estão em dados brutos. Proxy com `journey_updated_at` é aproximado.

**Opções:**
A. Aceitar proxy (`journey_updated_at`) para métricas de tempo — valores serão aproximados/underestimados
B. Deixar métricas de tempo como indisponíveis — não calcular tempos até dados melhores

**Recomendação:** Opção A (proxy com marca WARN em cada script); útil para agregações de nível UBS.

**Requerido:** Aprovação formal.

### 10.3 Aceitabilidade de métricas indisponíveis

**Questão:** 8 métricas não podem ser implementadas (IGI, notificações, chatbot, ajuda).

**Opção:**
- Aceitar incompletude — dashboard MVP funcionará sem estas métricas; backlog para futuro

**Impacto:** Requisitos 6.3 (IGI), 6.4 (notificações/chatbot), 6.9 (performance operacional) serão parcialmente ou não cobertos.

**Requerido:** Aceite explícito de stakeholder.

### 10.4 Pressuposição ZERO de produção

**Questão:** Views Fase 2 não foram rodadas em BigQuery real. Todos os números de Fase 3 são teóricos.

**Impacto:** Números do dashboard serão validados apenas após execução das views em BigQuery.

**Requerido:** Stakeholder confirma compreensão e aceitabilidade.

---

## Campo 11: Confirmações explícitas

### 11.1 Fase 3 foi executada no repositório GitHub institucional

✅ **Confirmado:**
- Todos os artefatos criados em: `/Users/.../proj_conemo/_clone_oficial_conemo/`
- Branch: `fase-3-construcao-marts-minimos` (criada de `fase-2-...`)
- Commits: 5 semânticos, auditáveis, com mensagens descritivas
- Nenhum trabalho fora do versionamento Git

### 11.2 Cláusula de governança foi incorporada e respeitada

✅ **Confirmado:**
- Governança obrigatória registrada em plano operacional
- Programação letrada obrigatória implementada (todos os docs incluem explicação natural)
- RULES.md e Workflow-Projeto.md consultados antes de qualquer ação
- Etapas de fluxo (Plano → Validação → Autorização) respeitadas
- Sem execução prematura de código SQL (Etapa 3.1 = documentação apenas)

### 11.3 Registro obrigatório de transição Fase 2 → Fase 3 foi seguido estritamente

✅ **Confirmado:**
- (1) Fase 2 entregou camada curada v1 documentada ✅ — registrado no plano
- (2) Pendência de homologação no BigQuery real ✅ — registrado em `fase-3-limites-herdados.md`
- (3) D1 em aberto ✅ — seção dedicada em limites-herdados
- (4) Fase 3 não pressupõe validação em produção ✅ — marca crítica "Pressuposição ZERO" será em cada script

**Todas as 4 observações integram formalmente escopo e documentação de Fase 3.**

### 11.4 Nenhuma atividade fora do escopo foi realizada

✅ **Confirmado:**
- ❌ Dashboard visual não foi adaptado (fora de escopo)
- ❌ Fase 4 não foi iniciada (bloqueada até aprovação Fase 3)
- ❌ D1 não foi "resolvido silenciosamente" (documentado como pendência)
- ❌ Camada curada não foi tratada como homologada (marca ZERO de produção)
- ❌ Parse estrutural não foi reintroduzido no Streamlit (marts consultam views, ponto)
- ❌ Nenhuma visualização de alertas detalhada foi construída
- ❌ Nenhuma timeline por participante foi construída
- ❌ Nenhuma regra de negócio foi alterada sem checkpoint

**Escopo autorizado foi respeitado integralmente.**

### 11.5 Fase 4 não foi iniciada

✅ **Confirmado:**
- Fase 4 está explicitamente fora de escopo deste relatório
- Nenhum artefato de Fase 4 foi criado
- Fase 4 será aberta apenas após aprovação formal de Fase 3
- Checkpoint de Fase 3 é obrigatório antes de qualquer movimento para Fase 4

---

## Resumo de conclusão

**Etapa 3.1 — Documentação de Fase 3 foi concluída e aprovada com ressalvas.**

- ✅ **5 documentos de especificação** (~1.825 linhas) produzidos
- ✅ **5 commits semânticos** auditáveis no GitHub institucional
- ✅ **Plano operacional** com arquitetura de 3 marts
- ✅ **Matriz de rastreamento** (requisitos → métricas → marts)
- ✅ **Regras de cálculo** de 25+ métricas
- ✅ **Documentação de limites** (D1, N7, N-IGI, campos indisponíveis)
- ✅ **Pressuposição ZERO de produção** registrada
- ✅ **RULES.md e Workflow-Projeto.md** seguidos
- ✅ **Governança incorporada**
- ✅ **Transição Fase 2 → 3** documentada

**Situação atual:**
- Etapa 3.1: **aprovada com ressalvas documentadas**
- Fase 3: **em aberto**
- Fase 4: **não autorizada**

**Aguardando:** execução da Etapa 3.2 e Etapa 3.3 para posterior consolidação final da Fase 3.

---

**Data de conclusão de Etapa 3.1:** 2026-04-07  
**Data de aprovação da Etapa 3.1:** 2026-04-07 (parecer de auditoria)  
**Data de autorização para Etapa 3.2:** [a preencher]  
**Aprovador:** [Professor/Revisor]

