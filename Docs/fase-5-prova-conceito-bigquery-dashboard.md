# Fase 5 — Prova de conceito controlada: camada BigQuery no dashboard

**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-08  
**Projeto:** CONEMO  
**Branch desta fase:** `fase-5-prova-integracao-dashboard-bigquery`

---

## 1) Objetivo da prova de conceito

Verificar, em ambiente controlado, se o dashboard atual consegue substituir total ou parcialmente a leitura do Parquet local por leitura da camada de consumo derivada do BigQuery, **sem reintroduzir transformação estrutural no Streamlit**.

---

## 2) Fonte atual vs. fonte nova testada

### 2.1 Fonte atual do dashboard
- `Data/PARQUET/conemo_dados_consolidados_raw_04_03_2026.parquet`
- leitura real confirmada com `pandas.read_parquet`
- 9.053 linhas no arquivo lido na execução controlada
- colunas observadas incluem: `user_id`, `json_data_user`, `sessionNumber`, `isCompleted`, `completedDate`, `email`

### 2.2 Fonte nova testada na prova
A prova usou o **schema funcional** das marts já validadas:
- `mart_ubs_monitoring_v1`
- `mart_project_management_v1`
- `mart_dashboard_export_v1`

A validação foi feita com `DataFrame` controlado em memória, preservando a estrutura das marts e evitando qualquer alteração do dashboard em produção local.

---

## 3) Testes executados

## T1 — Confirmação da fonte atual do dashboard

### O que foi testado
Leitura real do Parquet local usado por `dashboard_conemo.py`.

### Por que foi testado
Para confirmar o contrato de entrada atual do Streamlit antes de compará-lo com a camada BigQuery.

### Resultado
- arquivo existe e é legível;
- o app hoje depende de colunas em granularidade de usuário/sessão;
- a fonte atual não é uma mart agregada.

---

## T2 — Prova positiva parcial com schema de mart agregada

### O que foi testado
Um adaptador mínimo sobre `mart_ubs_monitoring_v1` e `mart_project_management_v1` para simular:
- filtros por cidade e UBS;
- total agregado de participantes;
- médias agregadas de PHQ/GAD;
- disponibilidade de timestamp;
- disponibilidade de visão executiva de gestão;
- preservação visual do botão `🔄` e do label MVP.

### Por que foi testado
Para demonstrar o menor caso viável de consumo da camada BigQuery no dashboard sem refatoração ampla.

### Resultado observado
A prova controlada retornou compatibilidade positiva para:
- `filters_ok = True`
- `timestamp_available = True`
- `management_view_available = True`
- `refresh_button_ui_preserved = True`
- `mvp_label_ui_preserved = True`

Também mostrou que o cálculo agregado de participantes e de médias PHQ/GAD é possível em modo UBS/gestão.

---

## T3 — Prova negativa complementar com o dashboard atual “as is”

### O que foi testado
Execução das dependências centrais do dashboard atual contra um `DataFrame` com schema de mart agregada.

### Por que foi testado
Para localizar exatamente onde o app quebra quando a fonte deixa de ser o Parquet detalhado.

### Falhas observadas
Foram observadas quebras imediatas por ausência de colunas esperadas pelo app atual:
- `user_id`
- `isCompleted`
- `sessionNumber`
- `completedDate`
- `json_data_user`

### Interpretação
Isso prova que a troca de fonte **não pode ser feita apenas substituindo a linha de leitura**; é necessário adaptar o contrato de dados consumido pelos blocos do app.

---

## 4) Compatibilidades confirmadas

### 4.1 Compatíveis no modo agregado
- filtro por UBS;
- filtro por cidade;
- navegação principal UBS/gestão;
- total agregado de participantes;
- médias agregadas PHQ-9/GAD-7;
- timestamp de atualização;
- manutenção do botão `🔄`;
- manutenção do label MVP.

### 4.2 Parcialmente compatíveis
- lógica de conclusão/progresso: existe cobertura parcial nas marts, mas não no mesmo formato de taxa direta por sessão usado hoje pelo dashboard.

---

## 5) Incompatibilidades e deltas encontrados

Não funcionam diretamente com as marts da Fase 3:
- visão individual por participante;
- busca por `user_id`;
- exibição de e-mail mascarado;
- distribuição de gênero;
- distribuição de idade;
- tabela detalhada de sessões;
- parsing de `json_data_user` dentro do Streamlit.

---

## 6) Conclusão da prova de conceito

A prova de conceito controlada demonstra que a substituição do Parquet local por leitura da camada BigQuery é **tecnicamente viável para a parte agregada do dashboard**, mas **não para a aplicação inteira em seu estado atual**.

### Conclusão explícita
A integração mínima é viável se a Fase 5 limitar o dashboard ao consumo **UBS/gestão** baseado nas marts validadas e tratar a visão individual auxiliar como fora do modo BigQuery nesta etapa.

---

## 7) Confirmação de escopo

- sem refatoração ampla do dashboard;
- sem alteração de SQL das views curadas ou marts;
- sem abertura da Fase 6;
- sem reintrodução de transformação estrutural no front-end.
