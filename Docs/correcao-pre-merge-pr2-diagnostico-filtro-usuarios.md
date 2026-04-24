# Fase A — Diagnóstico controlado do filtro de usuários pré-merge PR #2

**Projeto:** CONEMO
**Repositório institucional:** `conemo-project/conemo`
**Branch:** `fechamento-rodada-preparacao-pr`
**PR relacionado:** `conemo-project/conemo#2`
**Tipo de tarefa:** documentação e handoff, com auditoria/reconciliação técnica
**Escopo:** diagnóstico somente. Nenhuma alteração funcional foi autorizada ou executada.

---

## 1) Objetivo da Fase A

Diagnosticar onde e como deve ser aplicada a regra operacional urgente:

> O dashboard operacional do CONEMO deve exibir apenas usuários ativos que entraram no projeto a partir de `2026-01-01`.

Esta fase não implementa filtro. Ela identifica campo temporal, critério observável de atividade, ponto técnico de aplicação e contagens preliminares.

---

## 2) Fontes lidas

### 2.1 Normas e workflow

- `Docs/RULES.md` — lido integralmente no diretório pai do workspace antes da execução. No clone institucional da branch atual, o arquivo não foi localizado.
- `Docs/Workflow-Projeto.md` — lido integralmente no diretório pai do workspace antes da execução. No clone institucional da branch atual, o arquivo não foi localizado.
- `README.md` — lido no clone institucional; o próprio README lista `Docs/RULES.md` e `Docs/Workflow-Projeto.md` como obrigatórios, mas esses arquivos não estão presentes no filesystem da branch atual.

### 2.2 Fontes documentais e PR

- `Docs/Plano-implementacao-dashboard.md`
- `Docs/fechamento-rodada-preparacao-pr.md`
- `Docs/Nota-Decisoria-Pull-Request-02.md`
- GitHub PR #2: confirmado via GitHub/`gh` como aberto, base `main`, head `fechamento-rodada-preparacao-pr`, sem merge.
- GitHub PR #2: lista de arquivos alterados consultada via conector GitHub; comentários do PR consultados e nenhum comentário foi retornado.

### 2.3 Fontes técnicas

- `Code/PY/dashboard_conemo.py`
- `Data/PARQUET/conemo_dados_consolidados_raw_04_03_2026.parquet` — leitura exploratória apenas, sem modificação.
- `sql/fase2_cur_participant_current_v1.sql`
- `sql/fase2_cur_journey_current_v1.sql`
- `sql/fase2_cur_session_current_v1.sql`
- `sql/fase3_mart_ubs_monitoring_v1.sql`
- `sql/fase3_mart_project_management_v1.sql`
- `sql/fase3_mart_dashboard_export_v1.sql`
- `Docs/fase-2-nota-tecnica-implementacao.md`
- `Docs/fase-5-nota-tecnica-integracao-dashboard.md`
- `Docs/fase-5-prova-conceito-bigquery-dashboard.md`
- `Docs/fase-5-tabela-compatibilidade-dashboard-esquema.md`

### 2.4 `AGENTS.md`

`AGENTS.md` não foi localizado no clone institucional da branch atual.

---

## 3) Ponto atual de carga e seleção do dashboard

O dashboard efetivamente usado está em `Code/PY/dashboard_conemo.py`.

O ponto central de carga é `load_data()`:

- `PARQUET_PATH` aponta para `Data/PARQUET/conemo_dados_consolidados_raw_04_03_2026.parquet`;
- `load_data()` executa `pd.read_parquet(PARQUET_PATH)`;
- em seguida normaliza `sessionNumber` e `isCompleted`;
- extrai `ubs_name`, `ubs_city`, `phq_score`, `gad_score`, `gender`, `age` e `user_name` de `json_data_user`;
- remove cidades inválidas ou vazias: `Fake City`, `N/A` e string vazia.

A seleção visual ocorre depois da carga:

- filtros de cidade e UBS usam `ubs_city` e `ubs_name`;
- a métrica "Participantes" usa `df_users = dff.drop_duplicates(subset="user_id")`;
- gráficos e tabela agregada também dependem de `user_id`, `phq_score`, `gad_score`, `isCompleted` e `sessionNumber`.

Conclusão técnica: no dashboard atual, o ponto único mais seguro para aplicar um filtro funcional, se autorizado na Fase B, é dentro de `load_data()`, após leitura e derivação mínima dos campos necessários. A documentação de Fase 5 confirma que o contrato de saída de `load_data()` é o ponto mínimo de adaptação do dashboard.

Evidências diretas:

- `Code/PY/dashboard_conemo.py`, linhas 19-22: definição de `PARQUET_PATH`;
- `Code/PY/dashboard_conemo.py`, linhas 50-52: leitura com `pd.read_parquet`;
- `Code/PY/dashboard_conemo.py`, linhas 110-145: derivação de campos do JSON e filtro atual de cidades inválidas;
- `Code/PY/dashboard_conemo.py`, linhas 258-267: deduplicação por `user_id` e métricas principais;
- `Docs/fase-5-nota-tecnica-integracao-dashboard.md`, linhas 52-58 e 82-89: confirmação documental de que `load_data()` é o ponto mínimo de adaptação.

---

## 4) Campo de data de entrada

### 4.1 Candidatos observados

| Candidato | Fonte observada | Cobertura em participantes únicos | Avaliação |
|---|---:|---:|---|
| `json_data_user.createdAt._seconds` | Parquet atual, dentro de `json_data_user`; SQL usa `DATA.$.createdAt._seconds` como `created_at` | 334/389 | Melhor candidato para data de entrada/criação do usuário. |
| `created_at` | `cur_participant_current_v1.created_at` no SQL | derivado de `DATA.$.createdAt._seconds` | Campo curado correspondente para camada BigQuery/mart. |
| `firstFormTs` | Coluna top-level do Parquet | 232/389 | Representa primeira submissão/formulário, não necessariamente entrada/criação. Cobertura menor e mínimo observado em 2016, exigindo cautela. |
| `updatedAt` | `json_data_user.updatedAt` | 242/389 | Atualização posterior, não entrada. |
| `termsOfConsentDate` | `json_data_user.termsOfConsentDate` | 232/389 | Aceite de termo, não entrada geral. |
| `lastBaselineDate` | `json_data_user.lastBaselineDate` | 135/389 | Evento posterior de baseline, não entrada. |
| primeira jornada/sessão | `enabled`, `lastAccessSeconds`, `sessionNumber` e SQL de jornadas/sessões | parcial | Evento terapêutico-operacional posterior; não representa entrada no projeto. |

### 4.2 Campo recomendado

O campo recomendado para representar "data de entrada no projeto" é:

- no dashboard atual: `json_data_user.createdAt._seconds`, parseado a partir de `json_data_user`;
- na camada SQL/BigQuery: `cur_participant_current_v1.created_at`, derivado de `DATA.$.createdAt._seconds`.

Justificativa:

1. o SQL curado documenta `created_at` como timestamp de criação para auditoria e séries temporais;
2. a origem é a coleção de usuários (`users_raw_latest`), não uma jornada ou sessão posterior;
3. candidatos como `firstFormTs`, `lastBaselineDate`, `lastAccessSeconds` e sessão inicial representam eventos posteriores ou parciais;
4. `firstFormTs` tem cobertura menor e valor mínimo observado em 2016, incompatível com uso automático como data de entrada sem reconciliação adicional.

Limitação: `createdAt` está ausente em 55 de 389 participantes únicos no Parquet atual. A Fase B deve tratar ausentes de forma explícita, sem incluí-los silenciosamente como pós-`2026-01-01`.

Evidências diretas:

- `sql/fase2_cur_participant_current_v1.sql`, linhas 82-85: extração de `DATA.$.createdAt._seconds`;
- `sql/fase2_cur_participant_current_v1.sql`, linhas 167 e 239: publicação de `created_at`;
- contagem exploratória do Parquet: 334/389 participantes com `createdAt` não nulo; 138 participantes com `createdAt >= 2026-01-01`; 55 ausentes.

---

## 5) Critério de usuário ativo

### 5.1 Critérios observados

| Critério | Fonte | Avaliação |
|---|---|---|
| `enabled` no Parquet | coluna top-level derivada de jornada | Indica jornada habilitada, não status geral do usuário. |
| `journey_status = ACTIVE` | `cur_journey_current_v1.sql`, derivado de `DATA.$.enabled` | Critério observável de jornada ativa. Não equivale necessariamente a "usuário ativo". |
| `active_participants_ubs` | `mart_ubs_monitoring_v1.sql` | Conta participantes com `journey_status = 'ACTIVE'` e `journey_updated_at` nulo ou recente. É regra de mart, não usada pelo dashboard atual. |
| presença no Parquet operacional atual | `Data/PARQUET/...` | Indica presença na base consumida pelo dashboard, mas não status ativo formal. |
| `isTestUser`, `invalid`, `organization.testEnvironment` | `json_data_user` | Flags úteis para exclusão de teste/invalidade, não para confirmar atividade. |

### 5.2 Diagnóstico

Não há, no dashboard atual, um campo claro de **status ativo/inativo do usuário**.

Há critério observável para **jornada ativa** (`enabled = true` / `journey_status = ACTIVE`), mas ele não deve ser automaticamente promovido a "usuário ativo" sem decisão do professor, porque:

1. o próprio SQL define `journey_status` como derivado de jornada, não como status mestre do participante;
2. no Parquet atual, todos os 144 participantes com `enabled = true` têm `createdAt < 2026-01-01`;
3. aplicar simultaneamente `createdAt >= 2026-01-01` e `enabled = true` manteria 0 participantes no dashboard atual;
4. o dashboard atual não usa `enabled` como filtro de atividade.

Evidências diretas:

- `sql/fase2_cur_journey_current_v1.sql`, linhas 48-49: `journey_status` é derivado de `DATA.$.enabled`;
- `sql/fase2_cur_journey_current_v1.sql`, linhas 70-79 e 130-144: extração de `enabled` e `lastAccess`;
- `sql/fase3_mart_ubs_monitoring_v1.sql`, linhas 122-130: cálculo de `active_participants_ubs` com `journey_status = 'ACTIVE'`;
- contagem exploratória do Parquet: 144 participantes com `enabled = true`; 0 participantes com `createdAt >= 2026-01-01` e `enabled = true`.

### 5.3 Regra observável mínima, dependente de decisão

Se a coordenação decidir que "ativo" nesta correção urgente deve significar "participante atualmente presente na base operacional consumida pelo dashboard, não marcado como teste/invalidado", a regra mínima observável poderia ser:

1. `createdAt >= 2026-01-01`;
2. `user_id` presente;
3. exclusão de registros com evidência de teste/invalidade:
   - cidade de teste (`Fake City`, `Test`, `Teste`, `TestCity`, `Teste City`);
   - `isTestUser = true`;
   - `invalid = true`;
   - `organization.testEnvironment = true`.

Essa regra é apenas proposta diagnóstica. Ela exige decisão do professor antes da Fase B.

---

## 6) Evidências sobre piloto, teste, carga e quebra

Foram encontradas evidências de teste/invalidade, mas não campos explícitos para piloto, carga ou quebra.

Campos/evidências observados:

- `isTestUser` em `json_data_user`: 12 participantes únicos com `True`;
- `invalid` em `json_data_user`: 8 participantes únicos com `True`;
- `organization.testEnvironment` em `json_data_user`: 6 participantes únicos com `True`;
- cidade de teste: 1 participante único com cidade em lista de teste;
- SQL `cur_participant_current_v1.sql`: já documenta exclusão de cidades de teste por `organization.city`, mas não cobre `isTestUser`, `invalid` ou `organization.testEnvironment`.

União preliminar de flags de teste/invalidade: 24 participantes únicos, 1.123 linhas de sessão/dataset.

Evidências diretas:

- `sql/fase2_cur_participant_current_v1.sql`, linhas 153-162: identificação de cidade de teste;
- `sql/fase2_cur_participant_current_v1.sql`, linhas 218-221: exclusão SQL apenas de `is_test_record` derivado de cidade;
- contagem exploratória do Parquet: `isTestUser = true` em 12 participantes, `invalid = true` em 8, `organization.testEnvironment = true` em 6 e cidade de teste em 1.

---

## 7) Contagens preliminares

Unidade principal: participantes únicos por `user_id`, pois o dashboard calcula "Participantes" com `drop_duplicates(subset="user_id")`. Linhas do dataset também são registradas como apoio, porque o Parquet tem granularidade usuário × sessão/jornada.

### 7.1 Base atual antes de qualquer filtro

| Medida | Participantes únicos | Linhas |
|---|---:|---:|
| Total no Parquet atual | 389 | 9.053 |

### 7.2 Data de entrada recomendada (`createdAt`)

| Condição | Participantes únicos | Linhas |
|---|---:|---:|
| `createdAt < 2026-01-01` | 196 | 8.860 |
| `createdAt >= 2026-01-01` | 138 | 138 |
| `createdAt` ausente | 55 | 55 |

### 7.3 Teste/invalidade

| Condição | Participantes únicos | Linhas |
|---|---:|---:|
| União `isTestUser`/`invalid`/`organization.testEnvironment`/cidade de teste | 24 | 1.123 |
| União de teste/invalidade entre `createdAt >= 2026-01-01` | 2 | não calculado separadamente |

### 7.4 Atividade por jornada (`enabled = true`)

| Condição | Participantes únicos | Linhas |
|---|---:|---:|
| `enabled = true` em pelo menos uma linha do usuário | 144 | 8.808 |
| sem `enabled = true` | 245 | 245 |
| `createdAt >= 2026-01-01` e `enabled = true` | 0 | 0 |

### 7.5 Permanência sob regras candidatas

| Regra candidata | Participantes únicos que permaneceriam | Linhas que permaneceriam | Interpretação |
|---|---:|---:|---|
| `createdAt >= 2026-01-01` apenas | 138 | 138 | Filtra piloto histórico, mas não exclui flags de teste/invalidade. |
| `createdAt >= 2026-01-01` e sem flags de teste/invalidade | 136 | 136 | Regra mínima observável se professor aceitar "ativo" como presença operacional atual não test/invalid. |
| `createdAt >= 2026-01-01` e `enabled = true` | 0 | 0 | Critério estrito de jornada ativa é incompatível com o objetivo operacional esperado no Parquet atual. |

---

## 8) Diagnóstico do ponto de aplicação do filtro

### 8.1 Camada de dados consumida pelo dashboard

O dashboard atual consome diretamente o Parquet local `Data/PARQUET/conemo_dados_consolidados_raw_04_03_2026.parquet`. Não há mart ou SQL no caminho de execução atual do Streamlit.

Como a Fase A não pode alterar dados, SQL ou marts, não há ação nessa camada.

### 8.2 Função de carga/preparação do dashboard

`load_data()` é o ponto técnico mais seguro para o dashboard atual, se a Fase B for autorizada:

- é o ponto único de leitura e preparo;
- já contém filtros documentados de cidade inválida/teste;
- todos os blocos visuais usam o `DataFrame` retornado por essa função;
- permite aplicar o filtro antes de métricas, gráficos e visão auxiliar.

### 8.3 Filtro explícito após carga

É tecnicamente possível, mas menos seguro do que `load_data()`, porque parte da lógica visual e auxiliar pode passar a depender de múltiplos objetos filtrados manualmente.

### 8.4 SQL/mart

SQL/mart não é o ponto recomendado para corrigir o dashboard atual, porque a aplicação Streamlit em uso não consome as marts diretamente. As marts são relevantes para a evolução BigQuery, mas a documentação de Fase 5 registra que a troca de fonte exige adaptação explícita do contrato de `load_data()`.

---

## 9) Recomendação técnica

Recomendação condicionada:

1. **Data de entrada:** usar `createdAt` (`json_data_user.createdAt._seconds` no dashboard atual; `created_at` na camada curada).
2. **Ponto técnico, se a Fase B for autorizada:** aplicar o filtro no dashboard, dentro de `load_data()`, após a leitura do Parquet e a extração dos campos necessários.
3. **Usuário ativo:** não há critério mestre claro. A Fase B deve aguardar decisão do professor sobre a regra de atividade.

Decisão recomendada para Fase B: **bloquear até decisão adicional do professor sobre o critério de "usuário ativo"**.

Se o professor aprovar a regra observável mínima descrita na seção 5.3, a Fase B pode avançar com filtro no dashboard, em `load_data()`, sem alterar SQL/marts nesta correção urgente.

---

## 10) Riscos e limitações

1. `Docs/RULES.md`, `Docs/Workflow-Projeto.md` e `AGENTS.md` não estão presentes no clone institucional da branch atual; a ausência deve ser tratada como achado de governança documental.
2. `createdAt` está ausente em 55 participantes únicos; a Fase B não deve incluí-los por padrão no recorte pós-`2026-01-01`.
3. `firstFormTs` não é recomendado como data de entrada por cobertura menor e por representar submissão/formulário, não criação do usuário.
4. `enabled = true` representa jornada habilitada, não status mestre de usuário ativo.
5. O critério estrito `createdAt >= 2026-01-01` + `enabled = true` resulta em 0 participantes no Parquet atual.
6. Há flags de teste/invalidade além da cidade de teste já tratada no SQL; a Fase B deve decidir se entram na regra urgente.
7. Nenhuma contagem foi validada contra BigQuery live nesta fase; as contagens são exploratórias sobre o Parquet consumido pelo dashboard.

---

## 11) Validação de escopo da Fase A

- Código funcional não alterado.
- SQL e marts não alterados.
- Dados não alterados.
- Campo de data de entrada identificado com limitação documentada.
- Critério de usuário ativo não identificado de forma inequívoca; limitação documentada.
- Ponto recomendado de aplicação justificado.
- Contagens preliminares produzidas sobre o Parquet atual.
- Fase B não iniciada.
- PR #2 confirmado como aberto e não mergeado.

---

## 12) Encaminhamento

A Fase A está documentalmente concluída como diagnóstico.

Antes de abrir Fase B, o professor deve decidir se "usuário ativo" significa:

1. jornada ativa (`enabled = true` / `journey_status = ACTIVE`), sabendo que isso zera o recorte pós-`2026-01-01` no Parquet atual; ou
2. presença operacional atual no dashboard, com `createdAt >= 2026-01-01` e exclusão de flags de teste/invalidade; ou
3. outro critério canônico ainda não localizado nesta Fase A.

Não executar Fase B sem essa decisão.
