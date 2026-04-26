**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-26  
**Projeto:** CONEMO  

# Fase C.1 — Diagnóstico de Integração BigQuery-Dashboard (Versão Final Revisada)

**Data:** 2026-04-24  
**Status:** Pronto para C.2 (Aguardando Aprovação)  
**Branch:** `fase-c1-diagnostico-integracao-bigquery-dashboard`

## 1. Objetivo
Diagnosticar a viabilidade técnica da integração direta BigQuery → Dashboard, mapear dependências e identificar quebras de contrato entre o Parquet legado e as views curadas.

## 2. Inventário de Fontes e Gaps

| Recurso | Status no BigQuery | Compatibilidade Parquet | Bloqueio/Gap |
|---|---|---|---|
| Perfil Participante | `cur_participant_current_v1` | Alta | OK |
| Unidades de Saúde | `cur_health_unit_v1` | Alta | OK |
| Sessões e Conclusão | `cur_session_current_v1` | **Crítica** | Ausência de dados pós 25/01/2026 |
| Scores PHQ/GAD | `cur_score_current_v1` | **Média** | Erro de parsing na view original |

## 3. Diagnóstico de Chaves de Ligação (Joins)
- **Mapeamento:** O `user_id` do dashboard deve ser vinculado ao `participant_master_id` das views curadas.
- **Evidência:** Sucesso nos testes de `LEFT JOIN` entre participantes e UBS.
- **Risco:** Perda de registros se as chaves não forem consistentes entre `users_raw` e `cur_participant`.

## 4. Diagnóstico de Filtros de Governança
- **Corte Temporal:** Implementação obrigatória de `created_at >= '2026-01-25'` para evitar coortes antigas e desatualizadas.
- **Exclusão de Testes:** Filtro rigoroso por `is_test_record = false`.
- **Resultado:** A coorte ativa filtrada no BigQuery retornou 125 participantes únicos (conforme consulta em 24/04/2026).

## 5. Diagnóstico de Performance (Cache)
- **Latência:** Consultas demoram ~2s.
- **Mitigação:** Uso de `st.cache_data` com TTL 15min.
- **Impacto:** Redução de custos BQ e melhor UX.

## 6. Sumário de Achados e Recomendações
- ✅ **Chaves de Join:** Validadas e prontas.
- ⚠️ **Scores PHQ/GAD:** Bloqueados por erro na view. Exige Fase D (Saneamento).
- ⚠️ **Sessões:** Layer curada de sessões está vazia para a nova coorte. Exige investigação da ingestão.
- ❗ **Risco:** Exposição de PII se a máscara de e-mail no SQL falhar.
- ✅ **Recomendação final:** "Pronto para C.2".
