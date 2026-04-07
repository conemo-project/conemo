# Fase 0 — Preparação e congelamento do escopo

## 1) Status da fase
- Status atual: **concluída para auditoria/checkpoint formal**.
- Data de registro: 2026-04-07.
- Execução limitada à abertura documental e governança de versionamento.

## 2) Objetivo da fase
Abrir formalmente a rodada da camada SQL compartilhada e congelar a lógica de trabalho antes de qualquer implementação técnica.

## 3) Modo principal da tarefa
- Modo principal: **Documentação técnica e handoff**.
- Sequência preservada para continuidade: **modelagem de dados** (após aprovação formal desta Fase 0).

## 4) Fontes canônicas utilizadas
1. `Docs/RULES.md` (fonte canônica consultada no workspace do projeto CONEMO).
2. `Docs/Workflow-Projeto.md` (fonte canônica consultada no workspace do projeto CONEMO).
3. `Docs/Plano-implementacao-dashboard.md`.
4. Plano Operacional de Pré-processamento de Dados já aprovado (minuta executiva validada em instrução do professor).

## 5) Decisão de arquitetura congelada
Fica congelada para esta rodada a decisão validada:
- implementação **BigQuery-first**;
- desenho **SGBD-first**;
- camada SQL intermediária compartilhada no BigQuery como base única para dashboard e SGBD.

Interpretação operacional desta fase:
- a decisão de arquitetura está registrada e não será rediscutida na Fase 0;
- qualquer implementação técnica só poderá iniciar após aprovação formal do checkpoint.

## 6) Escopo da Fase 0 (executar somente)
1. Confirmar fontes canônicas obrigatórias.
2. Registrar a decisão de arquitetura validada.
3. Registrar escopo imediato e fora de escopo.
4. Abrir este documento vivo da fase.
5. Incorporar cláusula de governança obrigatória da execução.
6. Criar e registrar branch própria da Fase 0 no repositório institucional.
7. Preparar checkpoint formal de aprovação antes da Fase 1.

## 7) Fora do escopo (Fase 0)
- Escrever SQL curado.
- Construir views, tabelas ou marts.
- Adaptar dashboard.
- Abrir Fase 1.
- Alterar regras de negócio já validadas.
- Executar qualquer implementação técnica além do artefato documental e do versionamento da Fase 0.

## 8) Cláusula de governança obrigatória da execução
A execução desta fase, e de todas as fases subsequentes do Plano de Pré-processamento de Dados, ocorrerá exclusivamente no repositório GitHub institucional do projeto CONEMO. Nenhuma fase será conduzida fora do fluxo de versionamento do projeto. Toda produção de código, consulta, script, notebook ou artefato técnico deverá seguir **programação letrada**, com explicação clara em linguagem natural, e obedecer integralmente ao `Docs/RULES.md` e ao `Docs/Workflow-Projeto.md`. Cada fase relevante deverá ter branch própria, commits auditáveis, documentação correspondente, pull request quando aplicável e revisão registrada antes do merge.

## 9) Entidades mínimas previstas para as próximas fases
1. participante atual;
2. UBS/município;
3. sessões;
4. jornadas;
5. escores clínicos básicos disponíveis;
6. métricas operacionais básicas por UBS/cidade.

Campos mínimos previstos para contrato inicial:
- `participant_id` (ou equivalente operacional documentado);
- `ubs_name`, `ubs_city`;
- `gender`, `risk`;
- `journey_id`, `session_number`, `is_completed`;
- `event_timestamp`;
- `journey_score` (quando disponível);
- flags de completude, consistência e exclusão de teste.

## 10) Riscos principais
1. Divergência entre o conteúdo canônico do workspace e os arquivos atualmente espelhados no clone institucional.
2. Duplicação futura de regra de negócio entre SQL e camada de aplicação.
3. Escolha inadequada de chave mestre na reconciliação (`document_id`, `userId`, `respondent_id`).
4. Vazamento de PII para camada de consumo visual.
5. Avanço indevido para implementação antes do checkpoint formal.

## 11) Critérios de validação da Fase 0
A Fase 0 é considerada válida se:
1. fontes canônicas estiverem explicitamente registradas;
2. decisão de arquitetura estiver congelada e inequívoca;
3. escopo e fora de escopo estiverem documentados;
4. cláusula de governança estiver incorporada integralmente;
5. branch própria da fase estiver criada e registrada;
6. não houver implementação técnica iniciada.

## 12) Checkpoint de aprovação
- Gate obrigatório: **aprovação formal do professor/revisor da Fase 0**.
- Condição para continuidade: autorização explícita para iniciar apenas a Fase 1 (contrato mínimo da camada compartilhada).

## 13) Identificação da branch da fase
- Repositório institucional: `conemo-project/conemo` (clone local institucional).
- Branch da Fase 0: `fase-0-camada-sql-compartilhada-bigquery-sgbd`.

## 14) Registro de rastreabilidade
### O que foi feito
- leitura integral das fontes canônicas obrigatórias disponíveis no workspace;
- abertura deste documento vivo da fase;
- registro da decisão de arquitetura congelada;
- registro de escopo, fora de escopo, riscos, critérios e checkpoint;
- criação e registro da branch própria da Fase 0.

### Por que foi feito
- para cumprir a abertura formal da rodada com ciclo curto e auditável;
- para impedir início de implementação sem congelamento de escopo e governança;
- para garantir alinhamento entre dashboard e SGBD antes da modelagem técnica.

### Quais fontes foram usadas
- `Docs/RULES.md`;
- `Docs/Workflow-Projeto.md`;
- `Docs/Plano-implementacao-dashboard.md`;
- Plano Operacional de Pré-processamento de Dados aprovado.

### O que foi validado
- aderência ao modo principal da fase (documentação técnica e handoff);
- aderência da decisão BigQuery-first/SGBD-first;
- aderência ao requisito de governança com branch dedicada;
- ausência de implementação técnica fora do escopo da Fase 0.

### O que ficou pendente
1. aprovação formal do checkpoint da Fase 0;
2. autorização explícita para abertura da Fase 1;
3. sincronização explícita, quando aplicável, das referências canônicas no clone institucional para eliminar divergência documental entre workspace e clone.
