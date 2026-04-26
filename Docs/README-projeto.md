# Consolidação Documental — Projeto CONEMO

Este documento serve como índice consolidado e ponto de partida para a revisão institucional do repositório, abrangendo as frentes de governança, modelagem de dados e evolução do dashboard.

---

## 1. Estado Atual do Dashboard
- **Status:** **NÃO OPERACIONAL** (Aguardando validação institucional final).
- **Fonte de Dados:** BigQuery (`firestore_curated`) integrada.
- **Denominador:** 225 usuários válidos (Reconciliado na Fase D.3).
- **Modo de Operação:** Canônico (BigQuery) com fallback técnico (Parquet local).

---

## 2. Histórico de Fases Concluídas

### **Fase C — Integração BigQuery**
- Transição da fonte de dados local (Parquet) para a camada curada no BigQuery.
- Implementação de cache (900s), botão de atualização `🔄` e timestamp dinâmico.
- **Artefato:** `Docs/fase-c-integracao-bigquery.md`

### **Fase D — Saneamento e Reintegração de Scores**
- **D.1:** Diagnóstico da fonte de scores PHQ/GAD.
- **D.2:** Correção da view `cur_score_current_v1` (Saneamento de sintaxe).
- **D.3 Corretiva:** Reconciliação aritmética de denominadores (225 participantes) e rotulagem "Não respondeu" para UBS desconhecida.
- **D.4:** Implementação do histórico longitudinal por participante em área auxiliar.
- **Artefato:** `Docs/fase-d-saneamento-phq-gad.md`

---

## 3. Pull Requests Relacionados
- **PR #5:** Fase D.3 — Reintegração e Reconciliação de Denominadores.
- **PR #6:** Fase D.4 — Histórico Longitudinal PHQ/GAD.

---

## 4. Principais Decisões Aprovadas
1. **Recentramento do MVP:** Foco em agregação por UBS e Gestão de Projeto, com visão individual como auxiliar.
2. **Privacidade:** Mascaramento de PII (e-mail) e exclusão rigorosa de registros de teste identificados no RAW.
3. **Canonicidade:** BigQuery como fonte única de verdade; Parquet apenas para disponibilidade técnica.

---

## 5. Instruções de Execução Local
Para rodar o dashboard localmente (exige credenciais Google Cloud):
```bash
export GOOGLE_APPLICATION_CREDENTIALS="caminho/para/sua/chave.json"
source .venv/bin/activate
streamlit run Code/PY/dashboard_conemo.py
```

---

## 6. Limitações e Pendências Institucionais
- **Sessões Curadas:** Ausência de registros para a coorte post-cutoff na view `cur_session_current_v1`.
- **Validação:** Necessária aprovação formal da diretoria/coordenação para declarar o dashboard como operacional.
- **Merge/Deploy:** Bloqueados até conclusão da auditoria final.

---
**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-26  
**Projeto:** CONEMO
