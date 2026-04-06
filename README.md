# CONEMO — Repositório Institucional

**Organização:** [conemo-project](https://github.com/conemo-project)  
**Repositório:** `conemo-project/conemo`  
**Visibilidade:** Privado  
**Versão inicial:** 2026-04-06  
**Responsáveis:** Ricardo Ceneviva & Anderson Borba

---

## 1. Finalidade deste repositório

Este repositório concentra a base técnica e documental do projeto CONEMO, sob governança institucional.

Sua finalidade é:

- versionar código, documentação normativa e artefatos técnicos auditáveis do projeto;
- manter trilha rastreável de decisões técnicas, de escopo e de governança;
- oferecer base segura para colaboração controlada entre membros autorizados;
- preparar o projeto para fases de integração progressiva e controlada de código e documentação.

---

## 2. Restrições obrigatórias de uso

> **Este repositório é privado. Acesso restrito a membros autorizados pela coordenação.**

**O que NÃO deve ser versionado aqui:**

- dados clínicos, epidemiológicos ou operacionais do projeto (brutos ou processados);
- arquivos `.csv`, `.parquet`, `.xlsx`, `.sav`, `.dta` ou qualquer export de dados reais;
- credenciais, tokens, chaves, arquivos `.env`, arquivos `*credentials*.json`;
- caminhos locais de máquina ou segredos de infraestrutura;
- dumps, exports temporários ou caches de execução local.

Qualquer inclusão de conteúdo que não respeite essas restrições deve ser tratada como incidente de governança.

---

## 3. Estado atual do projeto (2026-04-06)

### Dashboard

- o dashboard sobe localmente em modo cache/local;
- o MVP visual está centrado no eixo **agregado-operacional com foco em UBS e gestão**;
- a visão individual por participante não é o eixo principal do MVP visual atual — é requisito de backend/modelagem para fase posterior;
- BigQuery e alertas não integram o núcleo obrigatório do MVP visual imediato;
- backend, metadados de coleta, dupla timeline analítica, alertas e segregação de PII são requisitos de retaguarda, não do MVP visual.

### Repositório institucional

- a organização `conemo-project` foi criada e aprovada;
- o repositório `conemo` foi criado como privado e aprovado;
- a fase de configuração inicial foi executada, auditada e formalmente aprovada em 2026-04-06;
- nenhum dado real, credencial ou cópia massiva do projeto local foi realizada.

---

## 4. Estrutura prevista para fases posteriores

A estrutura abaixo descreve a organização-alvo do repositório, a ser implementada em fases aprovadas formalmente pela coordenação. Nenhum diretório ou arquivo além dos já presentes (`README.md` e `.gitignore`) foi criado nesta fase.

```
conemo/
├── .gitignore          # proteção contra versionamento indevido
├── README.md           # este documento
├── Code/
│   ├── PY/             # scripts Python auditados e aprovados
│   └── R/              # scripts R auditados e aprovados
└── Docs/               # documentação normativa e técnica auditada e aprovada
```

**A integração de qualquer conteúdo do projeto local seguirá, obrigatoriamente, fases aprovadas formalmente pela coordenação, com revisão de governança prévia.**  
Nenhum diretório de dados (`Data/`) será versionado sem anonimização, segregação de PII e decisão formal registrada.

---

## 5. Governança

A execução técnica deste repositório segue os princípios definidos em:

- `Docs/RULES.md` — princípios de reprodutibilidade, acurácia e auditabilidade;
- `Docs/Workflow-Projeto.md` — protocolo operacional por papel (coordenador, executor técnico, revisor).

**O professor/coordenador é a autoridade final sobre escopo, aprovação e prioridade.**

Avanços para novas fases dependem de autorização formal prevista no workflow.

---

## 6. Dados sensíveis

Os dados do CONEMO são sensíveis por natureza (dados clínicos, identificadores de participantes, registros de saúde mental).

- **Dados reais não devem ser versionados aqui sob nenhuma circunstância.**
- Qualquer futura inclusão de dados — mesmo anonimizados — depende de:
  - anonimização formal documentada;
  - segregação de PII validada;
  - decisão explícita e registrada da coordenação.

---

*Versão inicial: 2026-04-06*  
*Atualizado em: 2026-04-06 — revisão pós-auditoria da Fase de Configuração Inicial*
