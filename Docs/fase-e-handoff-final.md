# Handoff final — Fase E — Reconciliação visual controlada do dashboard CONEMO

**Data:** 2026-05-03  
**Fase:** E.10 (documentação e handoff final)

---

## 6.1 Identificação

- **Artefato auditado:** `dashboard_conemo.py` (artefato local validado nas subfases E.7-C, E.8, E.9 e ajuste estético pós-E.9).
- **Path absoluto do artefato:**
  - `/Users/ricardoceneviva/Library/CloudStorage/GoogleDrive-ceneviva@gmail.com/.shortcut-targets-by-id/15FNAS0mfcKcdeIjRa8PNbvlMpwoj1tu6/proj_conemo/Code/PY/dashboard_conemo.py`
- **Rastreabilidade do artefato validado:** cópia local **não rastreada em Git** (workspace raiz sem `.git`).
- **Estado Git (workspace local):**
  - `git status --short --branch` → `fatal: not a git repository`
  - `git rev-parse HEAD` → `fatal: not a git repository`
- **Referência oficial (clone rastreado):**
  - Repositório: `conemo-project/conemo`
  - Branch no clone oficial: `main`
  - Commit: `79106c75be9c520374a1b726a85ffe1fbe18a012`
  - Status: `## main...origin/main`
- **SHA do arquivo validado local:** `b1d455e7b970cf25a5bc79e2217bd3cb8c1c6b0172bcb7228cb55863c7b2f7c3`
- **SHA do arquivo em main oficial (clone):** `82e2c9776877ac2653fac46b95e74973e2804f266b6fb102968e698826f40384`
- **Divergência:** o arquivo local validado diverge da `main` oficial.

---

## 6.2 Sumário executivo

- A **Fase E** foi concluída tecnicamente no **artefato local validado**.
- O dashboard permanece **NÃO OPERACIONAL**.
- **Deploy não autorizado**.
- **Controle de acesso por perfil** e **log real de exportações** permanecem pendentes antes de qualquer operacionalização.
- A pendência de **rastreabilidade Git** permanece como **gate institucional obrigatório**.
- A aba **Análise Descritiva** permanece em **backlog condicionado**.
- Novas fases, PRs, merge ou decisões de operação dependem de autorização explícita do professor.

---

## 6.3 Linha do tempo das subfases E.0 a E.9

> Nota: não foram localizados, no `Docs/` do workspace local, relatórios dedicados para todas as subfases E.0–E.9. O registro abaixo consolida as decisões aprovadas e os resultados técnicos validados no ciclo E.

| Subfase | Objetivo | Status | Produto entregue | Decisões | Pendências | Alteração de código | Validação | Decisão do Revisor |
|---|---|---|---|---|---|---|---|---|
| E.0 | Matriz de reconciliação | Aprovada/encerrada | Escopo reconciliado | Base para execução por fases | Nenhuma operacional | Não | Documental | Aprovado |
| E.1 | Tela UBS | Aprovada/encerrada | Estrutura visual UBS | Eixo agregado/operacional | Sem operação real | Sim (histórico da fase) | Revisão técnica | Aprovado |
| E.2 | Navegação | Aprovada/encerrada | Navegação controlada | 3 telas autorizadas | Sem novas páginas | Sim (histórico da fase) | Revisão visual/técnica | Aprovado |
| E.3 | Polimento e checagens leves | Aprovada/encerrada | Ajustes de robustez visual | Sem expansão de escopo | Itens fora do MVP no backlog | Sim (histórico da fase) | Checagens locais | Aprovado |
| E.4 | Helpers visuais | Aprovada/encerrada | Helpers padronizados | Reforço de não operacionalidade | Nenhuma adicional | Sim (histórico da fase) | Revisão técnica | Aprovado |
| E.5 | Páginas agregadas/backlog | Aprovada/encerrada | Organização por telas autorizadas | Backlog condicionado mantido | Itens não canônicos pendentes | Sim (histórico da fase) | Revisão funcional | Aprovado |
| E.6 | Jornadas/feedbacks backlog | Aprovada/encerrada | Limites explícitos de fontes | Sem importação RAW nova | Dependências canônicas pendentes | Sim (histórico da fase) | Revisão de escopo | Aprovado |
| E.7 | PII e exportações | Aprovada/encerrada | Delimitação de exportações | Preservar CSVs legados no roteiro | Deliberações sensíveis condicionadas | Sim (histórico da fase) | Auditoria de PII/export | Aprovado |
| E.7-C | Incorporação controlada CSV | Aprovada/encerrada | CSVs ativos + placeholders | Preservação integral funcional dos CSVs do legado | Gate de rastreabilidade | Sim | Compilação e checagens | Aprovado |
| E.8 | Denominadores e “Não Aderiu” | Aprovada/encerrada c/ ressalva | Relatório de validação de denominadores | Regra dinâmica preservada | Rastreabilidade pendente | Não (fase de validação) | Contagens e segregação | Aprovado c/ ressalva |
| E.9 | Streamlit/cache/atualização | Aprovada/encerrada c/ ressalva | Relatório de validação de execução local | Cache, botão, timestamp preservados | Rastreabilidade pendente | Não (fase de validação) | `py_compile` + Streamlit local | Aprovado c/ ressalva |
| Pós-E.9 | Ajuste estético pontual | Aprovado | Rótulos “Usuários Ativos” e “Resumo executivo” | Sem alteração lógica | Nenhuma nova | Sim (texto apenas) | `py_compile` + busca textual | Aprovado |

---

## 6.4 Componentes incorporados

No artefato local validado, permanecem incorporados/preservados:

- reorganização visual da tela UBS;
- navegação com três telas autorizadas:
  - `📊 Estatísticas por UBS`
  - `🔍 Governança — Não Aderiu`
  - `👤 Consulta auxiliar`
- seção **Governança — Não Aderiu**;
- seção **Consulta auxiliar**;
- helper `_status_caption(...)`;
- helper `validate_runtime_contract(...)`;
- helper `age_group(...)`;
- CSVs ativos e placeholders controlados da E.7-C;
- rótulos finais pós-E.9:
  - **“Usuários Ativos”**
  - **“Resumo executivo”**.

---

## 6.5 Componentes mantidos em backlog condicionado

Permanecem fora de escopo canônico implementado nesta etapa:

- Análise Descritiva;
- Formulário Web / Rastreio;
- Jornadas completas;
- Feedback/Patience completo;
- fontes RAW adicionais;
- `json_data_user`;
- `forms[]`;
- `patientId`;
- `patientWhatsAppId`;
- IGI/S-RAP item a item;
- baseline estruturado;
- controle de acesso por perfil;
- log real de exportações.

---

## 6.6 Validação de denominadores (E.8)

Valores validados no artefato local pós-E.7-C:

- `df_all`: **238**
- `df_main`: **132**
- `df_nao_aderiu`: **106**
- Não Aderiu sem score: **103**
- Não Aderiu com score: **3**
- interseção `df_main ∩ df_nao_aderiu`: **0**
- status válidos: **`Aderiu`, `Não Aderiu`**
- data de corte operacional preservada: **2026-01-28**
- regra dinâmica “Não Aderiu” preservada: classificação dinâmica por `add_conemo_protocol_status(...)`, incluindo suporte a `UNK_UHS`.

**Limite de extrapolação:** esta validação refere-se ao artefato local validado e **não** deve ser extrapolada automaticamente para a `main` oficial enquanto a rastreabilidade não for resolvida.

---

## 6.7 Validação de Streamlit/cache (E.9)

- `py_compile`: **OK**
- Streamlit local: **OK**
- Link local usado: `http://localhost:8501`
- `@st.cache_data(ttl=900)`: preservado
- `st.cache_data.clear()`: preservado
- `st.rerun()`: preservado
- botão `🔄 Atualizar dados`: preservado
- timestamp/última atualização: preservado
- status NÃO OPERACIONAL: preservado
- aba Análise Descritiva: não implementada

---

## 6.8 CSVs e exportações

- Todos os CSVs da versão legada 2026-04-20 foram preservados no roteiro funcional da Fase E.
- CSVs com base canônica disponível foram incorporados.
- CSVs clínico-operacionais foram adaptados.
- CSVs sem fonte canônica validada foram preservados como placeholders controlados.
- CSVs sensíveis ficaram condicionados à decisão explícita do professor.
- Nenhuma fonte RAW nova foi importada para implementação nesta fase de handoff.
- Controle de acesso por perfil e log real de exportação permanecem como gate pré-operacional.

---

## 6.9 Governança de PII

- Há autorização explícita de uso assistencial para visualização de dados pessoais/clínicos/PII por equipes clínicas e coordenação no contexto do CONEMO.
- **PII autorizada não é PII livre**.
- O uso deve respeitar finalidade, necessidade, escopo do projeto, perfil de acesso e rastreabilidade.
- Controle de acesso e logs de exportação devem ser implementados antes de qualquer operação.

---

## 6.10 Gate de rastreabilidade antes de PR, merge, deploy ou operacionalização

O gate vigente é **obrigatório**:

1. o artefato validado da Fase E está em cópia local não rastreada em Git;
2. a `main` oficial diverge do artefato validado;
3. a `main` oficial não deve ser tratada como versão final da Fase E sem reconciliação;
4. qualquer decisão futura exige transformar o artefato validado em branch/commit/PR rastreável;
5. nenhuma decisão de deploy ou operacionalização pode ocorrer antes disso.
6. **merge não autorizado** sem validação do Revisor e autorização explícita do professor/coordenador.

### Opções para resolução posterior do gate

1. criar branch a partir da versão local validada;
2. gerar PR corretivo com diff auditável;
3. revisar PR por `@anderborba` e `@wmhass`;
4. validar novamente denominadores/cache após PR;
5. só depois considerar merge;
6. deploy continua sujeito a autorização institucional posterior.

---

## 6.11 Roteiro pós-Fase E — validação de campos e estruturas ainda não canônicos

### Bloco 1 — Análise Descritiva / Baseline

Escopo mínimo:
- raça/cor;
- escolaridade;
- renda;
- ocupação;
- situação conjugal;
- suporte social;
- histórico de tratamento;
- uso de álcool/tabaco;
- qualidade de vida;
- ativação comportamental;
- variáveis sociodemográficas.

### Bloco 2 — Formulário Web / Rastreio

Escopo mínimo:
- `forms[]`;
- submissões;
- status de preenchimento;
- abandono/retomada;
- `submissionId`;
- `currentStep`;
- timestamps de início/atualização/conclusão.

### Bloco 3 — Instrumentos clínicos

Escopo mínimo:
- PHQ-9 item a item;
- GAD-7 item a item;
- IGI item a item;
- S-RAP item a item;
- distinção entre item, score, alerta e interpretação clínica.

### Bloco 4 — Jornadas e sessões

Escopo mínimo:
- jornadas PHQ/GAD;
- sessões;
- progresso;
- último acesso;
- status de sessão;
- sessão registrada/concluída/liberada/atrasada.

### Bloco 5 — Feedback/Patience

Escopo mínimo:
- fonte canônica;
- anonimização;
- texto livre;
- `patientId`;
- `patientWhatsAppId`;
- contrato de dados;
- visualização agregada ou clínica.

### Bloco 6 — Governança de PII e exportações

Escopo mínimo:
- campos permitidos por perfil;
- controle de acesso;
- log de exportações;
- finalidade assistencial;
- segregação domínio analítico × domínio PII.

### Matriz mínima obrigatória (para cada bloco)

| Campo | Descrição obrigatória |
|---|---|
| fonte primária | sistema/tabela de origem |
| tabela/mart canônico | camada curada/analítica oficial |
| unidade de análise | participante, sessão, UBS, evento etc. |
| denominador | referência numérica formal |
| granularidade | temporal e estrutural |
| sensibilidade/PII | classificação de risco |
| regra de acesso | perfil autorizado |
| uso permitido no dashboard | agregado, clínico, bloqueado etc. |
| decisão | canônico / backlog / rejeitado / depende de nova modelagem |

---

## Fontes lidas nesta E.10 (localizadas)

1. `Docs/RULES.md`
2. `Docs/Workflow-Projeto.md`
3. `Docs/Plano-implementacao-dashboard.md`
4. `Docs/fase-e7c-incorporacao-csv-dashboard.md`
5. `Code/PY/dashboard_conemo.py`
6. `Code/PY/dashboard-conemo-2026-04-20-v1.py` (referência histórica)

### Fontes não localizadas como documento dedicado no `Docs/` local

- Plano Operacional Revisado da Fase E (arquivo específico não encontrado)
- Relatório final dedicado de E.8 (arquivo específico não encontrado)
- Relatório final dedicado de E.9 (arquivo específico não encontrado)
- Relatório dedicado do ajuste estético pós-E.9 (arquivo específico não encontrado)

---

## Registro de conflitos identificados (documentação × estado aprovado)

1. `Docs/fase-e7c-incorporacao-csv-dashboard.md` ainda apresenta trechos de status “aguardando autorização”, enquanto o estado institucional atual informa E.7/E.7-C já aprovadas e encerradas.
2. A documentação local não contém todos os relatórios dedicados de E.8/E.9/ajuste pós-E.9, embora as decisões de aprovação estejam registradas no fluxo institucional recente.

Esses conflitos são de **documentação/rastreabilidade** e não foram tratados por alteração de código nesta E.10.
