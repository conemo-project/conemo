**Autor:** Ricardo Ceneviva  
**Data:** 2026-04-26  
**Projeto:** CONEMO  

# Fase C — Integração BigQuery → Dashboard

## Introdução
Esta fase documenta a transição do dashboard CONEMO para o BigQuery como fonte de dados canônica, eliminando a dependência do arquivo Parquet local desatualizado.

---

# 1. Objetivo
Integrar o dashboard Streamlit diretamente ao BigQuery ( Southamerica-east1), preservando o contrato de dados anterior e garantindo a continuidade da operação em modo híbrido (Cache local + BigQuery).

# 2. Diagnóstico Técnico
O diagnóstico detalhado da integração, mapeamento de schemas e identificação de gaps (como o erro nos scores PHQ/GAD) está registrado em:
`Docs/fase-c1-diagnostico-integracao-bigquery-dashboard.md`

# 3. Fontes de Dados (Canônicas)
O dashboard agora consome dados das seguintes views curadas:
- `firestore_curated.cur_participant_current_v1`
- `firestore_curated.cur_session_current_v1`
- `firestore_curated.cur_health_unit_v1`
- `firestore_export.users_raw_latest` (para demográficos básicos)

# 4. Estratégia de Implementação
1. **Fallback Automático:** O sistema tenta conexão com BigQuery; se falhar (ex: falta de credenciais em ambiente local), carrega o Parquet histórico.
2. **Cache Controlado:** Uso de `st.cache_data(ttl=900)` para otimizar custos e performance.
3. **Botão de Atualização 🔄:** Implementado na sidebar para forçar a limpeza do cache e nova consulta ao BigQuery.
4. **Timestamp Obrigatório:** Exibição clara do momento da última atualização e da fonte ativa (BigQuery ou Parquet).

# 5. Segurança e PII
- **Filtro de Corte:** Apenas registros a partir de 25/01/2026 são exibidos.
- **Exclusão de Testes:** Registros marcados como `is_test_record` ou de ambientes de teste são filtrados na query.
- **Máscara de Dados:** E-mails são mascarados na visualização (`abc***@domain.com`).

# 6. Pendências Identificadas
- **Scores PHQ/GAD:** Identificada falha na view original; scores aparecem como `NULL` nesta fase.
- **Sessões Curadas:** Ausência de registros para a coorte pós-janeiro na view de sessões curadas.

---

### Próximas Fases Recomendadas
- Fase de Saneamento Clínico (scores).
- Fase de Segurança e Anonimização.
- Fase de Validação Final e Operacionalização.

Nenhuma nova fase técnica foi iniciada neste ato.
