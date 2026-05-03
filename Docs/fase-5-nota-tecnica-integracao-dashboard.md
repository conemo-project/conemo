# Fase 5 — Nota técnica de integração mínima do dashboard com a camada de consumo BigQuery

**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-08  
**Projeto:** CONEMO  
**Repositório institucional:** `conemo-project/conemo`  
**Branch desta fase:** `fase-5-prova-integracao-dashboard-bigquery`  
**Modo principal:** dashboard, relatórios e exportação  
**Sequência:** auditoria e reconciliação → integração de fontes → documentação técnica/handoff

---

## 1) Objetivo

Executar a Fase 5 como **prova controlada de integração** entre o dashboard atual em Streamlit e a camada de consumo derivada do BigQuery, sem reabrir Fases 1–4 e sem iniciar a Fase 6.

---

## 2) Fontes efetivamente lidas antes da execução

### 2.1 Fontes canônicas obrigatórias
1. `Docs/RULES.md`
2. `Docs/Workflow-Projeto.md`
3. `Docs/Plano-implementacao-dashboard.md`
4. `Docs/fase-camada-sql-compartilhada-bigquery-sgbd.md`
5. `Docs/fase-1-contrato-minimo-camada-compartilhada.md`
6. `Docs/fase-2-verificacao-tecnica-bigquery.md`
7. `Docs/fase-2-nota-tecnica-implementacao.md`
8. `Docs/fase-3-3-validacao-cruzada-marts.md`
9. `Docs/fase-3-3-parecer-auditoria-2026-04-08.md`
10. `Docs/fase-4-nota-aderencia-sgbd.md`
11. `Docs/fase-4-parecer-auditoria-2026-04-08.md`
12. `Code/PY/dashboard_conemo.py` (clone institucional)

### 2.2 Base obrigatória adicional — observação de fonte
Não há arquivo dedicado com o título exato **“Plano Operacional de Pré-processamento de Dados aprovado”** no clone institucional nesta data. A referência operacional correspondente permanece formalmente registrada nas fases anteriores e foi tratada como fonte vinculante já documentada em Fase 0/Fase 1/Fase 4.

### 2.3 SQL efetivamente lidos
- `sql/fase2_cur_participant_current_v1.sql`
- `sql/fase2_cur_health_unit_v1.sql`
- `sql/fase2_cur_journey_current_v1.sql`
- `sql/fase2_cur_session_current_v1.sql`
- `sql/fase2_cur_score_current_v1.sql`
- `sql/fase3_mart_ubs_monitoring_v1.sql`
- `sql/fase3_mart_project_management_v1.sql`
- `sql/fase3_mart_dashboard_export_v1.sql`

---

## 3) Fonte atual do dashboard e contrato de consumo vigente

O dashboard atual lê **um único Parquet local** com granularidade mista usuário × sessão × jornada.

### 3.1 Fonte atual
- arquivo: `Data/PARQUET/conemo_dados_consolidados_raw_04_03_2026.parquet`
- leitura: `pd.read_parquet(PARQUET_PATH)`
- ponto de entrada central: função `load_data()` em `Code/PY/dashboard_conemo.py`

### 3.2 Estruturas esperadas hoje pelo app
O contrato efetivo consumido pelo Streamlit inclui, entre outras, as seguintes colunas:

- `user_id`
- `json_data_user`
- `sessionNumber`
- `isCompleted`
- `completedDate`
- `email`
- campos derivados em memória a partir do JSON do usuário:
  - `ubs_name`
  - `ubs_city`
  - `phq_score`
  - `gad_score`
  - `gender`
  - `age`
  - `user_name`

### 3.3 Consequência arquitetural
O dashboard atual **não consome uma mart agregada diretamente**. Ele consome um dataset de baixa granularidade já “achatado”, ainda com conteúdo de participante, sessão e JSON bruto suficientes para derivar filtros, métricas agregadas e a visão individual auxiliar.

---

## 4) Ponto mínimo de adaptação identificado

O **ponto mínimo de adaptação** é o **contrato de saída da função `load_data()`**, e não apenas a linha de leitura do Parquet.

Justificativa:
1. a troca de `pd.read_parquet(...)` por uma leitura da camada BigQuery não basta por si só;
2. toda a lógica posterior assume que `load_data()` devolve um `DataFrame` com granularidade de participante/sessão e colunas derivadas do JSON;
3. as marts da Fase 3 entregam dados em granularidade **agregada**, principalmente por UBS, cidade e escopo de gestão.

### 4.1 Interpretação operacional
A menor adaptação segura e reversível para a Fase 5 é:
- introduzir um **adaptador de fonte** na fronteira de `load_data()`;
- permitir um modo controlado de leitura da camada de consumo BigQuery;
- alimentar apenas os blocos **compatíveis** com dados agregados;
- manter explicitamente fora desse modo os blocos que dependem de granularidade individual.

---

## 5) Delta entre o esquema atual do dashboard e o esquema das marts

### 5.1 Compatibilidade estrutural imediata
As marts validadas já suportam diretamente:
- filtros por `ubs_city` e `ubs_name`;
- navegação agregada UBS/gestão;
- contagens agregadas por UBS/cidade/global;
- médias agregadas de PHQ e GAD;
- timestamp de snapshot (`snapshot_timestamp`);
- preservação do botão `🔄` como elemento visual de recarga/cache;
- preservação do label MVP.

### 5.2 Incompatibilidades reais
As marts atuais **não entregam** o que o dashboard hoje usa para:
- visão individual por participante;
- lookup por `user_id`;
- exibição/mascara de e-mail;
- distribuição de gênero;
- distribuição de idade;
- tabela individual de sessões com `sessionNumber`, `isCompleted` e `completedDate`;
- parsing de `json_data_user` em tempo de execução.

### 5.3 Ponto sensível adicional
A métrica atual de **“Conclusão de Sessões”** no Streamlit usa taxa baseada em linhas de sessão (`isCompleted`). Essa métrica **não está disponível diretamente** nas marts da Fase 3 no mesmo formato do app atual. Há métricas relacionadas (`completed_journeys_count_ubs`, `overdue_sessions_count_ubs`), mas não a mesma base direta de cálculo por sessão exibida hoje no front-end.

---

## 6) O que precisa mudar e o que não precisa mudar

### 6.1 O que pode permanecer sem mudança substantiva
- filtros visuais por cidade e UBS;
- navegação principal UBS/gestão;
- timestamp exibido na sidebar;
- botão `🔄` como componente visível;
- label MVP;
- estrutura geral da página agregada, desde que alimentada por métricas agregadas.

### 6.2 O que exige adaptação explícita
- a função `load_data()`;
- o contrato interno de dados usado nos blocos de métricas;
- gráficos e tabelas que hoje assumem granularidade de `user_id`;
- o bloco de visão individual por participante;
- a métrica de conclusão baseada diretamente em `isCompleted`.

---

## 7) O que não deve ser feito no Streamlit

Nesta fase, **não deve** ser feito no front-end:

1. reconstruir pseudo-registros de participante a partir das marts agregadas;
2. reintroduzir transformação estrutural de dados no Streamlit para simular camada curada;
3. reimplementar regras de negócio já validadas nas Fases 2–4;
4. acoplar o dashboard a parsing de JSON das marts de exportação;
5. usar o app para recomputar elegibilidade, longitudinalidade ou eventos faltantes;
6. mascarar ausências estruturais como se fossem dados completos.

---

## 8) Riscos e limitações desta Fase 5

1. A prova executada foi **controlada e mínima**, sem refatoração ampla.
2. A workspace atual não trouxe uma rota operacional pronta de leitura live do BigQuery dentro do dashboard.
3. A camada validada da Fase 3 sustenta bem o consumo **agregado**, mas não substitui integralmente o dataset local detalhado usado pela visão auxiliar individual.
4. Limites herdados permanecem válidos: D1, N7, ausência de IGI observável e ausência de eventos operacionais completos.

---

## 9) Conclusão técnica

A integração mínima com o dashboard é **viável de forma parcial e controlada**, desde que o objetivo da Fase 5 seja restrito ao consumo **agregado UBS/gestão**.

Ela **não é viável “as is”** para o dashboard inteiro no formato atual, porque o app ainda depende de granularidade individual e de colunas não presentes nas marts da Fase 3.

### Veredito objetivo
- **Viável sem refatoração ampla:** visão agregada UBS/gestão baseada em marts.
- **Não viável sem adaptação adicional:** visão individual auxiliar, demografia derivada, tabela de sessões detalhada e taxa de conclusão baseada em linhas de sessão.

---

## 10) Confirmação de escopo

- Execução realizada apenas no repositório institucional.
- Cláusula de governança preservada.
- Apenas a Fase 5 foi executada.
- Fase 6 não foi iniciada.

---

## 11) Status após auditoria

- Situação da Fase 5: aprovada.
- Parecer formal registrado em `Docs/fase-5-parecer-auditoria-2026-04-08.md`.
