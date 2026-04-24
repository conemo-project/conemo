# Fase 6 — Checklist de segurança e PII

**Data:** 2026-04-08  
**Projeto:** CONEMO  
**Escopo:** verificação documental/técnica de segregação de PII na rodada atual, sem alterar SQLs ou código do dashboard.

---

## 1) Premissas de segurança aplicadas

- Princípio de minimização de dados no consumo analítico.
- Separação entre camada analítica curada e dados sensíveis de origem.
- Transparência obrigatória de lacunas/limites (sem ocultação).

---

## 2) Checklist de segregação de PII

## 2.1 Camada curada

- [x] `cur_participant_current_v1` exclui campos PII diretos (`name`, `email`, `cpf`, `birthDate`, `phone`, `termsOfConsent`) no resultado analítico.
- [x] Campos publicados priorizam identificadores técnicos e atributos operacionais.
- [x] Flags de qualidade e reconciliação não reintroduzem PII textual.

**Status:** conforme.

## 2.2 Marts de consumo

- [x] `mart_ubs_monitoring_v1` e `mart_project_management_v1` são agregadas por UBS/cidade/global.
- [x] `mart_dashboard_export_v1` estrutura consumo por métrica/escopo sem PII direta.
- [x] Métricas indisponíveis são marcadas como `INDISPONIVEL`, sem uso de preenchimento arriscado.

**Status:** conforme.

## 2.3 Dashboard (ponto de atenção)

- [x] Fase 5 documentou que o dashboard local atual ainda depende de base detalhada para visão individual auxiliar.
- [x] Integração BigQuery recomendada na rodada atual restringe-se ao modo agregado UBS/gestão.
- [x] Não houve migração silenciosa que exponha PII por atalho técnico.

**Status:** conforme com restrição operacional.

---

## 3) Ameaças e riscos residuais

1. **Risco de reidentificação indireta** em recortes muito pequenos (UBS/cidade com baixa cardinalidade).
2. **Risco operacional no modo local** quando usada base detalhada com campos sensíveis fora da camada curada.
3. **Risco de interpretação inadequada** de métricas proxy (tempo/progresso) como verdade clínica completa.

---

## 4) Controles mínimos recomendados para operação

1. Aplicar supressão/mascaramento adicional em recortes com baixa contagem (política de limiar mínimo).
2. Manter segregação de ambientes (desenvolvimento vs consumo institucional).
3. Evitar exportação ad hoc de dados de granularidade individual fora da trilha formal.
4. Preservar logs de acesso/extração para auditoria.
5. Formalizar política de retenção e descarte para artefatos locais temporários.

---

## 5) Decisões humanas pendentes

1. Definir política institucional de limiar mínimo de publicação por agregado.
2. Definir política formal para uso da visão individual auxiliar no ciclo de transição.
3. Deliberar exigências de segurança para eventual integração online contínua com BigQuery.

---

## 6) Veredito do checklist de segurança/PII

> **Checklist de segurança e PII: APROVADO COM RISCOS RESIDUAIS CONTROLÁVEIS E PENDÊNCIAS DE POLÍTICA.**

No escopo da rodada, a segregação de PII na camada curada/marts permanece consistente; os riscos remanescentes estão explicitados para decisão institucional.