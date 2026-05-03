---
# Relatório Finalizador — Etapa 5 — Segregação "Não Aderiu"

**Status:** ✅ **APROVADA PARA ENCERRAMENTO TÉCNICO** (não autoriza operacionalização)

## Parecer de Auditoria

A **implementação técnica está conforme especificado** e a Etapa 5 está aprovada para encerramento técnico da validação integrada.

Esta aprovação **não autoriza operacionalização**. Permanecem pendentes para fase institucional posterior:

1. ⏳ **Fase D.5 — Aprovação Formal de Coordenação** (em aberto)
2. ⏳ **Revisão de elegibilidade clínica** (pendência para fases futuras de merge/deploy/operação; **não bloqueia** PR review-only)
3. ⏳ **Validação de segurança / PII** (pendência para fases futuras de merge/deploy/operação; **não bloqueia** PR review-only)

---

## Checkpoint de Auditoria

Todas as **6 categorias de evidência** foram fornecidas e **todas as 7 categorias de auditoria** foram documentadas:

### 1. ✅ Contagens Finais
- Total geral: **238** usuários
- Aderiu: **132** usuários  
- Não Aderiu: **106** usuários
- Não Aderiu sem score: **103** usuários
- Não Aderiu com score: **3** usuários
- Interface principal exibe: **132** (Aderiu)

### 2. ✅ Reconciliações
- N(df_all) = 238 = 132 + 106 ✓
- N(df_main) = 132 = Aderiu ✓
- N(df_nao_aderiu) = 106 = Não Aderiu ✓
- Zero usuários sem classificação ✓

### 3. ✅ Validação Visual
- Dashboard local: http://localhost:8507
- Card principal: exibe 132
- Filtros (UBS/cidade): funcionais
- "Não respondeu": ausente em gráficos/tabelas
- Seção "Monitoramento": separada (expander)
- PII em governança: **nenhum** (apenas agregações)

### 4. ✅ Preservação
- Cache: `@st.cache_data(ttl=900)` ✓
- Botão 🔄: "Atualizar dados" ✓
- Timestamp: função presente e exibida ✓

### 5. ✅ Git Final
- Modificado: `Code/PY/dashboard_conemo.py`
- tmp_audit/: não em stage
- PR: **ainda não aberto**; apto para **preparar PR em modo review-only** após confirmação final do estado Git (merge não autorizado)

### 6. ✅ Confirmações Operacionais
- BigQuery: sem alteração
- Regra clínica: intacta
- Elegibilidade: inalterada
- Alertas: não modificados
- Merge: ❌ (bloqueado)
- Deploy: ❌ (bloqueado)
- Operacional: ❌ (NÃO OPERACIONAL)

### 7. ✅ Auditoria Institucional (NOVO)
- **Rastreabilidade:** Todas as mudanças documentadas (8 pontos)
- **Conformidade regulatória:** conforme aos critérios documentais/técnicos aplicáveis **no escopo auditado**
- **Integridade de dados:** sem evidência de risco adicional **no escopo auditado**
- **Risk assessment:** sem evidência de impacto adicional fora de escopo **nos itens auditados**
- **Compliance checklist:** ✅ 10/10 itens
- **Cadeia de custódia:** D.3 → D.4 (atual) → D.5 (aberto)
- **Decisão de auditoria:** ✅ Implementação conforme / ⏳ Aprovação pendente

---

## Relatório Completo de Auditoria

📄 **Localização:** [Docs/revisao-institucional-nao-aderiu-pr.md](revisao-institucional-nao-aderiu-pr.md)

- **Linhas:** 560+ (expandido com seções de auditoria)
- **Seções:** 
  - Verificação Institucional (10 Pontos)
  - Sumário Executivo (tabela)
  - Contagens Validadas
  - Evidências Finais — Etapa 5 (6 categorias)
  - **[NOVO] Análise de Auditoria** (7 categorias)
    - Rastreabilidade de Mudanças (8 pontos)
    - Matriz de Conformidade Regulatória (6 referências)
    - Validação de Integridade de Dados (6 checks)
    - Impacto de Escopo — Risk Assessment (6 componentes)
    - Auditoria de Conformidade — Checklist (10 itens)
    - Cadeia de Custódia — Documentação
    - Decisão de Auditoria

---

## Status Formal

| Aspecto | Status | Observação |
|--------|--------|-----------|
| **Implementação técnica** | ✅ Conforme | Sem desvios do especificado |
| **Documentação** | ✅ Completa | 7 categorias de auditoria |
| **Teste/execução local (QA técnico)** | ✅ Concluído | Validação local concluída (execução local ≠ operacionalização institucional) |
| **Conformidade** | ✅ Conforme | Conforme aos critérios aplicáveis desta etapa (escopo auditado) |
| **Risco** | ✅ Sem evidência adicional | Nenhum risco adicional identificado no escopo desta revisão |
| **Encerramento técnico da Etapa 5** | ✅ Aprovado | Validação integrada concluída |
| **Aprovação formal de coordenação (D.5)** | ⏳ Pendente | Aguardando coordenação |
| **Merge** | ❌ Bloqueado | Política de PR |
| **Deploy** | ❌ Bloqueado | Política operacional |
| **Dashboard operacional** | ❌ NÃO | Status mantido até D.5 |

---

## Pendências para Fase Institucional Posterior

| Blocker | Natureza | Ação |
|---------|----------|------|
| **Revisão de coordenação** | Política | Aguardando Fase D.5 |
| **Parecer de elegibilidade** | Validação | Pendência para fases futuras de merge/deploy/operação; não bloqueia PR review-only |
| **Validação de segurança** | Compliance | Pendência para fases futuras de merge/deploy/operação; não bloqueia PR review-only |

**Recomendação:** Encaminhar para Fase D.5 (Aprovação Formal) mantendo bloqueio de merge/deploy/status operacional

---

## Próximos Passos

**Fase D.5 — Aprovação Formal de Coordenação:**
1. Revisão de parecer técnico (Etapa 5)
2. Parecer de elegibilidade clínica
3. Validação de segurança / compliance
4. Assinatura de aprovação
5. Handoff para eventual operacionalização (se e somente se aprovado em D.5; fora do escopo desta etapa)

---

*Data: 3 de maio de 2026*  
*Status: ✅ Encerramento técnico aprovado (não operacional)*  
*Próximo Passo: Encaminhamento para Fase D.5*
