# Fase 3 — Log saneado das Etapas preparatórias (1 e 2)
# Dataset de destino `firestore_curated`

**Data:** 2026-04-07  
**Projeto:** CONEMO  
**Branch atual:** `fase-3-etapa-2-checkpoint-operacional-final`  
**Escopo do log:** evidências saneadas da preparação do destino e checkpoint final (sem início da Etapa 3.2)

---

## Bloco A — Evidências preservadas da Etapa 1 (preparação do destino)

### [A1] Contexto e autenticação
- Conta ativa confirmada: `ricardo-ceneviva@conemo-412202.iam.gserviceaccount.com`
- Projeto ativo confirmado: `conemo-412202`

### [A2] Localização da origem
- Dataset de origem verificado: `firestore_export`
- Localização confirmada: `southamerica-east1`

### [A3] Existência prévia do destino
- Verificação de `firestore_curated` antes da operação: **não existente**

### [A4] Criação controlada do destino
- Comando executado: `bq --location=southamerica-east1 mk --dataset conemo-412202:firestore_curated`
- Resultado: **sucesso**

### [A5] Verificação pós-criação
- Dataset de destino: `firestore_curated`
- Localização: `southamerica-east1`

---

## Bloco B — Evidências da Etapa 2 (checkpoint operacional final)

### [B1] Visibilidade do dataset de destino
- Verificação de datasets no projeto: `firestore_export` e `firestore_curated` visíveis
- Resultado: **OK**

### [B2] Leitura das fontes mínimas
- `users_raw_latest`: **459**
- `sessions_raw_latest`: **7714**
- `journeys_raw_latest`: **899**
- Resultado: **OK**

### [B3] Compatibilidade origem × destino
- Origem (`firestore_export`) localização: `southamerica-east1`
- Destino (`firestore_curated`) localização: `southamerica-east1`
- Resultado: **compatível**

### [B4] Condição de escrita autorizada (dry-run)
- Teste DDL dry-run em `southamerica-east1`: **sucesso**
- Resultado: `Query successfully validated` (sem criação de objeto)

---

## Controle de escopo e segurança (Etapas 1 e 2)

- marts criadas: **não**
- views da Etapa 3.2 criadas: **não**
- alteração de dados brutos: **não**
- alteração de regras de negócio: **não**
- exposição de segredo: **não**
- commit de chave/credencial: **não**

---

## Resultado operacional consolidado

- Etapa 1 (preparação do dataset): **concluída com ressalvas**
- Etapa 2 (checkpoint final): **apto com ressalvas**
- Etapa 3.2: **não iniciada**
- Ressalva remanescente: warning de quota project ADC (não bloqueante)
