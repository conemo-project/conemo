# Fase 3 — Pré-check operacional obrigatório antes da Etapa 3.2

**Data:** 2026-04-07  
**Projeto:** CONEMO  
**Branch:** `fase-3-precheck-operacional-etapa-3-2`  
**Status da Fase 3:** em aberto (apenas Etapa 3.1 aprovada)  
**Modo principal:** Auditoria e reconciliação + documentação técnica/handoff

---

## 1) Objetivo e escopo desta execução

Este artefato registra **exclusivamente** o pré-check operacional obrigatório para decidir se a Etapa 3.2 pode começar.

**Fora do escopo desta execução:**
- implementar marts;
- criar views de Fase 3;
- alterar dados brutos;
- alterar regras de negócio;
- iniciar Etapa 3.2 sem aprovação formal.

---

## 2) Fontes canônicas lidas antes da execução

### Obrigatórias (lidas integralmente)
1. `Docs/RULES.md`
2. `Docs/Workflow-Projeto.md`
3. `Docs/Plano-implementacao-dashboard.md`
4. `Docs/fase-camada-sql-compartilhada-bigquery-sgbd.md` (Fase 0 — documento vivo)
5. `Docs/fase-1-contrato-minimo-camada-compartilhada.md` (Fase 1 aprovada)
6. `Docs/fase-2-verificacao-tecnica-bigquery.md`
7. `Docs/fase-2-nota-tecnica-implementacao.md`
8. `Docs/fase-3-construcao-marts-minimos-dashboard.md`
9. `Docs/fase-3-relatorio-conclusao.md`
10. `Docs/fase-3-parecer-auditoria-2026-04-07.md`
11. `Docs/fase-3-limites-herdados.md`

### Observação sobre "Plano Operacional de Pré-processamento de Dados aprovado"
Não foi identificado arquivo separado com esse nome no clone institucional. A referência operacional aparece registrada em Fase 0/Fase 1 como fonte canônica validada por instrução do professor.

---

## 3) Registro obrigatório de transição preservado

Durante todo o pré-check, foram preservadas explicitamente as condições herdadas:
1. Fase 2 entregou camada curada mínima v1 documentada.
2. Há pendência de execução/homologação no BigQuery real.
3. D1 (`respondent_id`) permanece em aberto.
4. Fase 3 não pressupõe validação em produção.
5. Parecer de auditoria: somente Etapa 3.1 aprovada; Fase 3 em aberto.

---

## 4) Matriz de testes obrigatórios executados

> Todos os testes abaixo foram executados sem criação de marts, sem alteração de dados brutos e sem exposição de segredo.

### T1 — Variável de ambiente e caminho autorizado
- **Comando:** checagem de `GOOGLE_APPLICATION_CREDENTIALS` + existência do arquivo no caminho autorizado.
- **Resultado:**
  - variável inicialmente **não definida**;
  - arquivo de chave no caminho autorizado **encontrado**.
- **Classificação:** ✅ concluído com ressalva operacional (era preciso exportar a variável na sessão).

### T2 — Ferramentas CLI disponíveis
- **Comando:** `command -v gcloud` e `command -v bq`.
- **Resultado:** ambos disponíveis.
- **Classificação:** ✅ aprovado.

### T3 — Autenticação e projeto alvo
- **Comando:** `gcloud auth activate-service-account --key-file ...` + `gcloud config set project conemo-412202` + `gcloud auth list`.
- **Conta ativa confirmada:** `ricardo-ceneviva@conemo-412202.iam.gserviceaccount.com`
- **Projeto ativo confirmado:** `conemo-412202`
- **Classificação:** ✅ aprovado com ressalva menor (warning de quota project em ADC).

### T4 — Teste funcional BigQuery e visibilidade de datasets
- **Comando:** query `SELECT 1` via `bq query` + `bq ls` no projeto.
- **Resultado:**
  - query executada com sucesso;
  - dataset visível: `firestore_export`.
- **Classificação:** ✅ aprovado.

### T5 — Verificação de fontes brutas e camada curada esperada
- **Comando:** `bq ls conemo-412202:firestore_export` e `bq ls conemo-412202:firestore_curated`.
- **Resultado:**
  - `firestore_export` acessível com objetos esperados (incluindo `users_raw_latest`, `sessions_raw_latest`, `journeys_raw_latest`);
  - `firestore_curated` **não encontrado**.
- **Classificação:** ⚠️ bloqueio parcial (dataset de destino da camada curada ausente).

### T6 — Permissão de leitura nas fontes mínimas
- **Comando:** `COUNT(*)` em `users_raw_latest`, `sessions_raw_latest`, `journeys_raw_latest`.
- **Resultado:** sucesso nos 3 testes, com retorno de contagens.
- **Classificação:** ✅ aprovado.

### T7 — Verificação de autorização IAM
- **Comando:** `gcloud projects get-iam-policy ...` filtrando conta ativa.
- **Papéis identificados:**
  - `roles/bigquery.admin`
  - `roles/firebase.admin`
- **Classificação:** ✅ aprovado para leitura/escrita autorizada; ⚠️ ressalva de privilégio amplo (operar com disciplina de escopo).

### T8 — Compatibilidade de destino e teste DDL sem escrita (dry-run)
- **Comando:** `bq query --dry_run 'CREATE OR REPLACE VIEW ... firestore_curated ...'`.
- **Resultado:** falha por `Dataset conemo-412202:firestore_curated was not found in location US`.
- **Diagnóstico:**
  - dataset de destino ausente;
  - origem `firestore_export` em `southamerica-east1`.
- **Classificação:** ⚠️ bloqueio operacional para iniciar Etapa 3.2 sem preparação do destino.

### T9 — Verificação de escrita indevida
- **Procedimento:** nesta execução não foi rodado nenhum comando de criação efetiva (`CREATE VIEW`, `CREATE TABLE`, `bq mk` etc.).
- **Resultado:** nenhuma escrita realizada.
- **Classificação:** ✅ aprovado.

### T10 — Integridade de escopo
- **Verificação:** nenhuma mart da Etapa 3.2 foi criada; nenhuma regra de negócio alterada; nenhum dado bruto alterado.
- **Classificação:** ✅ aprovado.

---

## 5) Diagnóstico consolidado por categoria de falha

| Categoria | Status | Evidência | Impacto operacional |
|---|---|---|---|
| Autenticação | OK | conta ativa de serviço autenticada | Sem bloqueio |
| Permissão de leitura | OK | consultas nas 3 fontes brutas executadas | Sem bloqueio |
| Projeto incorreto | NÃO | projeto ativo `conemo-412202` confirmado | Sem bloqueio |
| Dataset ausente | SIM | `firestore_curated` não encontrado | Bloqueia início seguro da Etapa 3.2 |
| Ausência de objeto esperado | PARCIAL | fontes brutas presentes; destino curado ausente | Bloqueio parcial |
| Conflito ambiente local × alvo | RISCO BAIXO | warning de quota project ADC; localização `southamerica-east1` na origem | Exige ajuste/registro antes de Etapa 3.2 |

---

## 6) Permissões confirmadas para Etapa 3.2 (sem execução de implementação)

### Confirmado
- leitura em `conemo-412202.firestore_export.*`;
- autenticação funcional da conta de serviço;
- papéis IAM compatíveis com operações BigQuery.

### Não confirmado por inexistência do destino
- criação/substituição de objetos de marts no dataset-alvo da fase, porque o dataset `firestore_curated` não existe no ambiente testado.

### Implicação
A Etapa 3.2 **não deve iniciar** até decisão formal sobre o dataset de destino (criação e localização correta) e confirmação operacional correspondente.

---

## 7) Regras de segurança atendidas

- nenhum segredo foi commitado ou gravado em arquivo versionado;
- conteúdo da chave JSON não foi exposto;
- não houve alteração de dados brutos;
- não houve criação de marts;
- não houve escrita fora de objetos autorizáveis;
- ambiente não foi tratado como homologado apenas por autenticação funcional.

---

## 8) Conclusão do pré-check

**Classificação final do ambiente:** **APTO COM RESSALVAS**

### Justificativa
Ambiente autenticado, projeto correto e leitura de fontes confirmada. Porém, há ressalvas operacionais relevantes:
1. `firestore_curated` ausente (destino esperado da camada curada/continuidade);
2. teste DDL dry-run indica falha por dataset inexistente/localização;
3. warning de quota project em ADC deve ser tratado para evitar ruído operacional.

### Decisão operacional
- **Não iniciar Etapa 3.2 automaticamente.**
- Submeter este pré-check à aprovação formal.
- Após decisão humana, executar preparação de destino autorizada (se aprovada) e repetir check rápido de prontidão.

---

## 9) Pendências e decisões humanas necessárias

1. Confirmar oficialmente qual dataset de destino será usado na Etapa 3.2 (`firestore_curated` ou outro autorizado).
2. Se `firestore_curated` for o destino oficial, autorizar criação do dataset com localização compatível com a arquitetura da fase.
3. Confirmar política de quota project ADC para eliminar warning operacional.
4. Registrar checkpoint formal de "pré-check aprovado" antes de iniciar qualquer SQL de marts.

---

## 10) Rastreabilidade

- Repositório: clone institucional `conemo-project/conemo`
- Branch deste pré-check: `fase-3-precheck-operacional-etapa-3-2`
- Execução: somente testes de autenticação/permissão/visibilidade + documentação
- Etapa 3.2: **não iniciada**
- Fase 3: **permanece em aberto**
- Fase 4: **não autorizada**
