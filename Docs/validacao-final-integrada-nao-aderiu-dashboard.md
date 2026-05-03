# Validação Final Integrada — Regra “Não Aderiu” (Etapa 5)

**Data:** 2026-05-02  
**Modo principal:** Auditoria e validação integrada  
**Executor técnico:** GitHub Copilot  
**Status do dashboard:** **NÃO OPERACIONAL**

---

## 1) Escopo desta etapa

Validação apenas (sem implementação nova), com foco em:

1. preservação da regra dinâmica de `Não Aderiu`;
2. integridade dos denominadores (`df_all`, `df_main`, `df_nao_aderiu`);
3. não contaminação das análises principais;
4. existência e isolamento da seção separada de monitoramento;
5. governança (sem alteração de BigQuery, sem merge, sem deploy).

---

## 2) Arquivos obrigatórios lidos

1. `Docs/RULES.md`
2. `Docs/Workflow-Projeto.md`
3. `README.md`
4. `Docs/nota-decisoria-nao-aderiu-dashboard.md`
5. `Docs/relatorio-distribuicao-ubs-scores-phq-gad.md`
6. `Docs/Plano-implementacao-dashboard.md`
7. `Code/PY/dashboard_conemo.py`
8. Equivalente canônico da Fase D: `_clone_oficial_conemo/Docs/fase-d-saneamento-phq-gad.md`

---

## 3) Regra dinâmica — verificação

### Evidência de regra por derivação (sem lista fixa)

No código do dashboard, `conemo_protocol_status` é derivado por regra operacional dinâmica baseada em `health_unit_key == "UNK_UHS"` e não por lista de IDs:

- função `_is_nao_aderiu(...)` e classificação derivada em `conemo_protocol_status`;
- criação dinâmica de `df_main` (`Aderiu`) e `df_nao_aderiu` (`Não Aderiu`).

### Resultado

- **Sem hard-code de contagem (105/106/132/238) no fluxo de classificação**;
- **Sem lista fixa de IDs para classificar `Não Aderiu`**;
- classificação recalculada a cada carga do DataFrame.

---

## 4) Validação de denominadores (estado corrente)

Consulta de validação executada em modo read-only (BigQuery) reproduzindo o pipeline de transformação do dashboard.

### Contagens observadas

- **Total geral pós-corte (`df_all`)**: 238
- **Total `Aderiu`**: 132
- **Total `Não Aderiu`**: 106
- **`Não Aderiu` sem score PHQ/GAD**: 103
- **`Não Aderiu` com algum score PHQ/GAD**: 3
- **Total nas análises principais (`df_main`/`df_users`)**: 132
- **Total da seção separada (`df_nao_aderiu`)**: 106

### Reconciliações (divergência residual no estado corrente)

- `N(df_main) = N(Aderiu)` → **132 = 132** ✅
- `N(df_nao_aderiu) = N(Não Aderiu)` → **106 = 106** ✅
- `N(df_all) = N(Aderiu) + N(Não Aderiu)` → **238 = 132 + 106** ✅
- usuários sem classificação (`conemo_protocol_status` nulo): **0** ✅

---

## 5) Benchmark canônico (105/102/3) vs estado corrente

### Benchmark de referência aprovado

- `Não Aderiu`: 105
- sem score no grupo: 102
- com score no grupo: 3

### Estado corrente observado

- `Não Aderiu`: 106
- sem score no grupo: 103
- com score no grupo: 3

### Interpretação da divergência

- diferença observada: **+1 caso `Não Aderiu`**, **+1 sem score**;
- coerente com base dinâmica atual (sem forçar ajuste manual);
- data mínima/máxima observada para `Não Aderiu`: **2026-01-28 11:15:07+00:00** até **2026-04-29 17:15:07+00:00**;
- houve **1 registro** no timestamp mais recente do grupo, compatível com entrada posterior ao retrato-base de benchmark.

**Conclusão:** benchmark histórico permanece válido como referência documental; estado corrente reconcilia corretamente com a regra dinâmica atual.

---

## 6) Exclusão de `Não Aderiu` das análises principais

Validado no código e em execução de reconciliação:

- cards principais, gráficos e tabela principal são derivados de `df_main`/`dff`/`df_users`;
- `Não Aderiu` em `df_main`: **0**.

### Pontos checados

1. cards principais;
2. distribuição por UBS;
3. médias PHQ/GAD;
4. indicadores clínicos agregados;
5. tabela principal (`Resumo por UBS`).

### Exportações principais

- não há rotina ativa de exportação (`download_button`/`to_csv`) nas análises principais desta versão.

---

## 7) Seção separada de monitoramento

A seção **“Monitoramento — Não Aderiu”** existe e permanece separada.

Validações:

- usa `df_nao_aderiu` como base do grupo monitorado;
- exibe agregados (totais, proporção, com/sem score, distribuição temporal, status territorial);
- inclui nota explícita de segregação do grupo;
- não reintegra `Não Aderiu` aos indicadores principais.

### PII na seção separada

- a seção separada não exibe nome/e-mail/CPF/telefone/endereço/contato alternativo;
- foco em agregados e qualidade de dados.

---

## 8) UBS/cidade e PHQ/GAD — validações específicas

### Filtros UBS/cidade

- filtros principais operam sobre `df_main` (aderentes);
- `UBS/cidade` continuam dimensão territorial;
- `Não Aderiu` continua status de adesão, separado (`conemo_protocol_status`).

### PHQ/GAD principal (contaminação)

Médias comparadas:

- média PHQ em `df_all`: **14.7985**
- média PHQ em `df_main`: **14.8015**
- delta (`df_main - df_all`): **+0.0030**

- média GAD em `df_all`: **12.9478**
- média GAD em `df_main`: **13.0000**
- delta (`df_main - df_all`): **+0.0522**

**Confirmação:** o dashboard principal usa `df_main`; portanto, os indicadores principais não são calculados com `Não Aderiu`.

---

## 9) Funcionamento local (execução)

### Comando executado

`/Users/ricardoceneviva/.../proj_conemo/.venv/bin/streamlit run Code/PY/dashboard_conemo.py --server.headless true --server.port 8503`

### Resultado

- app inicializado com sucesso;
- URL local gerada: `http://localhost:8503`;
- botão `🔄` e timestamp permanecem no código e carregamento;
- cache (`@st.cache_data`) preservado;
- sem erro impeditivo de inicialização.

Observação técnica: houve warning de ambiente (`NotOpenSSLWarning`), não impeditivo para subir localmente.

---

## 10) Governança e restrições

Confirmações desta etapa:

- **nenhuma alteração em BigQuery** (somente leitura);
- **nenhuma view/tabela/mart criada**;
- **nenhuma regra clínica alterada**;
- **nenhuma regra de elegibilidade alterada**;
- **nenhum alerta criado/alterado**;
- **sem merge**;
- **sem deploy**;
- dashboard permanece **NÃO OPERACIONAL**.

---

## 11) Estado Git e risco de rastreamento

### Workspace principal

- caminho principal (`proj_conemo`) não está com `.git` acessível no contexto atual (`fatal: not a git repository`).

### Clone oficial

- `_clone_oficial_conemo` está em Git (`is-inside-work-tree = true`);
- `git status --short`: **sem alterações listadas no momento desta validação (2026-05-02)**;
- `git status --short -- tmp_audit`: sem rastreamento listado.

Nota de governança: o estado Git é uma evidência pontual no tempo; revisões posteriores podem registrar modificações pendentes no clone oficial sem que isso implique merge/deploy/operação. Recomenda-se revalidar com `git status --short` imediatamente antes de preparar/atualizar o PR.

### Risco de PII local

- existe pasta local `tmp_audit/` com arquivos de listas de usuários (nomes de arquivos indicam potencial sensível);
- recomendação: manter fora de versionamento e sob controle de acesso local.

---

## 12) Critérios de aceite da Etapa 5 — checklist

1. regra dinâmica preservada ✅
2. benchmark 105/102/3 reconciliado como referência + divergência corrente explicada ✅
3. estado corrente com divergência residual zero nas partições validadas ✅
4. `df_main` contém apenas `Aderiu` ✅
5. `df_nao_aderiu` contém apenas `Não Aderiu` ✅
6. sem contaminação de gráficos principais ✅
7. seção separada de `Não Aderiu` correta ✅
8. filtros UBS/cidade preservados ✅
9. PHQ/GAD principais excluem `Não Aderiu` ✅
10. cache + botão `🔄` + timestamp preservados ✅
11. dashboard sobe localmente ✅
12. BigQuery sem alteração ✅
13. sem merge ✅
14. sem deploy ✅
15. dashboard permanece NÃO OPERACIONAL ✅

---

## 13) Pendências para auditoria final

1. validação visual humana final da interação dos filtros no navegador (QA funcional manual);
2. decisão de governança para padronizar o arquivo canônico da Fase D no mesmo diretório `Docs/` principal (hoje usado o equivalente em `_clone_oficial_conemo/Docs/`).
