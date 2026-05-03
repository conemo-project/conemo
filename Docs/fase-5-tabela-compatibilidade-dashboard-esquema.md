# Fase 5 — Tabela de compatibilidade entre o dashboard atual e o esquema das marts

**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-08  
**Projeto:** CONEMO  
**Branch desta fase:** `fase-5-prova-integracao-dashboard-bigquery`

---

## 1) Finalidade da tabela

Registrar, de forma auditável, o delta entre:
- o **esquema efetivamente esperado** por `Code/PY/dashboard_conemo.py`; e
- o **esquema disponível** nas marts validadas da Fase 3.

---

## 2) Tabela de compatibilidade

| Bloco do dashboard atual | Fonte atual esperada | Cobertura na camada BigQuery | Classificação | Observação de integração |
|---|---|---|---|---|
| Leitura inicial em `load_data()` | Parquet único com granularidade usuário × sessão | Não equivalente diretamente | incompatível direta | Exige adaptador de fonte |
| Filtro por cidade | `ubs_city` derivado do JSON do usuário | `ubs_city` presente nas marts | compatível | Pode ser mantido |
| Filtro por UBS | `ubs_name` derivado do JSON do usuário | `ubs_name` presente em `mart_ubs_monitoring_v1` | compatível | Pode ser mantido |
| Métrica “Participantes” | `user_id` único após deduplicação | `participant_count_ubs` / `participant_count` | compatível com adaptação mínima | Troca de cálculo, sem nova regra de negócio |
| Média PHQ-9 | `phq_score` por participante | `phq9_score_avg_ubs` | compatível com adaptação mínima | Requer consumo agregado |
| Média GAD-7 | `gad_score` por participante | `gad7_score_avg_ubs` | compatível com adaptação mínima | Requer consumo agregado |
| Conclusão de sessões | soma de `isCompleted` sobre linhas de sessão | não disponível no mesmo formato | parcialmente compatível | Exige redefinição visual ou nova métrica autorizada |
| Gráfico “Participantes por UBS” | contagem de `user_id` por UBS | `participant_count_ubs` | compatível | Sem necessidade de reconstruir linhas por usuário |
| Gráfico “PHQ/GAD por UBS” | média por participante/UBS | médias por UBS já prontas | compatível | Consumo direto da mart |
| Taxa de conclusão por UBS | média de `isCompleted` por UBS | não disponível diretamente | incompatível direta | Não recomputar no front-end |
| Distribuição de gênero | `gender` derivado do JSON | não disponível nas marts da Fase 3 | incompatível | Fora do modo BigQuery mínimo |
| Distribuição de idades | `age` derivada de `birthDate` | não disponível nas marts da Fase 3 | incompatível | Fora do modo BigQuery mínimo |
| Resumo tabular por UBS | agregações em memória sobre `df_users` | métricas de UBS disponíveis | compatível com adaptação mínima | Tabela pode ser reescrita como consumo agregado |
| Visão individual auxiliar | `user_id`, `email`, `sessionNumber`, `completedDate` | não disponível nas marts | incompatível | Não deve ser mantida no modo BigQuery desta fase |
| Timestamp | mtime do Parquet local | `snapshot_timestamp` nas marts | compatível com adaptação mínima | Muda a origem do timestamp, não o componente visual |
| Botão `🔄` | limpa cache e reroda app | compatível | compatível | Mantém UI; backend de recarga pode mudar |
| Label MVP | texto estático | independente da fonte | compatível | Sem impacto |
| Navegação UBS/gestão | sidebar do Streamlit | aderente ao escopo das marts | compatível | Mantém-se como eixo principal |

---

## 3) Síntese do delta

### 3.1 Compatível sem ampliação de escopo
- filtros por UBS/cidade;
- navegação UBS/gestão;
- indicadores agregados centrais;
- timestamp;
- botão `🔄`;
- label MVP.

### 3.2 Compatível apenas com adaptação mínima explícita
- totais de participantes;
- médias agregadas PHQ/GAD;
- resumo tabular por UBS.

### 3.3 Não compatível na Fase 5 sem extrapolar escopo
- visão individual auxiliar;
- demografia derivada (idade/gênero);
- detalhes de sessão por participante;
- taxa atual de conclusão baseada diretamente em `isCompleted` por linha.

---

## 4) Encaminhamento recomendado

A Fase 5 sustenta a seguinte decisão técnica:
- **integrar primeiro a camada BigQuery apenas na visão agregada UBS/gestão**;
- **não forçar compatibilidade artificial** da visão individual dentro desta fase;
- **não reintroduzir camada curada dentro do Streamlit**.

---

## 5) Confirmação de escopo

- tabela produzida exclusivamente para a Fase 5;
- sem refatoração ampla do dashboard;
- sem alteração de SQL;
- sem início da Fase 6.
