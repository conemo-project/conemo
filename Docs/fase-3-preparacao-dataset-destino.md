# Fase 3 — Etapa 1 preparatória antes da Etapa 3.2
# Preparação formal do dataset de destino (`firestore_curated`)

**Data:** 2026-04-07  
**Projeto:** CONEMO  
**Repositório:** `conemo-project/conemo` (clone institucional)  
**Branch desta etapa:** `fase-3-etapa-1-preparacao-dataset-destino`  
**Modo principal:** Especificação funcional → auditoria e reconciliação → documentação técnica/handoff

---

## 1) Escopo estrito executado

Esta execução realizou **somente** a Etapa 1 preparatória, com foco em destino institucional da camada curada compartilhada.

Executado:
1. confirmação do dataset oficial de destino: `firestore_curated`;
2. confirmação de localização correta no BigQuery;
3. verificação de existência prévia;
4. criação controlada do dataset no projeto `conemo-412202` (pois não existia);
5. documentação auditável da operação.

Não executado (fora do escopo):
- implementação de marts;
- criação de views da Etapa 3.2;
- alteração de dados brutos;
- alteração de regras de negócio;
- início de Etapa 2;
- início de Etapa 3.2.

---

## 2) Fontes obrigatórias lidas antes da execução

### 2.1 Fontes canônicas obrigatórias
1. `Docs/RULES.md` (workspace canônico)
2. `Docs/Workflow-Projeto.md` (workspace canônico)
3. `Docs/Plano-implementacao-dashboard.md`
4. `Docs/fase-camada-sql-compartilhada-bigquery-sgbd.md` (Fase 0 — documento vivo)
5. `Docs/fase-1-contrato-minimo-camada-compartilhada.md` (Fase 1 aprovada)
6. `Docs/fase-2-verificacao-tecnica-bigquery.md`
7. `Docs/fase-2-nota-tecnica-implementacao.md`

### 2.2 Base obrigatória da Fase 3 (lida)
1. `Docs/fase-3-parecer-auditoria-2026-04-07.md`
2. `Docs/fase-3-relatorio-conclusao.md` (registro de que apenas Etapa 3.1 foi aprovada)
3. `Docs/fase-3-nota-decisoria-dataset-destino-2026-04-07.md`
4. `Docs/fase-3-precheck-operacional-etapa-3-2.md` (cláusula formal de pré-check e diagnóstico)
5. `Docs/fase-3-precheck-operacional-log-saneado.md`

### 2.3 Observação sobre o “Plano Operacional de Pré-processamento de Dados aprovado”
Não há arquivo separado com esse título no clone institucional nesta data. A referência operacional está formalmente registrada em Fase 0/Fase 1/Fase 3.

---

## 3) Decisões e parâmetros operacionais aplicados

- **Dataset oficial de destino:** `firestore_curated` (decisão formal prévia mantida).
- **Projeto alvo:** `conemo-412202`.
- **Localização correta:** `southamerica-east1` (compatível com `firestore_export`).
- **Conta de serviço ativa usada na execução:** `ricardo-ceneviva@conemo-412202.iam.gserviceaccount.com`.

Justificativa técnica e arquitetural:
1. alinhamento com arquitetura BigQuery-first aprovada;
2. materialização explícita da camada curada compartilhada para continuidade controlada da Fase 3;
3. eliminação do bloqueio operacional identificado no pré-check anterior (dataset ausente).

---

## 4) Evidências de execução (comandos e resultados)

### 4.1 Verificação de localização da origem e existência prévia do destino
- Evidência: `firestore_export` confirmado em `southamerica-east1`.
- Evidência: `firestore_curated` inexistente antes da operação.

### 4.2 Criação controlada do dataset de destino
Comando executado:

```bash
bq --location=southamerica-east1 mk --dataset \
  --description "Camada curada compartilhada CONEMO (destino formal Etapa 3.2, criado na Etapa 1 preparatória)" \
  conemo-412202:firestore_curated
```

Resultado:
- `Dataset 'conemo-412202:firestore_curated' successfully created.`

### 4.3 Verificação pós-criação
- `TARGET_DATASET=firestore_curated`
- `TARGET_LOCATION=southamerica-east1`

### 4.4 Check técnico de prontidão sem escrita (dry-run DDL)
Comando executado:

```bash
bq query --use_legacy_sql=false --location=southamerica-east1 --dry_run \
'CREATE OR REPLACE VIEW `conemo-412202.firestore_curated.__perm_check_temp` AS SELECT 1 AS ok'
```

Resultado:
- `Query successfully validated` (0 bytes processados)
- `DDL_DRY_RUN=SUCCESS`

---

## 5) Segurança e governança

Cuidados adotados:
1. nenhum conteúdo da chave JSON foi impresso;
2. nenhum segredo foi versionado;
3. nenhuma mart foi criada;
4. nenhuma view da Etapa 3.2 foi criada;
5. nenhum dado bruto foi alterado;
6. execução restrita ao repositório institucional e branch dedicada.

Ressalva operacional mantida:
- warning de quota project em ADC observado durante autenticação (`gcloud auth application-default set-quota-project` permanece pendente de decisão/ajuste institucional).

---

## 6) Resultado da Etapa 1

Classificação da Etapa 1:
- **Concluída com ressalvas**.

Motivo da ressalva:
- operação principal concluída com sucesso (dataset criado e validado), porém persiste warning operacional de ADC quota project.

Impacto operacional:
- bloqueio de ausência do dataset foi removido;
- ambiente fica preparado para novo checkpoint formal;
- **Etapa 3.2 continua não liberada automaticamente**, conforme nota decisória vigente.

---

## 7) Pendências e decisão humana requerida

Pendências:
1. validar institucionalmente o ajuste de quota project ADC (opcional, mas recomendado);
2. realizar auditoria/checkpoint formal desta Etapa 1.

Decisão humana requerida antes de avançar:
- autorização explícita para iniciar a Etapa 2 (ainda não iniciada).

---

## 8) Conclusão formal

A preparação formal do dataset de destino da camada curada compartilhada foi executada no repositório institucional, em branch dedicada, com rastreabilidade e segurança.

Situação final desta execução:
- dataset de destino (`firestore_curated`): **criado e confirmado**;
- projeto alvo (`conemo-412202`): **confirmado**;
- localização (`southamerica-east1`): **confirmada**;
- Etapa 2: **não iniciada**;
- Etapa 3.2: **não iniciada**.
