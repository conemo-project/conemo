# Projeto CONEMO — Repositório Técnico-Documental

Este repositório concentra artefatos técnicos, analíticos e documentais do projeto CONEMO, com foco em governança, trilha de auditoria e evolução controlada da frente de dashboard SGBD.

---

## 1. Objetivo deste repositório

Hoje, este repositório existe para:

- registrar decisões técnicas e de governança do projeto;
- manter documentação normativa e canônica para execução por fases;
- armazenar código e insumos da frente de dashboard;
- preservar evidências auditáveis de validação, reconciliação e planejamento.

Tipos de artefato concentrados:

- documentação normativa e de workflow;
- planos e relatórios por fase/passo;
- scripts em Python e R para exploração, integração e dashboard;
- dados locais de trabalho (CSV/PARQUET) para execução cache-only;
- materiais de referência.

---

## 2. Estrutura atual do repositório

A estrutura abaixo descreve o estado atual, sem implicar reorganização já executada:

- `Code/`
  - `PY/`: scripts Python (inclui `dashboard_conemo.py` e scripts auxiliares)
  - `R/`: scripts e JSONs auxiliares da frente R
  - `Quarto/`: artefatos de exploração/visualização e arquivos de dados de apoio
- `Data/`
  - `CSV/`: bases em CSV
  - `PARQUET/`: cache e variantes em parquet usadas na execução local
- `Docs/`
  - documentos normativos, planos, auditorias, reconciliações e deliberação
- `Literature/`
  - materiais de literatura/referência
- arquivos de diagrama na raiz (`diagrama_banco_conemo.*`)

A estrutura está estável/congelada para as frentes em curso, salvo deliberação formal em fase própria.

---

## 3. Documentos normativos principais

Leitura obrigatória para qualquer execução:

1. [Docs/RULES.md](Docs/RULES.md)
2. [Docs/Workflow-Projeto.md](Docs/Workflow-Projeto.md)
3. [Docs/Plano-implementacao-dashboard.md](Docs/Plano-implementacao-dashboard.md)

Documentos de estado recente do dashboard:

4. [Docs/passo2-mapa-dependencias-cache-vs-bigquery.md](Docs/passo2-mapa-dependencias-cache-vs-bigquery.md)
5. [Docs/passo3-definicao-mvp-e-backlog.md](Docs/passo3-definicao-mvp-e-backlog.md)
6. [Docs/passo4-reconciliacao-mvp-visual.md](Docs/passo4-reconciliacao-mvp-visual.md)

Documento de estado recente do setup institucional GitHub:

7. [Docs/github-setup-fase-organizacao-repositorio.md](Docs/github-setup-fase-organizacao-repositorio.md)

---

## 4. Estado atual do projeto

Resumo factual do estado documentado:

- trilha de governança e auditoria foi conduzida em múltiplas fases documentais em `Docs/`;
- Passo 2 (dependências cache vs BigQuery) está documentado como completo;
- Passo 3 (definição de MVP e backlog) está documentado como completo;
- Passo 4 (reconciliação do MVP visual) está documentado como aprovado e encerrado após complemento corretivo vinculante em [Docs/passo4-reconciliacao-mvp-visual.md](Docs/passo4-reconciliacao-mvp-visual.md);
- Fase 5 (frente documental de deliberação) está aprovada e encerrada como fase documental; seus efeitos operacionais permanecem condicionados à deliberação formal da Coordenação.
- a frente de setup institucional GitHub está documentada e aprovada em [Docs/github-setup-fase-organizacao-repositorio.md](Docs/github-setup-fase-organizacao-repositorio.md), com a organização `conemo-project` e o repositório privado `conemo` criados com sucesso;
- a fase de configuração inicial do repositório `conemo-project/conemo` foi executada, auditada e formalmente aprovada em 2026-04-06: `.gitignore` robusto e `README.md` institucional criados; repositório privado, limpo e apto para fases posteriores;
- a **Fase A** (configuração avançada mínima do GitHub) está **formalmente encerrada** como aprovada com ressalvas (auditoria final: 2026-04-06); documentada em [Docs/fase-github-configuracao-avancada.md](Docs/fase-github-configuracao-avancada.md); o projeto está **autorizado a avançar para a Fase B**.
- a **Fase B** (revisão final documental do plano canônico do dashboard) está **formalmente encerrada** em 2026-04-06: [Docs/Plano-implementacao-dashboard.md](Docs/Plano-implementacao-dashboard.md) consolidado como versão final canônica (V.2.0.0); decisão sobre botão `🔄`, requisito de `timestamp` e separação entre MVP visual / backend-modelagem / fase posterior incorporados; projeto pronto para abertura da Fase C.
- a **Fase C** (melhorias do dashboard) está **formalmente aberta** em 2026-04-06 para preparação executiva, registrada em [Docs/fase-c-abertura-melhorias-dashboard-conemo.md](Docs/fase-c-abertura-melhorias-dashboard-conemo.md), sem implementação técnica iniciada neste registro.
- a **Fase 6** (qualidade, segurança e handoff) está **formalmente aprovada e encerrada** em 08/04/2026, com parecer em [Docs/fase-6-parecer-auditoria-2026-04-08.md](Docs/fase-6-parecer-auditoria-2026-04-08.md) e relatório em [Docs/fase-6-relatorio-conclusao-rodada.md](Docs/fase-6-relatorio-conclusao-rodada.md);
- o **Plano Operacional de Pré-processamento de Dados** está **formalmente encerrado** em 08/04/2026, com parecer em [Docs/parecer-encerramento-fase-6-plano-preprocessamento-2026-04-08.md](Docs/parecer-encerramento-fase-6-plano-preprocessamento-2026-04-08.md) e submissão institucional no [PR #2](https://github.com/conemo-project/conemo/pull/2).

Importante:

- propostas e roadmap não devem ser interpretados como cronograma autorizado automático;
- avanços para novas fases dependem de aprovação formal prevista no workflow.

---

## 5. Estado atual da frente do dashboard

Consolidado fiel aos artefatos vigentes:

- o dashboard sobe localmente;
- a operação atual do MVP visual está em modo cache/local;
- integração BigQuery não é parte do escopo visual obrigatório do MVP atual;
- o botão `🔄` permanece preservado no dashboard; sua operação está temporariamente condicionada à credencial Google/BigQuery; a dependência não constitui exclusão funcional;
- no longo prazo, o botão `🔄` permanece componente formal da arquitetura de atualização via BigQuery;
- o eixo do MVP visual foi recentrado para **agregado-operacional com foco em UBS e gestão**;
- a visão individual por participante permanece requisito estrutural de backend/modelagem, mas não é eixo principal da interface visual atual;
- o `timestamp` da última atualização do cache é **requisito obrigatório** da próxima fase técnica.

Referência canônica para esse enquadramento: [Docs/Plano-implementacao-dashboard.md](Docs/Plano-implementacao-dashboard.md) (versão final canônica V.2.0.0, Fase B) e reconciliação formal em [Docs/passo4-reconciliacao-mvp-visual.md](Docs/passo4-reconciliacao-mvp-visual.md).

---

## 6. Histórico recente de trabalho (síntese factual)

- **Passo 1**: teste funcional do dashboard (referenciado nos passos seguintes)
- **Passo 2**: mapeamento de dependências cache vs BigQuery
- **Passo 3**: definição de MVP e backlog priorizado
- **Passo 4**: reconciliação do dashboard atual com o MVP visual revisado
- **Setup GitHub institucional**: organização `conemo-project` e repositório privado `conemo` criados e aprovados
- **Configuração inicial do repositório `conemo`**: `.gitignore` robusto e `README.md` institucional criados, commit inicial enviado, fase formalmente aprovada em auditoria (2026-04-06); ressalvas menores tratadas no mesmo ciclo
- **Fase A — Configuração avançada mínima do GitHub**: política mínima de contribuição definida, bloqueio HTTP 403 registrado sem improvisação, auditoria de ajustes aprovada em 2026-04-06 — **fase formalmente encerrada; clearance para Fase B concedido**
- **Fase B — Revisão final documental do plano canônico**: [Docs/Plano-implementacao-dashboard.md](Docs/Plano-implementacao-dashboard.md) consolidado como V.2.0.0 (versão final canônica), **formalmente encerrado** em auditoria; decisão sobre botão `🔄`, navegação UBS-first e `timestamp` incorporados; projeto pronto para abertura da Fase C
- **Fase C — Abertura da fase de melhorias do dashboard**: kickoff documental registrado em [Docs/fase-c-abertura-melhorias-dashboard-conemo.md](Docs/fase-c-abertura-melhorias-dashboard-conemo.md); base executiva mantida no plano canônico + complemento do Passo 4; sem início de implementação neste ato
- **Fase 6 — Qualidade, segurança e handoff**: fase formalmente auditada como **aprovada e encerrada** em 08/04/2026, com saneamento da pendência final de governança/rastreabilidade registrado em [Docs/fase-6-parecer-auditoria-2026-04-08.md](Docs/fase-6-parecer-auditoria-2026-04-08.md)
- **Encerramento formal da rodada do Plano Operacional de Pré-processamento de Dados**: registrado em 08/04/2026 em [Docs/parecer-encerramento-fase-6-plano-preprocessamento-2026-04-08.md](Docs/parecer-encerramento-fase-6-plano-preprocessamento-2026-04-08.md), com submissão institucional no [PR #2](https://github.com/conemo-project/conemo/pull/2)

Observação: esta lista é histórico de execução/documentação, não cronograma automático de próximas fases.

---

## 7. Pendências e próximos pontos de atenção

Itens que permanecem em fase própria ou dependência formal:

- execução técnica da próxima fase do dashboard com base no escopo reconciliado do Passo 4;
- itens dependentes de BigQuery/credencial e decisões de arquitetura/deploy;
- deliberações formais da coordenação para itens de governança documental da Fase 5;
- decisão institucional sobre viabilização de proteção técnica da `main` (branch protection/rulesets) no GitHub privado, dado bloqueio atual de plano/permissão (HTTP 403) — registrada como **pendência residual de governança técnica** (Fase A encerrada);
- decisão sobre redundância de owner da organização `conemo-project` (risco de owner único) — registrada como **pendência residual de governança técnica** (Fase A encerrada);
- componentes explicitamente adiados no plano do MVP visual (ex.: visão individual como eixo principal da interface, alertas detalhados em camada visual, timelines explícitas por participante na interface).

---

## 8. Como retomar o projeto sem perda de contexto

Ordem recomendada de leitura para retomada:

1. [Docs/RULES.md](Docs/RULES.md)
2. [Docs/Workflow-Projeto.md](Docs/Workflow-Projeto.md)
3. [Docs/Plano-implementacao-dashboard.md](Docs/Plano-implementacao-dashboard.md)
4. [Docs/passo2-mapa-dependencias-cache-vs-bigquery.md](Docs/passo2-mapa-dependencias-cache-vs-bigquery.md)
5. [Docs/passo3-definicao-mvp-e-backlog.md](Docs/passo3-definicao-mvp-e-backlog.md)
6. [Docs/passo4-reconciliacao-mvp-visual.md](Docs/passo4-reconciliacao-mvp-visual.md)
7. [Docs/github-setup-fase-organizacao-repositorio.md](Docs/github-setup-fase-organizacao-repositorio.md)
8. [Docs/fase-github-configuracao-avancada.md](Docs/fase-github-configuracao-avancada.md)
9. [Docs/fase-c-abertura-melhorias-dashboard-conemo.md](Docs/fase-c-abertura-melhorias-dashboard-conemo.md)
10. [Docs/fase-6-relatorio-conclusao-rodada.md](Docs/fase-6-relatorio-conclusao-rodada.md)
11. [Docs/fase-6-parecer-auditoria-2026-04-08.md](Docs/fase-6-parecer-auditoria-2026-04-08.md)
12. [Docs/parecer-encerramento-fase-6-plano-preprocessamento-2026-04-08.md](Docs/parecer-encerramento-fase-6-plano-preprocessamento-2026-04-08.md)

Documento canônico atual para escopo visual do MVP do dashboard:

- [Docs/Plano-implementacao-dashboard.md](Docs/Plano-implementacao-dashboard.md)

Documento vinculante de reconciliação do Passo 4:

- [Docs/passo4-reconciliacao-mvp-visual.md](Docs/passo4-reconciliacao-mvp-visual.md)

READMEs complementares de navegação:

- [Docs/README.md](Docs/README.md)
- [Code/README.md](Code/README.md)
- [Data/README.md](Data/README.md)

---

## 9. Regras de uso e atualização deste README

- Atualizar este README sempre que fases/passo relevantes forem concluídos e formalmente registrados.
- Manter aderência estrita aos documentos canônicos em `Docs/`.
- Não sobrescrever decisões aprovadas sem registro formal de auditoria/reconciliação.
- Não converter proposta em decisão final sem documento de aprovação correspondente.
