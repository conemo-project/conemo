# Fase 4 — Backlog técnico para aderência plena ao núcleo do SGBD

**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-08  
**Projeto:** CONEMO  
**Branch:** `fase-4-alinhamento-explicito-modelo-sgbd`

---

## 1) Objetivo

Consolidar pendências remanescentes para evolução da camada compartilhada até o núcleo pleno do SGBD, sem reabrir Fases 1–3.

### Eixos centrais do núcleo do SGBD

Os eixos centrais considerados nesta Fase 4, sempre na mesma ordem, são:

1. participante
2. unidade de saúde
3. triagem/elegibilidade
4. avaliação longitudinal
5. escore derivado
6. uso do app

### Relação com os demais artefatos da Fase 4

- A matriz de aderência faz o mapeamento estrutural entre objetos implementados e eixos do núcleo do SGBD.
- A nota de aderência consolida o julgamento de cobertura da camada atual.
- Este backlog traduz as lacunas identificadas em pendências técnicas e decisórias.

---

## 2) Visões externas já possíveis com a camada atual

### 2.1 Visões já deriváveis (uso controlado)

1. **Painel operacional por UBS**
   - base: `mart_ubs_monitoring_v1`
   - capacidade: volume, baseline, ativos, atrasos, abandono, distribuição PHQ/GAD

2. **Visão executiva global/cidade**
   - base: `mart_project_management_v1`
   - capacidade: cobertura, qualidade de dados, proxies de funil e atividade

3. **Exportação estruturada para consumo externo**
   - base: `mart_dashboard_export_v1`
   - capacidade: entrega tabular padronizada com sinalização de métricas indisponíveis

### 2.2 Limitações dessas visões

- elegibilidade explícita ainda não materializada como fato/decisão (relacionada ao item 3.1.1);
- ausência de IGI observável na camada atual (relacionada ao item 3.2.2);
- ausência de eventos operacionais completos de notificação/chatbot/help (relacionada ao item 3.2.3);
- métricas temporais com proxies onde falta timestamp de evento robusto (N7; relacionada ao item 3.2.4).

---

## 3) Backlog técnico consolidado

## 3.1 Pendências de modelagem

1. **Materializar decisão de elegibilidade**
   - alvo mínimo: `eligibility_status`, `eligibility_reason`, `rule_version`
   - motivo: eixo triagem/elegibilidade hoje está apenas parcialmente coberto
   - classificação associada: parcialmente coberta

2. **Formalizar eixo longitudinal clínico**
   - alvo mínimo: fatos de reavaliação por instrumento e versão temporal
   - motivo: separar evolução clínica de progresso operacional
   - classificação associada: parcialmente coberta

3. **Separar semanticamente score clínico vs score de jornada**
   - alvo mínimo: regra canônica de uso e comparabilidade entre tipos de escore
   - motivo: evitar interpretação indevida
   - classificação associada: parcialmente coberta

## 3.2 Pendências de dados/fontes

1. **Resolver D1 (`respondent_id` ausente)**
   - alternativa A: incorporar na fonte/export
   - alternativa B: decisão formal de manter `document_id` como chave única da camada mínima
   - classificação associada: coberta

2. **Recuperar cobertura IGI (se existir na fonte)**
   - confirmar existência, localização e qualidade
   - classificação associada: parcialmente coberta

3. **Mapear fontes de eventos operacionais faltantes**
   - notificações
   - chatbot
   - help requests
   - classificação associada: parcialmente coberta

4. **Confirmar fonte de timestamp de evento em sessões (N7)**
   - substituir proxy por temporalidade observável robusta
   - classificação associada: parcialmente coberta

## 3.3 Pendências de implementação

1. Evoluir camada curada com fatos adicionais (sem quebrar compatibilidade das views atuais).
2. Expandir marts para consumo SGBD além do escopo mínimo dashboard.
3. Implementar testes de reconciliação temporal (eventos e durations) quando timestamps robustos estiverem disponíveis.
4. Documentar versionamento das regras de transformação adicionais por fase.

## 3.4 Pendências de governança/decisão

1. Deliberação formal sobre estratégia definitiva de chave mestre (impacto em reprocessamento histórico).
2. Deliberação de escopo mínimo obrigatório para “núcleo pleno” do SGBD (critério de aceite da próxima fase).
3. Priorização institucional do backlog por risco/impacto operacional.
4. Autorização formal de abertura da próxima fase (Fase 5 permanece não autorizada nesta entrega).

---

## 4) Priorização sugerida (não executiva)

- **P0 (crítico para núcleo):** D1, elegibilidade explícita, timestamp robusto.
- **P1 (alto impacto analítico):** eventos operacionais completos e longitudinal clínico.
- **P2 (expansão):** refinamentos avançados de comparabilidade de escores e visões ampliadas.

---

## 5) Síntese final de prontidão

A camada atual suporta visões externas operacionais relevantes e auditáveis, porém a aderência ao núcleo pleno do SGBD depende do fechamento do backlog acima, principalmente em elegibilidade explícita, temporalidade robusta e eventos operacionais hoje indisponíveis.

---

## 6) Confirmação de escopo

- Documento produzido exclusivamente para Fase 4.
- Sem reimplementação de `cur_*`.
- Sem reimplementação de marts.
- Sem início de Fase 5.
