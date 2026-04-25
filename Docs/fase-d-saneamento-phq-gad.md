# Fase D — Saneamento e reintegração dos scores PHQ/GAD

## Fase D.1 — Diagnóstico da fonte dos scores PHQ/GAD

### 1. Objetivo
Diagnosticar a causa técnica da indisponibilidade dos scores PHQ-9 e GAD-7 no Dashboard e mapear as fontes BigQuery válidas para saneamento na Fase D.2.

### 2. Fontes internas consultadas
- `Docs/RULES.md`
- `Docs/Workflow-Projeto.md`
- `Docs/fase-c-integracao-bigquery.md`
- `Docs/fase-c1-diagnostico-integracao-bigquery-dashboard.md`
- `Code/PY/dashboard_conemo.py`

### 3. Fontes BigQuery inspecionadas
- `conemo-412202.firestore_curated.cur_score_current_v1` (View Quebrada)
- `conemo-412202.firestore_curated.cur_participant_current_v1` (Chaves)
- `conemo-412202.firestore_export.users_raw_latest` (Fonte Primária)
- `conemo-412202.firestore_export.journeys_raw_latest` (Fonte Secundária)

### 4. Consultas diagnósticas executadas
- Inventário de tabelas via `INFORMATION_SCHEMA.TABLES`.
- Auditoria de schema via `INFORMATION_SCHEMA.COLUMNS`.
- Amostragem de dados via `SELECT` e `bq show --view`.
- Inspeção de caminhos Firestore via `document_name`.

### 5. Inventário de fontes

| Dataset | Tabela/View | Tipo | Relevância para PHQ/GAD | Status |
| ------- | ----------- | ---- | ----------------------- | ------ |
| firestore_curated | `cur_score_current_v1` | VIEW | **Alta** (Fonte esperada) | **Erro de Parsing** |
| firestore_curated | `cur_participant_current_v1` | VIEW | Média (Chaves de Join) | OK |
| firestore_export | `users_raw_latest` | VIEW | **Alta** (Contém JSON triagem) | OK |
| firestore_export | `journeys_raw_latest` | VIEW | Média (Contém scores jornada) | OK |

### 6. Schema das fontes candidatas

| Fonte | Campo | Tipo | Nullable | Relevância | Observação |
| ----- | ----- | ---- | -------- | ---------- | ---------- |
| `cur_score_v1` | `score_value` | FLOAT64 | YES | Direta | Campo atualmente inacessível |
| `users_raw` | `data` | STRING | YES | Estrutural | Contém array `forms` com scores |
| `users_raw` | `path_params` | STRING | YES | Chave | Contém `userId` (Presente nesta tabela) |
| `journeys_raw`| `document_name` | STRING | NO | Chave | Contém `userId` no path da string |
| `journeys_raw`| `path_params` | STRING | - | - | **AUSENTE** nesta tabela (Causa do erro) |

### 7. Diagnóstico de `cur_score_current_v1`

| Item verificado | Resultado | Evidência | Impacto |
| --------------- | --------- | --------- | ------- |
| Disponibilidade | **Falha Crítica** | `Unrecognized name: path_params` | View não carrega dados |
| Causa Raiz | Bug de Referência | CTE `journey_scores` referencia coluna inexistente | Invalida o `UNION ALL` total |
| Localização PHQ | Presente (CTE1) | Extração via `data.forms[0].scores` | Correto em teoria, mas bloqueado |
| Localização GAD | Presente (CTE1) | Extração via `data.forms[0].scores` | Correto em teoria, mas bloqueado |

### 8. Matriz de localização PHQ/GAD

| Instrumento | Fonte | Campo/estrutura | Chave | Data | Granularidade | Status | Observação |
| ----------- | ----- | --------------- | ----- | ---- | ------------- | ------ | ---------- |
| PHQ-9 | `users_raw` | `data.forms[?].scores[?].score` | `document_id` | `forms.date` | Participante | Localizado | Triagem inicial |
| GAD-7 | `users_raw` | `data.forms[?].scores[?].score` | `document_id` | `forms.date` | Participante | Localizado | Triagem inicial |
| PHQ/GAD | `journeys_raw`| `data.score` | `document_name` | `timestamp` | Jornada | Parcial | Scores de progresso |

### 9. Mapeamento de chaves

| Chave | Fonte | Presente? | Unicidade | Join possível com dashboard? | Risco |
| ----- | ----- | --------- | --------- | ---------------------------- | ----- |
| `document_id` | `users_raw` | Sim | Sim (User) | Sim (via `source_user_id`) | Baixo |
| `document_name` | `journeys_raw` | Sim | Sim (Path) | Sim (Exige parsing de string) | Médio |
| `participant_master_id`| Curated | Sim | Sim | Sim (Chave mestre) | Baixo |

### 10. Hipótese diagnóstica

1. **Por que `phq_score` e `gad_score` ficaram nulos na Fase C?** 
   A view consolidada de scores (`cur_score_current_v1`) contém um erro de sintaxe SQL (referência à coluna `path_params` inexistente no dataset de jornadas). Para não bloquear o dashboard na Fase C, optou-se por retornar `NULL` temporariamente na query principal.
2. **Os dados existem?** 
   Sim. Os scores de triagem estão no JSON da `users_raw_latest` e os scores de jornada estão no JSON da `journeys_raw_latest`.
3. **Formato:** 
   Os dados aparecem como scores já calculados (ex: `{"type":"PHQ","score":27}`) dentro de arrays no Firestore.
4. **Caminho para D.2:** 
   A correção deve ocorrer na camada de dados (BigQuery), restaurando a funcionalidade da view de scores ou criando uma alternativa saneada.

### 11. Recomendação para D.2

**Recomendação: A. Corrigir `cur_score_current_v1`.**

- **Justificativa:** O erro é cirúrgico e puramente de referência. Corrigir a view existente restaura a integridade de todas as marts dependentes sem fragmentar o schema com "v2", "v3", etc.
- **Risco:** Baixo. A lógica de extração dos scores PHQ/GAD em si já parece correta na primeira CTE.
- **Dependências:** Acesso para `CREATE OR REPLACE VIEW`.

### 12. Limitações
- Scores de jornada (`PHQ_JOURNEY`, `GAD_JOURNEY`) exigem parsing do `document_name` para recuperar o ID do usuário, dado que a coluna `path_params` não está disponível.
- A amostragem confirmou scores extremos (PHQ 27, GAD 21), validando a necessidade de testes de faixa na Fase D.2.

### 13. Confirmações de escopo

[x] Não alterei código.
[x] Não alterei SQL persistente.
[x] Não criei view.
[x] Não criei tabela.
[x] Não criei mart.
[x] Não alterei objeto BigQuery.
[x] Não fiz deploy.
[x] Não alterei regras clínicas.
[x] Não alterei elegibilidade.
[x] Não removi nem anonimizei PII.
[x] Não registrei PII sensível no relatório.
[x] Não declarei o dashboard operacional.
[x] Não iniciei D.2.
[x] A recomendação para D.2 está documentada.

---
**Executor:** Gemini CLI Agent  
**Data:** 2026-04-24

## Fase D.2 — Contrato de dados e correção controlada de `cur_score_current_v1`

### 1. Objetivo
Registrar o contrato de dados e executar a correção controlada da view `cur_score_current_v1`, restaurando a disponibilidade dos scores PHQ/GAD no BigQuery.

### 2. Aprovação da Fase D.1
A Fase D.1 foi formalmente aprovada. O diagnóstico confirmou que a view falha devido à referência inexistente da coluna `path_params` no dataset de jornadas. A recomendação de correção cirúrgica da view foi aceita como caminho para a D.2.

### 3. Escopo da Fase D.2
- Definir contrato mínimo de dados.
- Salvar snapshot da definição atual (antes da correção).
- Testar SQL proposta em modo consulta (`SELECT`).
- Atualizar a view de forma controlada.
- Validar integridade dos dados pós-correção.

### 4. Itens fora do escopo
- Alteração do código do dashboard (`dashboard_conemo.py`).
- Reintegração de scores ao dashboard (Fase D.3).
- Alteração de regras clínicas ou elegibilidade.
- Deploy ou declaração de operacionalidade.

### 5. Contrato mínimo de dados

| Campo | Tipo esperado | Fonte | Regra de preenchimento | Obrigatório? | Observação |
|---|---|---|---|---|---|
| `participant_id` | STRING | `users_raw` / `journeys_raw` | ID mestre ou originário | Sim | Chave de ligação |
| `score_source` | STRING | Metadado | Nome da tabela raw | Sim | Rastreabilidade |
| `instrument` | STRING | Metadado | 'PHQ', 'GAD', 'PHQ_JOURNEY', etc. | Sim | Distinção de escala |
| `score_total` | FLOAT64 | JSON | Valor numérico extraído | Sim | `NULL` se ausente |
| `score_timestamp` | TIMESTAMP | JSON / Metadado | Melhor data disponível | Sim | Momento da submissão |
| `source_document_id` | STRING | Metadado | ID do documento Firestore | Sim | Trilha técnica |
| `score_rule_version` | STRING | Metadado | 'd2_v1' | Sim | Controle de versão |

**Regras do Contrato:**
1. Missing deve ser preservado como `NULL`. Não usar `COALESCE(..., 0)`.
2. O score `0` deve ser tratado como dado substantivo.
3. Nenhuma classificação clínica ou de risco deve ser feita nesta view.

### 7. SQL Aplicada
A lógica foi implementada usando `REGEXP_EXTRACT` para corrigir o erro de referência da coluna `path_params`. A SQL completa está versionada em `Docs/fase-d-cur_score_current_v1_applied.sql`.

### 8. Resultados dos Testes Pós-Correção
A view foi validada em 2026-04-24 com os seguintes resultados:
- **Disponibilidade:** ✅ View consultável sem erros.
- **Volume de dados:** 1402 registros recuperados (282 usuários únicos).
- **Integridade de Chaves:** ✅ `participant_id` não nulo em todos os registros.
- **Faixas Clínicas:**
    - PHQ: 0.0 a 27.0 (N=282 triagem + 280 jornada)
    - GAD: 0.0 a 21.0 (N=282 triagem + 279 jornada)
    - Outros: 0.0 a 28.0 (N=279)
- **Missing Data:** ✅ Preservado como `NULL` (1 registro detectado).

### 9. Limitações
- Scores de jornada exigem parsing do `document_name`. Se o path do Firestore mudar, a view precisará de atualização.

### 10. Recomendação para D.3
Prosseguir para a **Fase D.3 — Reintegração controlada ao dashboard**, substituindo as colunas nulas no Streamlit pela leitura da view `cur_score_current_v1`.

### 11. Confirmações Finais (Checklist)
[x] D.1 aprovada foi registrada.
[x] Contrato de dados dos scores foi documentado.
[x] Definição anterior da view foi salva (`before_d2`).
[x] Rollback foi documentado.
[x] SQL proposta foi testada como SELECT antes de alterar a view.
[x] Apenas `cur_score_current_v1` foi alterada.
[x] SQL aplicada foi salva.
[x] View consulta sem erro e retorna dados válidos.
[x] Nenhum código do dashboard foi alterado.
[x] Nenhuma regra clínica ou de elegibilidade foi alterada.
[x] Dashboard segue não operacional.

---
**Executor:** Gemini CLI Agent  
**Data:** 2026-04-24

