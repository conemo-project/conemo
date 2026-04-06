# Fase C1 — Minuta executiva para o Agente Executor (abertura formal registrada no clone oficial)

**Data de registro:** 2026-04-06  
**Status:** Etapa 0 preparatória + Etapa 1 formal executadas no clone oficial — sem implementação funcional de P0/P1/P2  
**Modo principal:** Tipo F — dashboard, relatórios e exportação  
**Sequência secundária:** Tipo G — auditoria e reconciliação; Tipo H — documentação e handoff  
**Branch da fase:** `feat/dashboard-fase-c1-mvp-operacional`  
**Clone oficial utilizado:** `/Users/ricardoceneviva/Library/CloudStorage/GoogleDrive-ceneviva@gmail.com/.shortcut-targets-by-id/15FNAS0mfcKcdeIjRa8PNbvlMpwoj1tu6/proj_conemo/_clone_oficial_conemo`  
**Remoto validado:** `https://github.com/conemo-project/conemo.git`

> Esta minuta deriva do plano operacional aprovado e deve ser executada com estrita aderência ao `RULES.md`, ao `Workflow-Projeto.md` e à base executiva canônica do dashboard. O projeto exige fluxo curto, auditável, reprodutível e sem avanço automático para nova fase. Toda entrega substancial deve deixar trilha inspecionável por outro revisor.

## Registro de abertura formal no clone oficial

- abertura executada no clone oficial após integração mínima do conteúdo local validado;
- integração restrita a `README.md`, documentos canônicos em `Docs/`, `Code/README.md` e `Code/PY/dashboard_conemo.py`;
- nenhuma implementação funcional do dashboard foi iniciada nesta etapa;
- `Code/PY/dashboard_conemo.py` foi apenas integrado ao clone oficial, sem edição.

---

## 1. Objetivo executivo da fase

Implementar a rodada inicial de melhoria do dashboard, já aprovada, como **início formal do ciclo contínuo de desenvolvimento** do dashboard, com **GitHub obrigatório**, preservando integralmente o escopo funcional P0/P1/P2 já validado:

* **P0**

  * exibir `timestamp` da última atualização do cache;
  * reorganizar a navegação principal para priorizar UBS/gestão;
  * manter o botão `🔄`;
* **P1**

  * corrigir cidade vazia no filtro;
  * normalizar duplicidade de cidade por caixa/variação;
* **P2**

  * incluir label discreto de versão MVP, apenas se não ampliar escopo.

## 2. Fontes canônicas obrigatórias

O executor deve trabalhar com esta hierarquia:

1. instruções explícitas do professor;
2. `Docs/Plano-implementacao-dashboard.md` final;
3. `Docs/RULES.md`;
4. `Docs/Workflow-Projeto.md`;
5. plano operacional aprovado desta fase.

## 3. Arquivos autorizados

**Arquivo técnico principal**

* `Code/PY/dashboard_conemo.py`

**Arquivos documentais complementares, se necessários**

* `Docs/fase-dashboard-executiva-1.md`
* `README.md`
* `Code/README.md`
* `Docs/README.md`

Nenhum outro arquivo deve ser alterado sem nova autorização. Isso é consistente com o workflow do projeto: executar apenas a fase aprovada, nos arquivos autorizados, sem abrir nova frente.

## 4. Escopo e fora de escopo

### Dentro do escopo

* ajustes locais no dashboard para P0/P1/P2;
* preservação das exportações CSV agregadas;
* criação de branch;
* commits pequenos e rastreáveis;
* abertura de PR;
* revisão antes do merge;
* registro documental mínimo da fase.

### Fora do escopo

* credenciais, segredos, BigQuery, integrações externas e deploy;
* refatoração ampla;
* reestruturação do repositório;
* mudança de regras clínicas ou motor de alertas;
* promoção da visão individual a eixo principal da navegação;
* CI/CD ou novas automações de governança.

---

# 5. Sequência exata de execução no GitHub

## Etapa 0 — Preparação local

Antes de editar qualquer arquivo:

1. atualizar `main` local com a versão corrente do repositório;
2. confirmar que a base a ser usada corresponde ao estado aprovado da Fase C;
3. confirmar que apenas `Code/PY/dashboard_conemo.py` será alterado tecnicamente, salvo documentação mínima autorizada.

## Etapa 1 — Criar branch da fase

Nome recomendado da branch:

```bash
git checkout main
git pull origin main
git checkout -b feat/dashboard-fase-c1-mvp-operacional
```

**Regra:** não trabalhar diretamente na `main`.

## Etapa 2 — Registrar abertura documental mínima

Se for necessário deixar rastro da abertura da fase, criar ou atualizar:

* `Docs/fase-dashboard-executiva-1.md`

Conteúdo mínimo:

* objetivo da fase;
* backlog P0/P1/P2;
* arquivo principal autorizado;
* branch utilizada;
* itens fora de escopo;
* critérios de validação.

**Commit recomendado**

```bash
git add Docs/fase-dashboard-executiva-1.md
git commit -m "docs: abre fase executiva C1 do dashboard"
```

Esse passo é desejável porque o projeto exige trilha documental e handoff revisável.

## Etapa 3 — Implementar P0

Editar `Code/PY/dashboard_conemo.py` para:

* exibir `timestamp` da última atualização do cache em posição visível;
* reorganizar navegação principal para priorizar UBS/gestão;
* remover a visão individual da navegação principal, sem apagar sua lógica subjacente;
* preservar o botão `🔄`.

**Commit recomendado**

```bash
git add Code/PY/dashboard_conemo.py
git commit -m "feat: prioriza navegacao UBS gestao e exibe timestamp do cache"
```

## Etapa 4 — Implementar P1

Ainda em `Code/PY/dashboard_conemo.py`:

* corrigir cidade vazia no filtro;
* normalizar duplicidade de cidade por caixa/variação;
* garantir UBS como pivô funcional do filtro.

**Commit recomendado**

```bash
git add Code/PY/dashboard_conemo.py
git commit -m "fix: corrige filtro de cidade e normaliza duplicidades"
```

## Etapa 5 — Implementar P2, se não ampliar escopo

Somente se não houver conflito com P0/P1:

* inserir label discreto de versão MVP.

**Commit recomendado**

```bash
git add Code/PY/dashboard_conemo.py
git commit -m "feat: adiciona label discreto de versao MVP"
```

Se P2 for adiado, registrar isso no documento da fase e não criar commit artificial.

## Etapa 6 — Atualizar documentação final da fase

Atualizar `Docs/fase-dashboard-executiva-1.md` com:

* arquivos modificados;
* conteúdo implementado;
* testes/verificações realizados;
* decisão sobre P2;
* pendências;
* pontos para decisão humana;
* branch e commits principais.

**Commit recomendado**

```bash
git add Docs/fase-dashboard-executiva-1.md README.md Docs/README.md Code/README.md
git commit -m "docs: registra validacao e handoff da fase C1 do dashboard"
```

Só incluir `README.md`, `Docs/README.md` e `Code/README.md` se houver mudança factual que justifique atualização.

## Etapa 7 — Push da branch

```bash
git push -u origin feat/dashboard-fase-c1-mvp-operacional
```

## Etapa 8 — Abrir Pull Request

Abrir PR da branch:

`feat/dashboard-fase-c1-mvp-operacional` → `main`

### Título recomendado do PR

`Fase C1 do dashboard: MVP operacional com navegacao UBS/gestao`

### Corpo recomendado do PR

```text
## Contexto
Implementa a Fase C1 do dashboard CONEMO conforme plano operacional aprovado.

## Escopo implementado
- P0: timestamp do cache, navegacao UBS/gestao, preservacao do botao 🔄
- P1: correcao de cidade vazia e normalizacao de duplicidades
- P2: [implementado ou adiado, informar]

## Arquivos alterados
- Code/PY/dashboard_conemo.py
- Docs/fase-dashboard-executiva-1.md
- [outros, se houver]

## Fora de escopo preservado
- sem alteracao de credenciais
- sem integracao externa
- sem deploy
- sem refatoracao ampla
- sem mudanca de regras clinicas

## Validacao realizada
- timestamp visivel
- navegacao principal orientada a UBS/gestao
- visao individual fora da navegacao principal
- botao 🔄 preservado
- filtro UBS mantido como pivo
- cidade vazia removida
- duplicidades de cidade normalizadas
- exportacoes CSV agregadas preservadas

## Pendencias
- [listar ou informar nenhuma]

## Pontos para revisao
- coerencia funcional da navegacao
- clareza do timestamp
- preservacao do escopo aprovado
```

---

# 6. Checklist de revisão do PR

O revisor deve verificar, no mínimo:

## Escopo

* a fase entregou exatamente P0/P1/P2, sem expansão indevida;
* nenhum item fora de escopo foi tocado.

## Funcionalidade do MVP

* a navegação principal está orientada a UBS/gestão;
* a visão individual saiu da navegação principal;
* o botão `🔄` permanece visível;
* o `timestamp` do cache está visível e compreensível;
* o filtro UBS continua sendo o pivô principal;
* a cidade vazia desapareceu;
* as duplicidades por caixa/variação foram normalizadas;
* as exportações CSV agregadas seguem preservadas.

## Segurança e governança

* não houve alteração em credencial, integração externa ou deploy;
* não houve mudança de regra clínica ou lógica de alertas;
* não houve exposição indevida de PII.

## Qualidade técnica

* os commits estão pequenos e semanticamente claros;
* o código ficou legível e auditável;
* a lógica implementada está explicada em documentação suficiente para revisão humana;
* o PR descreve corretamente o que foi feito e o que não foi feito.

## Handoff

* `Docs/fase-dashboard-executiva-1.md` registra:

  * o que foi feito;
  * por que foi feito;
  * quais fontes foram usadas;
  * o que foi validado;
  * o que ficou pendente;
  * o que depende de aprovação humana.

---

# 7. Critério para aprovação do PR

O PR só pode ser aprovado se houver evidência explícita de que:

1. a implementação respeitou o plano aprovado;
2. os critérios funcionais do Passo 4 foram cumpridos;
3. a trilha GitHub está completa:

   * branch própria;
   * commits rastreáveis;
   * PR com descrição adequada;
   * revisão anterior ao merge.

## 8. Regra de merge

Depois da revisão:

* corrigir eventuais comentários;
* registrar aprovação;
* só então fazer merge na `main`.

Como a proteção automática da `main` ainda pode não estar tecnicamente ativa, o executor e o mantenedor devem tratar essa revisão como **obrigatória por disciplina operacional**, não como mera formalidade. Isso é coerente com o plano aprovado e com a exigência de fluxos simples, auditáveis e reprodutíveis.

## 9. Relatório de conclusão esperado do executor

Ao final, o executor deve entregar um relatório curto com:

* branch usada;
* arquivos criados ou modificados;
* commits principais;
* link ou identificação do PR;
* conteúdo principal implementado;
* testes/verificações realizados;
* pendências;
* decisão sobre P2;
* confirmação explícita de que não avançou para nova fase.

---

## Registro operacional

- Minuta registrada em 2026-04-06.
- Etapa 1 solicitada em 2026-04-06 (abertura formal da fase) foi iniciada com leitura das fontes obrigatórias.
- Bloqueio técnico encontrado: pasta de trabalho atual sem diretório `.git` (erro: `fatal: not a git repository (or any of the parent directories): .git`), impedindo `git checkout main`, criação de branch e commit local.
- Nenhuma implementação funcional foi iniciada em `Code/PY/dashboard_conemo.py`.
- Próxima ação: assim que o repositório Git local estiver disponível nesta pasta, repetir apenas a Etapa 1 (`main` atualizado + branch `feat/dashboard-fase-c1-mvp-operacional` + commit `docs: abre fase executiva C1 do dashboard`).
