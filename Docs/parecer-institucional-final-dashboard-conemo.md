# Parecer Institucional Final — Dashboard CONEMO (Etapa 6)

**Data:** 2026-05-03  
**Projeto:** CONEMO  
**Objeto:** decisão institucional sobre condições de PR, merge, deploy e operacionalização do dashboard  
**Escopo desta etapa:** parecer documental e decisório, sem execução de PR/merge/deploy e sem alteração técnica

---

## 1) Objeto e limite do parecer

Este parecer consolida a etapa institucional final após as validações técnicas e documentais já executadas no ciclo corrente do dashboard CONEMO.

Fora de escopo nesta etapa:
- abrir PR;
- executar merge;
- executar deploy;
- declarar o dashboard operacional.

---

## 2) Base normativa e evidências consideradas

Base normativa principal:
- `Docs/RULES.md`
- `Docs/Workflow-Projeto.md`
- `Docs/Plano-implementacao-dashboard.md`
- `Docs/passo4-reconciliacao-mvp-visual.md`

Evidências técnicas/documentais de fechamento:
- `Docs/nota-decisoria-nao-aderiu-dashboard.md`
- `Docs/validacao-final-integrada-nao-aderiu-dashboard.md`
- `Docs/relatorio-distribuicao-ubs-scores-phq-gad.md`
- `Docs/fase-6-checklist-qualidade.md`
- `Docs/fase-6-checklist-seguranca-pii.md`
- `Docs/fase-6-handoff-final.md`
- `Docs/fase-6-relatorio-conclusao-rodada.md`
- `Code/PY/dashboard_conemo.py` (estado canônico atual)

Referência histórica complementar (espelho institucional):
- `_clone_oficial_conemo/Docs/fase-d-saneamento-phq-gad.md`

---

## 3) Síntese executiva

As validações de Etapas 1–5 foram consideradas concluídas para o escopo autorizado, com confirmação dos pontos centrais:

1. Regra de negócio dinâmica de `Não Aderiu` preservada (`health_unit_key == "UNK_UHS"`), sem lista fixa de IDs e sem hard-code de contagens.
2. Separação analítica mantida entre `df_all`, `df_main` (Aderiu) e `df_nao_aderiu` (Não Aderiu).
3. Corte canônico operacional aplicado em `2026-01-28 00:00:00 UTC` (inclusivo) no arquivo canônico.
4. Governança e segurança/PII aprovadas com riscos residuais documentados.
5. Estado formal permanece **NÃO OPERACIONAL**.

---

## 4) Consolidação de resultados (Etapas 1–5)

### 4.1 Resultado consolidado

- Total atual observado: **238**
- `Aderiu`: **132**
- `Não Aderiu`: **106**
- `Não Aderiu` sem PHQ/GAD: **103**
- `Não Aderiu` com algum PHQ/GAD: **3**

### 4.2 Ressalva documental obrigatória (benchmark histórico vs estado corrente)

Fica registrada, de forma explícita, a divergência entre:
- benchmark histórico inicial: **105 / 102 / 3**;
- estado corrente de base: **106 / 103 / 3**.

Classificação institucional desta divergência: **esperada e aceitável**, por refletir variação real da base ao longo do tempo, sem alteração da regra de classificação.

---

## 5) Riscos e pendências classificadas

### 5.1 Bloqueantes para merge/deploy/operação

1. **Ausência de autorização formal da Coordenação** para transição de estado (pré-requisito de governança).
2. **Estado oficial ainda NÃO OPERACIONAL** em artefatos de validação e decisão.
3. **Necessidade de checklist institucional final de aceite de uso** (produto, segurança e operação) antes de qualquer publicação operacional.

### 5.2 Não bloqueantes imediatos (backlog controlado)

1. Warnings de ambiente local (OpenSSL/urllib3 e Python 3.9) sem evidência de impacto funcional crítico no escopo desta etapa.
2. Divergência de espelho (`_clone_oficial_conemo/Code/PY/dashboard_conemo.py`) com vestígio de corte antigo, classificada como saneamento documental/técnico posterior.
3. Ajuste de consistência menor na consulta individual auxiliar (apontamento de auditoria), sem impacto no gate institucional desta rodada.

---

## 6) Critérios decisórios por gate (PR, merge, deploy, operacionalização)

### 6.1 Gate PR (abertura de PR)

**Status recomendado:** `AUTORIZÁVEL COM CONDIÇÕES`.

**Status do PR (nesta etapa):** PR **ainda não aberto**; documentação apta para preparar PR **review-only** após confirmação final do estado Git (merge não autorizado).

Condições mínimas:
1. PR exclusivamente de consolidação rastreável desta rodada;
2. anexar este parecer e evidências de validação final;
3. explicitar ressalva de benchmark `105/102/3` vs `106/103/3` no corpo do PR;
4. incluir nota de saneamento planejado para o espelho institucional.

### 6.2 Gate merge em `main`

**Status recomendado:** `NÃO AUTORIZADO NESTE MOMENTO`.

Pré-condições para futura autorização:
1. aprovação formal da Coordenação registrada em artefato institucional;
2. revisão final dos pontos bloqueantes de governança;
3. confirmação de integridade documental entre canônico e espelho.

### 6.3 Gate deploy

**Status recomendado:** `NÃO AUTORIZADO`.

Pré-condições para futura autorização:
1. merge previamente autorizado e concluído;
2. decisão explícita de ambiente de publicação;
3. checklist de segurança/PII e operação assinado para contexto de uso real.

### 6.4 Gate operacionalização

**Status recomendado:** `NÃO AUTORIZADO`.

Pré-condições para futura autorização:
1. conclusão dos gates de merge e deploy;
2. validação institucional de uso pelos coordenadores;
3. formalização do termo de passagem de estado para operacional.

---

## 7) Decisão institucional desta etapa

**Decisão:** Etapa 6 (parecer institucional final) concluída com emissão de recomendação formal de gates.

Classificação final por gate:
- PR: **Autorizável com condições**;
- Merge: **Não autorizado neste momento**;
- Deploy: **Não autorizado**;
- Operacionalização: **Não autorizada**.

---

## 8) Plano mínimo de continuidade (sem execução nesta etapa)

1. Deliberação da Coordenação sobre abertura de PR de consolidação.
2. Se aprovado, anexação deste parecer e das evidências listadas na Seção 2.
3. Saneamento planejado do espelho institucional para convergência de corte canônico.
4. Nova checagem institucional final antes de qualquer decisão de merge/deploy/operação.

### 8.1 Ressalva menor de conferência final do repositório

Antes de usar este parecer como base para atualização do PR, recomenda-se solicitar ao executor uma confirmação curta de estado do repositório, preferencialmente com `git status --short`, declarando que:

- apenas o parecer institucional foi criado/alterado nesta etapa;
- nenhum código foi alterado;
- nenhum arquivo com PII foi criado ou preparado para commit;
- não houve alteração em BigQuery;
- não houve merge;
- não houve deploy;
- o dashboard permanece **NÃO OPERACIONAL**.

Na evidência local observável desta revisão, o workspace principal `proj_conemo` não está inicializado como repositório Git local, e o repositório Git disponível no espelho institucional `_clone_oficial_conemo` apresenta `M Code/PY/dashboard_conemo.py` em `git status --short`. Portanto, essa confirmação do executor permanece prudente antes de avançar para atualização do PR.

Ressalva de consistência temporal: a evidência de `git status` em `Docs/validacao-final-integrada-nao-aderiu-dashboard.md` refere-se ao momento da validação (2026-05-02). Este parecer registra a observação em 2026-05-03; divergências entre “limpo” vs “modificado” podem ocorrer por alterações posteriores e devem ser tratadas como diferença de timestamp, não como mudança de política (merge/deploy/operação seguem NÃO autorizados).

---

## 9) Declaração de encerramento do parecer

Este documento formaliza o posicionamento institucional final desta rodada para o dashboard CONEMO, preservando governança, rastreabilidade e controle de risco.

Até nova deliberação formal da Coordenação, permanece válida a diretriz:

> **sem merge, sem deploy e sem operacionalização.**
