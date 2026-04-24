# Correção Pré-Merge PR #2: Filtro de Usuários Ativos (Corte: 2026-01-25)

## 1. Objetivo da Fase B
Completar, documentar e versionar a correção mínima do dashboard (Fase B) para que exiba apenas usuários/pacientes cadastrados a partir de uma data de corte específica.

## 2. Decisão Funcional do Corte
O filtro aplicado utiliza o critério `createdAt >= 2026-01-25`.

## 3. Justificativa
Alteração solicitada pelos diretores do projeto CONEMO, em substituição ao corte anterior (2026-01-01), visando refletir adequadamente a nova base de participantes ativos da rodada atual.

## 4. Arquivo Alterado
- `Code/PY/dashboard_conemo.py`

## 5. Ponto Exato de Aplicação do Filtro
O filtro foi aplicado na função `load_data()`, logo após a normalização do campo de timestamp com `pd.to_numeric(..., errors="coerce")`, garantindo robustez caso os dados venham ausentes ou mal formatados. Também foi adicionado o devido tratamento de exceção (NaN) no momento de exibir o gráfico de progresso de sessões (`.dropna(subset=["sessionNumber"])`) para evitar o erro de `IntCastingNaNError`.

## 6. Campo Usado para Data de Entrada
Foi utilizado o campo `createdAt` (convertido para segundos como `created_at_seconds`).

## 7. Regra de Exclusão de createdAt Ausente
Registros com `createdAt` ausente foram excluídos implicitamente e explicitamente ao utilizar `df["created_at_seconds"].notna()`.

## 8. Flags de Teste/Invalidade Excluídas
Foi extraída a flag `isTest` dos dados do usuário (`json_data_user`), e registros em que `isTest == True` foram excluídos da visualização (`~df["is_test"]`).

## 9. Contagens Antes/Depois no Parquet
- **Total antes do filtro:** 9053 registros (389 participantes únicos)
- **Total com createdAt ausente:** 55
- **Total com createdAt < 2026-01-25:** 8863
- **Total com createdAt >= 2026-01-25:** 135
- **Total excluído por flags de teste/invalidade (isTest):** 0
- **Total final após filtro de data e flags:** 135 registros (135 participantes únicos)

## 10. Contagens de Referência no BigQuery (Corte 2026-01-25)
- **Total de usuários na fonte bruta (`users_raw_latest`):** 482
- **Total com createdAt >= 2026-01-25:** 228
- **Total com createdAt < 2026-01-25:** 199
- **Total com createdAt ausente:** 55
- **Total pós-2026-01-25 sem flags brutas observáveis (`isTest != 'true'`):** 228
- **Contagens na camada curada (`cur_participant_current_v1`):**
  - Total geral: 481
  - Total com createdAt >= 2026-01-25: 228
  - Total pós-2026-01-25 sem `is_test_record`: 125

## 11. Validação Funcional Executada
O dashboard foi executado localmente via script Python chamando `load_data()` bem como o script inteiro, confirmando que:
- O app carrega sem erro global.
- `load_data()` executa com sucesso.
- Lógica de exibição das sessões foi robustecida para ignorar registros com `sessionNumber` ausente (NaN).

## 12. Limitações
- As contagens do Parquet local (`conemo_dados_consolidados_raw_04_03_2026.parquet`) diferem ligeiramente do BigQuery online devido à data de exportação/snapshot dos dados.
- O modo cache/local persiste utilizando o Parquet antigo até que o pipeline alimente um novo Parquet, ou que as chaves de acesso ao BigQuery sejam habilitadas pela interface.

## 13 a 18. Confirmações Obrigatórias
- **Confirmação de que SQL/marts não foram alterados:** Sim, nenhuma view SQL, CTE ou mart foi modificado.
- **Confirmação de que objetos BigQuery não foram alterados:** Sim, apenas consultas de leitura (SELECT) foram executadas.
- **Confirmação de que `enabled = true` não foi usado:** Sim, o filtro baseia-se estritamente na data de criação.
- **Confirmação de que `journey_status = ACTIVE` não foi usado:** Sim.
- **Confirmação de que o PR #2 não foi mergeado:** Sim, o pull request segue aberto na branch `fechamento-rodada-preparacao-pr`.
- **Confirmação de que nenhuma nova fase foi iniciada:** Sim, limitou-se ao escopo da Fase B exigida para o pre-merge.