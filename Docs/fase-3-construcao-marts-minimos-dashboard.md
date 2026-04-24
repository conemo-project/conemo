# Fase 3 — Construção dos marts mínimos para o dashboard

**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-07  
**Status:** Plano operacional — Etapa 3.1 (construção e documentação)  
**Branch:** `fase-3-construcao-marts-minimos`  
**Modo principal:** Indicadores e marts analíticos

---

## 1) Objetivo da Fase 3

Construir os **marts mínimos para consumo do dashboard**, derivados da camada curada mínima v1 entregue na Fase 2, **sem reintroduzir transformação estrutural no Streamlit** e **sem pressupor que a camada curada já foi validada em produção no BigQuery real**.

A Fase 3 focaliza indicadores e agregações operacionais para consumo em nível de **UBS e gestão do projeto**, preservando as ressalvas das Fases 0, 1 e 2 como restrições inerentes da implementação.

---

## 2) Cláusula de governança obrigatória da execução

A execução desta fase ocorre **exclusivamente no repositório GitHub institucional do projeto CONEMO**, com **branch própria dedicada**, **commits auditáveis pequenos** e **documentação integrada com programação letrada**.

Toda produção de código, consulta, script ou artefato técnico segue obrigatoriamente:
- `Docs/RULES.md` — especificamente: programação letrada, código interleado com explicação natural clara, marcação de fontes, respeito à evidência e ao domínio real do CONEMO.
- `Docs/Workflow-Projeto.md` — especificamente: fase dedicada com documentação, commits semânticos, validação de escopo, aprovação antes de avançar.

**Nenhuma atividade será iniciada fora deste fluxo.**

---

## 3) Registro obrigatório de transição da Fase 2 para a Fase 3

Esta fase mantém **explícitas** as seguintes condições herdadas de Fase 2:

1. **A Fase 2 entregou uma camada curada mínima v1 documentada** — cinco views SQL prontas para execução, com explicação natural integrada, regras de transformação documentadas e nota técnica. ✅

2. **Ainda há pendência de execução e homologação técnica no BigQuery real** — as views não foram executadas no ambiente de produção. O dataset `firestore_curated` não foi criado. As queries de validação não foram rodadas. Fase 2 permanece em estado de "código pronto, não validado em operação".

3. **A decisão sobre divergência material D1 (`respondent_id`) continua em aberto** — field completamente ausente da fonte física (`users_raw_latest`). Fase 2 documentou como `source_respondent_id = NULL` e `id_reconciliation_status = 'RESOLVED_DOCUMENT'`, preservando o contrato lógico v1 mas marcando pendência.

4. **Fase 3 não deve pressupor que a camada curada já foi validada em produção** — todos os cálculos de marts são derivados de views que ainda não rodaram em BigQuery com dados reais. A validação ocorrerá em paralelo ou após deployment das views.

**Essas quatro observações integram formalmente o escopo e as limitações da Fase 3. Nenhuma delas será "resolvida silenciosamente".**

---

## 4) Escopo autorizado da Fase 3

**Autorizado:**

1. ✅ Construir 3 marts mínimas SQL derivadas da camada curada:
   - `mart_ubs_monitoring_v1` — indicadores agregados por UBS
   - `mart_project_management_v1` — indicadores de gestão global do projeto
   - `mart_dashboard_export_v1` — tabela de exportação estruturada para Streamlit

2. ✅ Garantir aderência aos requisitos do dashboard conforme `Docs/Plano-implementacao-dashboard.md` (seções 1–8):
   - Foco em UBS/gestão (não individual)
   - Métricas agregadas (funil, progresso, atraso, conclusão)
   - Distribuição de escores por UBS
   - Indicadores operacionais por cidade/território

3. ✅ Documentar para cada métrica:
   - Numerador (definição)
   - Denominador (população)
   - Filtros aplicados
   - Janela temporal

4. ✅ Preservar a camada curada como base de consumo:
   - Marts consultam 5 views da Fase 2, não JSON bruto ou transformação no Streamlit

5. ✅ Registrar explicitamente limites herdados da Fase 2:
   - D1 não resolvido
   - D2 resolvido (document_id)
   - N7 não implementado (event_timestamp)
   - Pressuposição zero de homologação em produção

6. ✅ Documentação técnica e artefatos versionados no GitHub:
   - Scripts SQL com programação letrada
   - Notas de métricas (definições formais)
   - Tabela de validação cruzada requisito ↔ métrica ↔ fonte
   - Registro documental de fase

7. ✅ Preparar para checkpoint de aprovação antes da Fase 4

**Fora do escopo (proibido):**

- ❌ Adaptar dashboard visual (Streamlit)
- ❌ Abrir a Fase 4
- ❌ Tratar a camada curada como homologada em produção
- ❌ Resolver silenciosamente D1 (`respondent_id`)
- ❌ Construir visualização detalhada de alertas
- ❌ Construir timeline completa por participante
- ❌ Incorporar complexidade total de IGI (v1 apenas descritiva)
- ❌ Alterar regras de negócio já validadas sem checkpoint documental
- ❌ Reintroduzir parse estrutural no Streamlit

---

## 5) Arquitetura de marts (proposta v1)

A Fase 3 constrói 3 marts em SQL, todas consultando as 5 views curadas da Fase 2:

```
Camada A (bruta):                 Camada B (curada):               Camada C (marts):
users_raw_latest                  cur_participant_current_v1       
sessions_raw_latest       ──>     cur_health_unit_v1       ──>    mart_ubs_monitoring_v1
journeys_raw_latest               cur_journey_current_v1           mart_project_management_v1
                                  cur_session_current_v1           mart_dashboard_export_v1
                                  cur_score_current_v1
```

### 5.1 `mart_ubs_monitoring_v1`

**Granularidade:** 1 linha por UBS × período (agregada por dia ou semana).

**Propósito:** indicadores operacionais e clínicos por unidade de saúde, consumíveis para filtro e visão UBS no dashboard.

**Métricas esperadas (extraídas do Plano-implementacao-dashboard.md):**
- Volume de participantes por UBS
- Funil: iniciou web → concluiu web → elegível → baixou app → baseline
- Participantes ativos, atrasados, desistentes, concluídos
- Distribuição de escores (PHQ-9, GAD-7 por faixa de gravidade)
- Eventos operacionais agregados (notificações, chatbot, pedidos de ajuda)

**Fonte primária:** `cur_participant_current_v1` (participantes), `cur_health_unit_v1` (dimensão), `cur_session_current_v1` (progresso), `cur_score_current_v1` (escores).

### 5.2 `mart_project_management_v1`

**Granularidade:** 1 linha por período (agregada globalmente ou por cidade).

**Propósito:** visão executiva do projeto — cobertura total, tempos médios, desempenho operacional, comparabilidade entre UBS.

**Métricas esperadas:**
- Funil completo global (web → elegível → app → baseline → ativo em jornada)
- Tempos médios entre etapas
- Cobertura por cidade e UBS (proporção participantes / população-alvo teórica se disponível)
- Distribuição de atraso e abandono
- Consistência de dados (% com scores, % com atualização recente)
- Taxa de completação de jornada (por tipo)

**Fonte primária:** Agregação de todas as 5 views curadas.

### 5.3 `mart_dashboard_export_v1`

**Granularidade:** 1 linha por combinação de dimensões relevantes (participante + UBS + período + tipo de métrica).

**Propósito:** tabela estruturada, pronta para leitura pelo Streamlit, sem necessidade de transformação adicional.

**Conteúdo:**
- Dimensões: `participant_id`, `health_unit_key`, `ubs_name`, `ubs_city`, `period`, `journey_type`
- Métricas de fato: contagens, somas, médias de escores, flags de status
- Metadados: `data_quality_flag`, `timestamp_last_update`, `period_start`, `period_end`

**Nota:** esta mart é "de exportação", não é de consumo direto no dashboard mas serve para extrair subconjuntos CSV conforme necessário.

---

## 6) Fontes canônicas e artefatos da Fase 3

### 6.1 Leitura obrigatória (já concluída):
- ✅ `Docs/RULES.md` (460 linhas)
- ✅ `Docs/Workflow-Projeto.md` (653 linhas)
- ✅ `Docs/Plano-implementacao-dashboard.md` (V.2.1.0, versão final canônica)
- ✅ `Docs/fase-1-contrato-minimo-camada-compartilhada.md`
- ✅ `Docs/fase-2-verificacao-tecnica-bigquery.md`
- ✅ `Docs/fase-2-nota-tecnica-implementacao.md`

### 6.2 Artefatos a produzir:

| Artefato | Propósito | Tipo |
|---|---|---|
| Este documento (seção 3 adiante) | Plano operacional da Fase 3 | MD |
| `sql/fase3_mart_ubs_monitoring_v1.sql` | Implementation + literate programming | SQL |
| `sql/fase3_mart_project_management_v1.sql` | Implementation + literate programming | SQL |
| `sql/fase3_mart_dashboard_export_v1.sql` | Implementation + literate programming | SQL |
| `sql/fase3_validacao_marts_requisitos.sql` | Queries de validação cruzada | SQL |
| `Docs/fase-3-regras-metricas.md` | Definições formais de cada métrica | MD |
| `Docs/fase-3-validacao-requisitos-marts.md` | Tabela de rastreamento métrica ↔ requisito ↔ fonte | MD |
| `Docs/fase-3-limites-herdados.md` | Documentação de limites e pressuposto zero de produção | MD |

---

## 7) Plano de implementação por etapa

### **Etapa 3.1 — Documentação de requisitos e rastreabilidade** (Em execução)

**Objetivo:** mapear cada requisito do dashboard (per Plano-implementacao-dashboard.md) para métrica correspondente, campo de fonte na camada curada, e validação cruzada.

**Artefatos:**
- `Docs/fase-3-validacao-requisitos-marts.md` — matriz requisito → métrica → campo → source view
- `Docs/fase-3-regras-metricas.md` — definição formal de cada métrica (numerador, denominador, filtro, período)

**Validação:** revisor humano verifica se cada requisito está mapeado sem lacunas.

### **Etapa 3.2 — Implementação dos marts em SQL** (Sequência)

Criar 3 scripts SQL, cada um com:
- **Bloco de explicação natural:** objetivo, granularidade, fontes, regras de negócio, limites conhecidos herdados da Fase 2
- **SQL comentado:** queries bem formatadas, nomes de colunas descritivos, CTEs bem nomeadas
- **Bloco de notas:** decisões de implementação, hipóteses, validações internas esperadas

**Sequência recomendada:**
1. `mart_ubs_monitoring_v1` (mais específica)
2. `mart_project_management_v1` (derivável de `mart_ubs_monitoring_v1`)
3. `mart_dashboard_export_v1` (agregação final)

**Linguagem:** SQL (BigQuery dialect), com sintaxe `CREATE OR REPLACE VIEW` (estado será "proposto, não rodado").

### **Etapa 3.3 — Queries de validação cruzada** (Paralela a 3.2)

Criar bloco de queries que:
- Contam registros em cada mart
- Validam agregações (sum, count, avg por dimensão)
- Verificam coerência entre marts (ex.: participantes em `mart_ubs_monitoring_v1` ⊆ `cur_participant_current_v1`)
- Testam casos extremos (UBS com zero participantes, períodos vazios, etc.)
- Ligam cada métrica de mart a um campo de fonte curada

**Arquivo:** `sql/fase3_validacao_marts_requisitos.sql` (comentado, pronto para execução manual em BigQuery).

### **Etapa 3.4 — Documentação de limites herdados** (Paralela)

Criar documento explícito que registra:
- D1 ausente na Fase 2, presente nesta Fase 3 (pressuposto: usar `participant_master_id` sem prejuízo)
- D2 resolvido (document_id = $.id)
- N4 corrigido (`health_unit_key` de `organization.id`, não `path_params`)
- N7 não implementado (`event_timestamp` nesta v1)
- Pressuposição **zero** de homologação em produção das views da Fase 2
- Indicadores parcialmente observáveis ou indisponíveis registrados

---

## 8) Critérios obrigatórios de validação da Fase 3

A Fase 3 só será considerada **concluída** se houver verificação explícita de que:

✅ **1. Cada métrica do mart está ligada a um requisito do plano do dashboard**
   - Matriz de rastreamento produto da Etapa 3.1

✅ **2. O dashboard pode consumir os marts sem parse estrutural adicional**
   - Marts estão prontas para leitura pelo Streamlit via SQL de seleção simples (SELECT * WHERE filtro)

✅ **3. PII não entra na camada de consumo visual**
   - Nenhum campo de `pii_participant_identity`, email, CPF, nome completo nos marts

✅ **4. Ressalvas herdadas da Fase 2 permanecem explícitas**
   - Documentadas em cada script SQL e em `fase-3-limites-herdados.md`

✅ **5. Não há pressuposição indevida de homologação em produção da camada curada**
   - Nota clara em cada mart: "views da Fase 2 não foram validadas em BigQuery real"

✅ **6. Numeradores, denominadores, filtros e janelas estão documentados**
   - `fase-3-regras-metricas.md` completa

✅ **7. Artefatos técnicos seguem programação letrada**
   - SQL com explicação natural integrada; não código puro

✅ **8. Documentação permite auditoria por revisor humano**
   - Rastreabilidade métrica → campo → fonte clara
   - Decisões de transformação justificadas
   - Limites, hipóteses e pendências explícitas

---

## 9) Fora do escopo (reforço)

**Explicitamente proibido nesta fase:**
- ❌ Abrir Fase 4
- ❌ Visualização em Streamlit (dashboard visual)
- ❌ Resolução de D1 (respondent_id)
- ❌ Pressuposição de produção validada
- ❌ Timelines por participante (apenas agregadas)
- ❌ Visualização detalhada de alertas
- ❌ Análises causais (apenas descritivas)
- ❌ Novas regras de negócio não aprovadas

---

## 10) Dicionário preliminar de métricas (extraído do Plano-implementacao-dashboard.md)

### 10.1 Métricas de funil

| Métrica | Numerador | Denominador | Filtro | Período |
|---|---|---|---|---|
| `web_initiated` | COUNT(DISTINCT participant_id com registration) | — | — | Configurável (dia/semana/mês) |
| `web_completed` | COUNT(DISTINCT participant_id com screening web completo) | `web_initiated` | — | Configurável |
| `eligible_count` | COUNT(DISTINCT participant_id com elegibilidade=ELIGIBLE) | `web_completed` | — | Configurável |
| `app_downloaded` | COUNT(DISTINCT participant_id com baseline app preenchido) | `eligible_count` | — | Configurável |
| `baseline_completed` | COUNT(DISTINCT participant_id com baseline_submission não nulo) | `app_downloaded` | — | Configurável |

### 10.2 Métricas de progresso

| Métrica | Numerador | Denominador | Filtro | Período |
|---|---|---|---|---|
| `active_in_journey` | COUNT(DISTINCT participant_id com journey_status=ACTIVE) | `baseline_completed` | — | Configurável |
| `sessions_completed` | COUNT(DISTINCT participant_id,journey_id com session_status=COMPLETED) | `baseline_completed` × journey_type | — | Configurável |
| `sessions_overdue` | COUNT(DISTINCT participant_id,journey_id com session_status=OVERDUE) | `active_in_journey` | — | Configurável |
| `abandonment_rate` | COUNT(DISTINCT participant_id com journey_status=INACTIVE) | `baseline_completed` | — | Configurável |

### 10.3 Métricas de escores clínicos

| Métrica | Numerador | Observação | Filtro | Período |
|---|---|---|---|---|
| `avg_phq9_baseline` | AVG(score_value WHERE score_type='PHQ' AND score_source='FORM_INITIAL') | Escore inicial de rastreio | — | Período de coleta |
| `avg_gad7_baseline` | AVG(score_value WHERE score_type='GAD' AND score_source='FORM_INITIAL') | Escore inicial de rastreio | — | Período de coleta |
| `phq_distribution` | COUNT(DISTINCT participant_id) grouped by score_bucket (0-4, 5-9, 10-14, 15-19, 20-27) | Distribuição de gravidade | — | Período de coleta |
| `gad_distribution` | COUNT(DISTINCT participant_id) grouped by score_bucket (0-4, 5-9, 10-14, 15-20) | Distribuição de gravidade | — | Período de coleta |

### 10.4 Métricas de cobertura (gestão)

| Métrica | Numerador | Denominador | Observação | Período |
|---|---|---|---|---|
| `ubs_count_active` | COUNT(DISTINCT health_unit_key com ≥1 participante ativo) | Total de UBS no sistema | — | Configurável |
| `coverage_by_city` | COUNT(DISTINCT participante) | População-alvo teoricamente disponível por cidade (se dado disponível) | Parcialmente observável | Período |
| `quality_flag_ok_pct` | COUNT(DISTINCT participant_id com record_quality_flag='OK') | COUNT(DISTINCT participant_id) | Proporção de registros sem avisos | Configurável |

**Nota sobre métricas parcialmente observáveis:** o documento do dashboard menciona "quantas vezes o participante tentou mas não completou" — este indicador **não é coletado no sistema atual**. Será registrado em `fase-3-limites-herdados.md` como "indisponível".

---

## 11) Estrutura esperada dos arquivos

```
_clone_oficial_conemo/
├── Docs/
│   ├── fase-3-construcao-marts-minimos-dashboard.md      (este arquivo)
│   ├── fase-3-validacao-requisitos-marts.md              (Etapa 3.1)
│   ├── fase-3-regras-metricas.md                         (Etapa 3.1)
│   ├── fase-3-limites-herdados.md                        (Etapa 3.4)
│   └── [outros documentos da fase...]
├── sql/
│   ├── fase3_mart_ubs_monitoring_v1.sql                  (Etapa 3.2)
│   ├── fase3_mart_project_management_v1.sql              (Etapa 3.2)
│   ├── fase3_mart_dashboard_export_v1.sql                (Etapa 3.2)
│   └── fase3_validacao_marts_requisitos.sql              (Etapa 3.3)
```

---

## 12) Checkpoint obrigatório antes do merge

**Aprovação requerida para cada um dos seguintes:**

1. ✅ Mapeamento requisito → métrica (Etapa 3.1)
2. ✅ Implementação das 3 marts (Etapa 3.2)
3. ✅ Queries de validação (Etapa 3.3)
4. ✅ Documentação de limites (Etapa 3.4)
5. ✅ Ausência de PII nos marts
6. ✅ Programação letrada em todos os scripts SQL
7. ✅ Conformidade com RULES.md e Workflow-Projeto.md

**Só após aprovação formal do professor:** merge no branch main e fechamento de Fase 3.

---

## 13) Próximos passos (em ordem)

1. **Etapa 3.1:** Executar agora — criar documento de mapeamento requisitos × métricas
2. **Etapa 3.2:** Executar em sequência — implementar as 3 marts SQL
3. **Etapa 3.3:** Paralela a 3.2 — validação e queries de auditoria
4. **Etapa 3.4:** Paralela a 3.2–3.3 — documentação de limites herdados
5. **Etapa 3.5:** Relatório de conclusão com 11 campos obrigatórios
6. **Checkpoint formal:** Aprovação para Fase 4

---

**Data de aprovação do plano:** [a preencher após validação]  
**Aprovador:** [Professor/Revisor]

