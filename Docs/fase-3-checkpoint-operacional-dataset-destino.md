# Fase 3 — Etapa 2 preparatória antes da Etapa 3.2
# Checkpoint operacional final de prontidão (`firestore_curated`)

**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-07  
**Projeto:** CONEMO  
**Repositório:** `conemo-project/conemo` (clone institucional)  
**Branch desta etapa:** `fase-3-etapa-2-checkpoint-operacional-final`  
**Modo principal:** Auditoria e reconciliação → documentação técnica/handoff

---

## 1) Escopo desta execução (Etapa 2 apenas)

Esta execução realizou exclusivamente o checkpoint operacional final de prontidão antes da Etapa 3.2.

Incluído:
1. visibilidade do dataset `firestore_curated`;
2. leitura das fontes mínimas (`users_raw_latest`, `sessions_raw_latest`, `journeys_raw_latest`);
3. compatibilidade entre origem e destino (localização);
4. condição de escrita nos objetos autorizados da Etapa 3.2 por **dry-run**;
5. classificação final do ambiente.

Fora do escopo (respeitado):
- implementação de marts;
- criação de views da Etapa 3.2;
- alterações em dados brutos;
- alterações de regras de negócio;
- início da Etapa 3.2.

---

## 2) Pré-condição obrigatória

Pré-condição exigida: Etapa 1 concluída e aprovada formalmente.

Evidência considerada para execução desta Etapa 2:
1. Etapa 1 concluída e documentada em `Docs/fase-3-preparacao-dataset-destino.md`;
2. dataset `firestore_curated` criado e confirmado na Etapa 1;
3. autorização formal para executar Etapa 2 recebida na instrução explícita desta execução.

---

## 3) Fontes obrigatórias lidas

### 3.1 Canônicas
1. `Docs/RULES.md` (workspace canônico)
2. `Docs/Workflow-Projeto.md` (workspace canônico)
3. `Docs/Plano-implementacao-dashboard.md`
4. Plano Operacional de Pré-processamento de Dados aprovado (referenciado em Fase 0/Fase 1)

### 3.2 Base de fases anteriores
1. `Docs/fase-camada-sql-compartilhada-bigquery-sgbd.md` (Fase 0)
2. `Docs/fase-1-contrato-minimo-camada-compartilhada.md` (Fase 1)
3. `Docs/fase-2-verificacao-tecnica-bigquery.md` (Fase 2)
4. `Docs/fase-2-nota-tecnica-implementacao.md` (Fase 2)

### 3.3 Base da Fase 3
1. `Docs/fase-3-parecer-auditoria-2026-04-07.md`
2. `Docs/fase-3-limites-herdados.md`
3. `Docs/fase-3-nota-decisoria-dataset-destino-2026-04-07.md`
4. `Docs/fase-3-precheck-operacional-etapa-3-2.md`
5. `Docs/fase-3-precheck-operacional-log-saneado.md`
6. `Docs/fase-3-preparacao-dataset-destino.md`

---

## 4) Testes executados (checkpoint final)

> Todos os testes abaixo ocorreram sem criação de marts, sem criação de views da Etapa 3.2 e sem escrita efetiva em objetos de produção.

### T1 — Visibilidade do dataset de destino
- Comando: `bq ls --project_id=conemo-412202`
- Evidência: datasets visíveis `firestore_curated` e `firestore_export`
- Resultado: ✅ `firestore_curated` visível e confirmado

### T2 — Leitura das fontes mínimas
- Comando (users): `SELECT COUNT(*) FROM conemo-412202.firestore_export.users_raw_latest`
- Resultado: ✅ `459`

- Comando (sessions): `SELECT COUNT(*) FROM conemo-412202.firestore_export.sessions_raw_latest`
- Resultado: ✅ `7714`

- Comando (journeys): `SELECT COUNT(*) FROM conemo-412202.firestore_export.journeys_raw_latest`
- Resultado: ✅ `899`

Classificação T2: ✅ leitura funcional nas três fontes mínimas

### T3 — Compatibilidade origem × destino
- Origem: `conemo-412202.firestore_export`
- Destino: `conemo-412202.firestore_curated`
- Verificação de localização:
  - `SOURCE_LOCATION=southamerica-east1`
  - `TARGET_LOCATION=southamerica-east1`
- Resultado: ✅ compatibilidade confirmada

### T4 — Condição de escrita autorizada (sem extrapolar escopo)
- Comando: dry-run DDL em `southamerica-east1`
- Query: `CREATE OR REPLACE VIEW conemo-412202.firestore_curated.__perm_check_temp AS SELECT 1`
- Modo: `--dry_run`
- Resultado: ✅ validação bem-sucedida (0 bytes processados)
- Observação: nenhum objeto foi criado, por desenho de segurança do teste

### T5 — Integridade de escopo e segurança
Verificado:
1. nenhuma mart criada;
2. nenhuma view da Etapa 3.2 criada;
3. nenhum dado bruto alterado;
4. nenhum segredo exposto;
5. Etapa 3.2 não iniciada.

Resultado: ✅ conforme escopo autorizado

---

## 5) Diagnóstico consolidado por categoria de falha

| Categoria | Status | Evidência | Impacto operacional |
|---|---|---|---|
| Autenticação | OK | conta ativa de serviço confirmada | Sem bloqueio |
| Permissão | OK | leitura das 3 fontes + dry-run DDL válido | Sem bloqueio |
| Projeto incorreto | NÃO | projeto `conemo-412202` ativo | Sem bloqueio |
| Localização incompatível | NÃO | origem = destino = `southamerica-east1` | Sem bloqueio |
| Dataset ausente | NÃO | `firestore_curated` visível | Sem bloqueio |
| Ausência de objeto esperado | NÃO | fontes mínimas presentes e lidas | Sem bloqueio |
| Conflito ambiente local × alvo | RISCO BAIXO | warning recorrente de quota project ADC | Ressalva operacional não bloqueante |

---

## 6) Classificação final do ambiente

**Resultado final do checkpoint:** **APTO** *(reclassificado em 2026-04-07 após saneamento da ressalva ADC)*

Justificativa:
1. dataset de destino está visível e compatível;
2. leitura das fontes mínimas está funcional;
3. condição de escrita autorizada foi validada por dry-run sem extrapolação de escopo;
4. ~~ressalva operacional de quota project ADC~~ — **saneada**: `gcloud auth application-default set-quota-project conemo-412202` executado e confirmado operacionalmente com visibilidade normal do dataset `firestore_curated`.

---

## 7) Pendências e decisão humana

Pendências:
1. ~~ajuste institucional do quota project ADC~~ — **encerrado** (2026-04-07): confirmado operacionalmente via `bq`;
2. auditoria formal desta Etapa 2.

Decisão humana necessária:
- autorização formal para iniciar Etapa 3.2 (esta execução não a iniciou).

---

## 8) Conclusão formal da Etapa 2

O checkpoint operacional final de prontidão foi concluído de forma auditável no repositório institucional, em branch dedicada, com segurança e sem extrapolação de escopo. A ressalva operacional sobre quota project ADC foi saneada em 2026-04-07 e confirmada operacionalmente, resultando em reclassificação do ambiente.

Situação final:
- ambiente: **apto** para início controlado da Etapa 3.2;
- Etapa 3.2: **não iniciada**;
- criação de marts/views de marts: **não realizada**.
