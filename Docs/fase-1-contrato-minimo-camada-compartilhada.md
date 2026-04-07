# Fase 1 — Contrato mínimo da camada compartilhada (BigQuery/SGBD)

## 1) Status da fase
- Status atual: **concluída para auditoria/checkpoint formal**.
- Data de registro: 2026-04-07.
- Modo principal: **Modelagem de dados**.
- Limite da fase: somente contrato lógico e documentação; sem implementação SQL.

## 2) Objetivo da Fase 1
Definir o contrato lógico mínimo da camada compartilhada antes de qualquer implementação SQL, preservando a arquitetura validada (**BigQuery-first na implementação** e **SGBD-first no desenho**).

## 3) Fontes canônicas efetivamente usadas
1. `Docs/RULES.md`.
2. `Docs/Workflow-Projeto.md`.
3. `Docs/Plano-implementacao-dashboard.md`.
4. Plano Operacional de Pré-processamento de Dados aprovado (instrução executiva vigente).
5. `Docs/fase-camada-sql-compartilhada-bigquery-sgbd.md` (Fase 0 aprovada/encerrada).

## 4) Cláusula de governança obrigatória da execução
A execução desta fase, e de todas as fases subsequentes do Plano de Pré-processamento de Dados, ocorrerá exclusivamente no repositório GitHub institucional do projeto CONEMO. Nenhuma fase será conduzida fora do fluxo de versionamento do projeto. Toda produção de código, consulta, script, notebook ou artefato técnico deverá seguir **programação letrada**, com explicação clara em linguagem natural, e obedecer integralmente ao `Docs/RULES.md` e ao `Docs/Workflow-Projeto.md`. Cada fase relevante deverá ter branch própria, commits auditáveis, documentação correspondente, pull request quando aplicável e revisão registrada antes do merge.

## 5) Ressalva de governança herdada da Fase 0
Permanece registrada a ressalva de possível divergência entre o workspace canônico e o clone institucional. Esta Fase 1 **preserva a ressalva**, sem tentar resolvê-la fora do escopo.

## 6) Escopo executado na Fase 1
1. Fixação da granularidade de cada entidade curada mínima.
2. Definição da estratégia de identificador mestre (`document_id`, `userId`, `respondent_id`).
3. Matriz `fonte bruta → entidade curada`.
4. Definição de domínios mínimos (sexo/gênero, risco, cidade, UBS, jornada, status de sessão, missingness).
5. Segregação explícita PII vs domínio analítico.
6. Registro de campos obrigatórios, opcionais e estados de ausência.
7. Nomeação de objetos mínimos da v1.
8. Preparação para checkpoint formal antes da Fase 2.

## 7) Fora do escopo (respeitado)
- Implementação SQL curado.
- Construção de views/tabelas no BigQuery.
- Construção de marts.
- Adaptação do dashboard.
- Abertura da Fase 2.
- Alteração de regras de negócio já validadas.

---

## 8) Contrato de chaves e granularidade

### 8.1 Estratégia de identificador mestre
**Princípio:** a camada compartilhada v1 adota `participant_master_id` como chave canônica analítica de integração, derivada por reconciliação de identificadores operacionais.

**Regra de reconciliação (prioridade):**
1. usar `respondent_id` quando existir e for válido;
2. na ausência, usar `userId` válido;
3. na ausência de ambos, usar `document_id` válido;
4. sem identificador reconciliável: registrar `participant_master_id = NULL` e `id_reconciliation_status = 'UNRESOLVED'` (registro não apto para joins analíticos críticos até saneamento).

**Campos de governança de chave (obrigatórios em todas as entidades com participante):**
- `participant_master_id`
- `source_document_id`
- `source_user_id`
- `source_respondent_id`
- `id_reconciliation_status` (`RESOLVED_RESPONDENT`, `RESOLVED_USER`, `RESOLVED_DOCUMENT`, `UNRESOLVED`)

### 8.2 Granularidade por entidade mínima
- `cur_participant_current_v1`: **1 linha por participante atual** (`participant_master_id`).
- `cur_health_unit_v1`: **1 linha por unidade de saúde padronizada** (`health_unit_key`).
- `cur_session_current_v1`: **1 linha por sessão de jornada por participante** (`participant_master_id` + `journey_id` + `session_number`).
- `cur_journey_current_v1`: **1 linha por jornada por participante** (`participant_master_id` + `journey_id`).
- `cur_score_current_v1`: **1 linha por escore/instrumento no recorte corrente por participante** (`participant_master_id` + `score_type` + `score_reference_date`).

---

## 9) Nomes e papéis dos objetos mínimos (v1)
1. `cur_participant_current_v1` — retrato analítico atual de participante (sem PII direta).
2. `cur_health_unit_v1` — domínio padronizado de UBS/cidade.
3. `cur_session_current_v1` — estado de sessões por jornada.
4. `cur_journey_current_v1` — estado de jornada por participante.
5. `cur_score_current_v1` — escores clínicos básicos disponíveis no recorte atual.

---

## 10) Matriz de mapeamento: fonte bruta → entidade curada

| Fonte bruta (camada A) | Entidade curada de destino | Papel no contrato |
|---|---|---|
| `users_raw_latest` | `cur_participant_current_v1` | Identificação operacional reconciliável, atributos demográficos analíticos e vínculo com UBS/cidade |
| `users_raw_latest` | `cur_health_unit_v1` | Origem primária de nome/código de UBS e cidade (com padronização) |
| `journeys_raw_latest` | `cur_journey_current_v1` | Estado da jornada por participante, tipo de jornada e timestamps de referência |
| `sessions_raw_latest` | `cur_session_current_v1` | Sessão por jornada/participante, progressão e status operacional |
| `journeys_raw_latest` + `sessions_raw_latest` + `users_raw_latest` | `cur_score_current_v1` | Escores clínicos básicos disponíveis e contexto mínimo de referência temporal |

---

## 11) Domínios mínimos (v1)

### 11.1 Sexo/gênero
- Campo curado: `gender`.
- Domínio canônico inicial: `FEMININO`, `MASCULINO`, `OUTRO`, `NAO_INFORMADO`.
- Normalização: trim, upper, remoção de variantes locais para domínio canônico.

### 11.2 Risco
- Campo curado: `risk`.
- Domínio canônico inicial: `BAIXO`, `MODERADO`, `ALTO`, `NAO_CLASSIFICADO`.
- Observação: não altera regra clínica; apenas padroniza representação operacional.

### 11.3 Cidade
- Campo curado: `ubs_city`.
- Normalização: remoção de espaços excedentes, harmonização de caixa, dicionário de equivalências.

### 11.4 UBS
- Campo curado: `ubs_name` + `health_unit_key`.
- Normalização: nome canônico, resolução de abreviações e variações ortográficas.

### 11.5 Jornada
- Campo curado: `journey_id`, `journey_type`.
- Domínio canônico inicial para `journey_type`: `DEPRESSION`, `ANXIETY`, `BOTH`, `UNKNOWN`.

### 11.6 Status de sessão
- Campo curado: `session_status`.
- Domínio canônico inicial: `NOT_STARTED`, `IN_PROGRESS`, `COMPLETED`, `OVERDUE`, `UNKNOWN`.

### 11.7 Missingness
- Campo curado transversal: `missing_code`.
- Domínio mínimo: `NA` (não se aplica), `NI` (não informado), `UNK` (desconhecido), `NULL_TECH` (ausência técnica).

---

## 12) Nota de segregação PII vs domínio analítico

### 12.1 Pertence a PII (não entra em camada analítica de consumo)
- CPF/documentos pessoais em formato identificável;
- telefones;
- e-mails;
- endereço completo;
- nome completo quando identificável diretamente;
- contatos alternativos e localizadores pessoais.

### 12.2 Pertence ao domínio analítico (permitido na camada compartilhada)
- `participant_master_id` pseudonimizado/reconciliado;
- atributos demográficos não identificáveis diretamente (ex.: `gender` padronizado);
- UBS/cidade padronizadas;
- estado de jornada/sessão;
- escores clínicos agregáveis e seus metadados operacionais de referência;
- flags de completude, consistência e exclusão de teste.

### 12.3 Regra operacional
Nenhum campo PII deve atravessar para entidades de consumo visual/analítico da camada compartilhada v1.

---

## 13) Dicionário mínimo de dados (com validação de campo completa)

### 13.1 `cur_participant_current_v1`

| Campo | Fonte identificada | Regra de extração | Regra de limpeza | Definição funcional | Justificativa de uso | Obrigatoriedade | Missingness |
|---|---|---|---|---|---|---|---|
| `participant_master_id` | `users_raw_latest.document_id/userId/respondent_id` | aplicar hierarquia de reconciliação de IDs | trim, validação de vazio, deduplicação por prioridade | chave canônica de participante na camada compartilhada | integrar entidades sem expor PII | obrigatório | sem valor => `UNRESOLVED` + exclusão de joins críticos |
| `source_document_id` | `users_raw_latest.document_id` | leitura direta do identificador bruto | trim | traço de origem do ID documental | auditoria/reprocessamento | opcional | `NULL_TECH` |
| `source_user_id` | `users_raw_latest.userId` | leitura direta | trim | traço de origem do ID de usuário | auditoria/reconciliação | opcional | `NULL_TECH` |
| `source_respondent_id` | `users_raw_latest.respondent_id` | leitura direta | trim e padronização textual | traço de origem do ID de pesquisa | reconciliação com núcleo SGBD | opcional | `NULL_TECH` |
| `id_reconciliation_status` | derivado | regra determinística da reconciliação | validação contra domínio fechado | estado da resolução de chave mestre | controle de qualidade e governança | obrigatório | nunca nulo |
| `gender` | `users_raw_latest.data` | parse de JSON do atributo de gênero | mapear variantes para domínio canônico | sexo/gênero analítico padronizado | segmentação descritiva | opcional | `NAO_INFORMADO`/`NI` |
| `risk` | `users_raw_latest.data` | parse de JSON de campo de risco disponível | normalizar para domínio de risco | nível de risco operacional documentado | priorização operacional agregada | opcional | `NAO_CLASSIFICADO`/`UNK` |
| `health_unit_key` | `users_raw_latest.data.path_params` | extrair chave de UBS/cidade e aplicar lookup | normalizar e deduplicar | chave padronizada da unidade de saúde | joins estáveis com dimensão de UBS | obrigatório | ausência => `UNK_UHS` com flag |
| `is_test_record` | `users_raw_latest.data` | extrair marcador de teste por regra documental | booleanização e default false | marcação de registro de teste | filtrar ruído operacional | obrigatório | default `false` |
| `record_quality_flag` | derivado | regra de consistência mínima de campos críticos | padronizar domínio `OK/WARN/FAIL` | semáforo de qualidade por linha | auditoria e troubleshooting | obrigatório | default `WARN` |

### 13.2 `cur_health_unit_v1`

| Campo | Fonte identificada | Regra de extração | Regra de limpeza | Definição funcional | Justificativa de uso | Obrigatoriedade | Missingness |
|---|---|---|---|---|---|---|---|
| `health_unit_key` | `users_raw_latest.data.path_params` | extrair identificador operacional de UBS | normalização textual/código | chave canônica da UBS | dimensão de referência para agregação | obrigatório | ausência => chave técnica `UNK_UHS` |
| `ubs_name` | `users_raw_latest.data` | parse de nome da UBS | trim, caixa, dicionário de equivalência | nome padronizado da unidade | consistência de filtros e agrupamentos | obrigatório | ausência => `NI` |
| `ubs_city` | `users_raw_latest.data` | parse da cidade associada | normalização ortográfica e de caixa | cidade padronizada da UBS | agregação por território | obrigatório | ausência => `UNK` |
| `health_unit_status` | derivado | classificar unidade ativa/inconsistente | domínio fechado (`ACTIVE/INACTIVE/UNKNOWN`) | estado operacional da unidade | controle de qualidade dimensional | opcional | `UNKNOWN` |

### 13.3 `cur_journey_current_v1`

| Campo | Fonte identificada | Regra de extração | Regra de limpeza | Definição funcional | Justificativa de uso | Obrigatoriedade | Missingness |
|---|---|---|---|---|---|---|---|
| `participant_master_id` | `journeys_raw_latest` + reconciliação com `users_raw_latest` | resolver IDs conforme contrato mestre | deduplicar por prioridade | chave de participante para a jornada | integração com participante/sessão | obrigatório | `UNRESOLVED` com flag |
| `journey_id` | `journeys_raw_latest.document_id/path_params` | extração do identificador da jornada | trim/normalização | identificador da jornada | unicidade por participante+jornada | obrigatório | não permitido sem flag crítica |
| `journey_type` | `journeys_raw_latest.data` | parse do tipo da jornada | mapear para domínio canônico | tipo de intervenção (depressão/ansiedade) | indicadores de progresso por jornada | obrigatório | `UNKNOWN` |
| `journey_status` | `journeys_raw_latest.data` | parse do estado operacional | normalizar para domínio fechado | situação atual da jornada | acompanhamento operacional | opcional | `UNKNOWN` |
| `journey_updated_at` | `journeys_raw_latest` timestamp | leitura do timestamp de atualização | padronização temporal UTC | última atualização conhecida da jornada | ordenação temporal e auditoria | obrigatório | `NULL_TECH` com flag |

### 13.4 `cur_session_current_v1`

| Campo | Fonte identificada | Regra de extração | Regra de limpeza | Definição funcional | Justificativa de uso | Obrigatoriedade | Missingness |
|---|---|---|---|---|---|---|---|
| `participant_master_id` | `sessions_raw_latest` + reconciliação | aplicar contrato mestre | deduplicação por prioridade | chave de participante da sessão | integração entre entidades | obrigatório | `UNRESOLVED` com flag |
| `journey_id` | `sessions_raw_latest.path_params` | parse do vínculo de jornada | normalização textual | vínculo da sessão à jornada | trajetória terapêutica | obrigatório | `UNK` com flag |
| `session_number` | `sessions_raw_latest.data` | parse do número/ordem de sessão | cast inteiro e validação de faixa | ordem da sessão na jornada | cálculo de progresso e atraso | obrigatório | `NULL_TECH` com flag |
| `is_completed` | `sessions_raw_latest.data` | parse do marcador de conclusão | booleanização e regra default | conclusão da sessão | indicadores de adesão/conclusão | obrigatório | default `false` |
| `session_status` | derivado de estado + conclusão + prazo | regra de classificação operacional | mapear para domínio canônico | estado padronizado da sessão | métricas agregadas estáveis | obrigatório | `UNKNOWN` |
| `event_timestamp` | `sessions_raw_latest` timestamp | leitura do timestamp do evento base | padronização UTC | tempo de referência da sessão | séries temporais operacionais | obrigatório | `NULL_TECH` com flag |

### 13.5 `cur_score_current_v1`

| Campo | Fonte identificada | Regra de extração | Regra de limpeza | Definição funcional | Justificativa de uso | Obrigatoriedade | Missingness |
|---|---|---|---|---|---|---|---|
| `participant_master_id` | reconciliação de `users_raw_latest`/`journeys_raw_latest`/`sessions_raw_latest` | aplicar contrato mestre | deduplicar por prioridade | chave de participante para escore | integração com demais entidades | obrigatório | `UNRESOLVED` com flag |
| `score_type` | `journeys_raw_latest`/`sessions_raw_latest.data` | parse do tipo de escore disponível | mapear para domínio (PHQ/GAD/IGI/OUTROS) | tipo de escore clínico | monitoramento clínico agregado | obrigatório | `UNKNOWN` |
| `score_value` | campos de score disponíveis na fonte bruta | parse do valor numérico | cast numérico e validação de faixa quando definida | valor do escore bruto/derivado disponível | indicadores clínicos por UBS/gestão | opcional | `NI`/`NULL_TECH` |
| `score_reference_date` | timestamp associado ao escore | extração do timestamp de referência | padronização UTC/data | data de referência do escore | comparação temporal e auditoria | obrigatório | `NULL_TECH` com flag |
| `score_quality_flag` | derivado | validar presença, faixa e coerência temporal | domínio `OK/WARN/FAIL` | sinalização de qualidade do escore | controle de confiabilidade analítica | obrigatório | default `WARN` |

---

## 14) Critérios de validação da Fase 1 (atendidos)
1. Cada campo documentado possui: fonte, extração, limpeza, definição funcional e justificativa.
2. Granularidade de cada entidade está explícita.
3. Estratégia de chave mestre está explícita e auditável.
4. Separação PII vs analítico está explícita.
5. Nomes e papéis dos objetos mínimos estão definidos sem ambiguidade.
6. Escopo da fase foi respeitado sem implementação técnica.

## 15) Checkpoint formal antes da Fase 2
- Gate obrigatório: aprovação formal do professor/revisor sobre este contrato lógico mínimo.
- Condição para avanço: autorização explícita para iniciar somente a Fase 2 (implementação SQL da camada curada mínima).

## 16) Registro de rastreabilidade
### O que foi feito
- contrato lógico mínimo consolidado para as cinco entidades v1;
- matriz fonte→curada produzida;
- dicionário mínimo de dados produzido;
- estratégia de identificador mestre documentada;
- segregação PII/analítico documentada;
- critérios de validação e checkpoint registrados.

### Por que foi feito
- reduzir ambiguidade antes da implementação SQL;
- evitar retrabalho entre dashboard e SGBD;
- garantir rastreabilidade, auditabilidade e governança por fase.

### O que foi validado
- aderência ao modo principal (modelagem de dados);
- aderência à cláusula de governança e ao fluxo de versionamento;
- aderência ao escopo (sem SQL, sem marts, sem adaptação de dashboard).

### O que ficou pendente
1. aprovação formal do checkpoint da Fase 1;
2. autorização explícita para abrir Fase 2;
3. confirmação final dos nomes físicos de campos brutos no momento da implementação (sem mudança conceitual do contrato).
