# Correção Pré-Merge PR #2: Filtro de Usuários Ativos (Corte: 2026-01-25)

## 1. Objetivo da Fase B
Executar a implementação cirúrgica do filtro operacional no dashboard para exibir apenas usuários elegíveis ao recorte pós-corte temporal definido, com validação técnica e rastreabilidade documental.

## 2. Decisão funcional do corte 2026-01-25
O filtro aplicado no dashboard utiliza o critério `createdAt >= 2026-01-25 00:00:00 UTC` (`1769299200`).

## 3. Justificativa
Alteração solicitada pelos diretores do projeto CONEMO para adequar o dashboard ao recorte operacional vigente da rodada atual.

## 4. Arquivo alterado
- `Code/PY/dashboard_conemo.py`

## 5. Ponto exato de aplicação do filtro
O filtro foi aplicado na função `load_data()`, após a extração dos campos de `json_data_user` e antes dos blocos visuais, no trecho que:
1. normaliza `created_at_seconds` com `pd.to_numeric(..., errors="coerce")`;
2. aplica o corte temporal em `created_at_seconds`;
3. exclui flags observáveis de teste/invalidade.

## 6. Campo usado para data de entrada
Foi usado `createdAt._seconds` (materializado como `created_at_seconds` no dashboard).

## 7. Regra de exclusão de `createdAt` ausente
Registros com `createdAt` ausente ou inválido são excluídos por `created_at_seconds.notna()` após a normalização numérica com `errors="coerce"`.

## 8. Flags de teste/invalidade excluídas (quando observáveis no Parquet)
Foram excluídos registros com qualquer uma das condições abaixo:
- `isTest = true`;
- `isTestUser = true`;
- `invalid = true`;
- `organization.testEnvironment = true`;
- cidade com padrão observável de teste (`test|teste|fake|load|carga|break|quebra`).

## 9. Contagens reais no Parquet (corte 2026-01-25)
Parquet consumido pelo dashboard: `Data/PARQUET/conemo_dados_consolidados_raw_04_03_2026.parquet`

- Total antes do filtro (linhas): **9053**
- Participantes únicos antes: **389**
- Total com `createdAt` ausente: **55**
- Total com `createdAt < 2026-01-25`: **8863**
- Total com `createdAt >= 2026-01-25`: **135**
- Total excluído por flags observáveis de teste/invalidade (no subconjunto pós-corte): **2**
- Total final após filtro de data e flags (linhas): **133**
- Participantes únicos depois: **133**

## 10. Contagens reais no BigQuery (corte 2026-01-25)
### Fonte bruta `conemo-412202.firestore_export.users_raw_latest`
- `total_bruto`: **482**
- `total_sem_created_at`: **55**
- `total_pre_corte`: **199**
- `total_pos_corte`: **228**
- `total_pos_corte_sem_flags`: **225**

### Camada curada `conemo-412202.firestore_curated.cur_participant_current_v1`
- `total_curado`: **481**
- `total_sem_created_at`: **54**
- `total_pre_corte`: **199**
- `total_pos_corte`: **228**

## 11. Validação funcional executada
Validações executadas nesta Fase B:
1. Inicialização local do Streamlit confirmada sem erro de aplicação (`streamlit run ...`).
2. Execução do script do dashboard em modo bare sem exceção fatal de lógica (`python Code/PY/dashboard_conemo.py`).
3. Estruturas de filtro por Cidade/UBS confirmadas no código (`multiselect`).
4. Seção de visão por participante confirmada no código (`Estatísticas por Participante` + `selectbox` de ID).
5. Botão `🔄` preservado.
6. `timestamp` de atualização do cache preservado.
7. Não há bloco explícito de exportação no arquivo atual; portanto, não houve regressão de exportação nesta fase.

## 12. Limitações
1. O dashboard continua consumindo snapshot Parquet local; portanto, contagens da UI podem divergir do BigQuery atual.
2. Avisos de ambiente (`pyarrow`/`streamlit` em sandbox) foram observados, sem impacto funcional no filtro implementado.
3. A validação visual foi técnica (subida da aplicação e checagens estruturais), sem auditoria de UX manual completa em navegador nesta etapa.

## 13. Confirmação: SQL/marts
Confirmado: **nenhum SQL/mart foi alterado**.

## 14. Confirmação: objetos BigQuery
Confirmado: **nenhum objeto BigQuery foi alterado** (somente `SELECT` de leitura).

## 15. Confirmação: `enabled = true`
Confirmado: **`enabled = true` não foi usado** como critério do filtro.

## 16. Confirmação: `journey_status = ACTIVE`
Confirmado: **`journey_status = ACTIVE` não foi usado** como critério do filtro.

## 17. Confirmação: PR #2
Confirmado em 2026-04-24 via `gh pr view`: **PR #2 aberto (`OPEN`) e não mergeado (`mergedAt = null`)**.

## 18. Confirmação: escopo
Confirmado: **nenhuma nova fase foi iniciada**. Esta execução permaneceu restrita à Fase B.
