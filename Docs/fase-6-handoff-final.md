# Fase 6 — Handoff final

**Data:** 2026-04-08  
**Projeto:** CONEMO  
**Objetivo:** transferência formal de estado ao encerramento da rodada, com delimitação de prontidão e pendências decisórias.

---

## 1) O que está entregue e estável

1. Camada curada mínima (`cur_*`) implementada e validada tecnicamente em fases anteriores.
2. Marts mínimas (`mart_ubs_monitoring_v1`, `mart_project_management_v1`, `mart_dashboard_export_v1`) validadas na Fase 3.3.
3. Alinhamento explícito com o núcleo SGBD produzido na Fase 4 (com taxonomia de cobertura padronizada).
4. Prova de integração com dashboard realizada na Fase 5, com viabilidade parcial formalizada.
5. Checklists de qualidade e segurança/PII da Fase 6 concluídos nesta rodada.

---

## 2) Prontidão por frente

## 2.1 Prontidão para consumo agregado (dashboard UBS/gestão)

**Status:** PRONTO PARA USO CONTROLADO.

Cobertura esperada:
- filtros por cidade/UBS;
- indicadores agregados centrais;
- visão de gestão por cidade/global;
- timestamp/snapshot e trilha auditável de métricas.

## 2.2 Prontidão para consumo individual detalhado no dashboard atual

**Status:** NÃO PRONTO PARA SUBSTITUIÇÃO INTEGRAL.

Motivos:
- dependência de colunas granulares do Parquet local (`user_id`, `json_data_user`, `sessionNumber`, `isCompleted`, `completedDate`);
- ausência dessas estruturas no mesmo formato nas marts da Fase 3.

## 2.3 Prontidão para núcleo pleno SGBD

**Status:** PARCIAL.

Eixos cobertos: participante, unidade de saúde.  
Eixos parcialmente cobertos: triagem/elegibilidade, avaliação longitudinal, escore derivado, uso do app.

---

## 3) Limites herdados que permanecem válidos

1. **D1:** `respondent_id` ausente na fonte exportada.
2. **N7:** timestamp de evento de sessão ainda sem implementação robusta (proxy em uso).
3. **Cobertura ausente nesta camada:** IGI, notificações, chatbot e help requests.

---

## 4) Decisões humanas obrigatórias para continuidade

1. Definir estratégia institucional de chave mestre e reconciliação histórica.
2. Deliberar escopo operacional da integração do dashboard:
   - opção A: manter modo agregado UBS/gestão como padrão de transição;
   - opção B: autorizar evolução adicional para componentes individuais.
3. Priorizar backlog de aderência plena ao núcleo SGBD por risco/impacto.
4. Aprovar política de segurança para agregações de baixa cardinalidade (limiar mínimo de publicação).

---

## 5) Pendências operacionais (sem execução nesta Fase 6)

- evolução de modelagem para elegibilidade explícita;
- evolução temporal para eventos robustos de sessão;
- expansão de cobertura de fontes operacionais não disponíveis;
- eventual evolução do dashboard além do modo agregado mínimo.

---

## 6) Instruções de continuidade (sem abrir nova fase automaticamente)

1. Usar como base de retomada:
   - `Docs/fase-6-checklist-qualidade.md`
   - `Docs/fase-6-checklist-seguranca-pii.md`
   - artefatos de encerramento das Fases 3.3, 4 e 5.
2. Não reabrir fases concluídas sem justificativa formal de não conformidade material.
3. Qualquer avanço posterior requer autorização formal explícita da coordenação.

---

## 7) Declaração de handoff

> O estado técnico-documental da rodada está transferido com rastreabilidade, limites explícitos e critérios claros de continuidade. O projeto permanece apto a operação controlada no escopo agregado e depende de deliberação humana para expansão.