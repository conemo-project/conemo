# Workflow-Projeto.md

**Autor:** Ricardo Ceneviva  
**Versão:** 2026-04-04  
**Escopo:** fluxo operacional para execução, revisão, integração e validação de artefatos técnicos do projeto CONEMO

---

# Protocolo operacional do projeto CONEMO

## 1. Finalidade do workflow

Este workflow organiza a cooperação entre:

1. o professor e coordenador do projeto;
2. o agente executor técnico;
3. o agente revisor metodológico, factual, editorial e de governança.

O objetivo é garantir que a produção técnica do CONEMO seja:

- aderente à documentação canônica do projeto;
- metodologicamente correta;
- funcionalmente coerente;
- tecnicamente auditável;
- segura do ponto de vista de dados;
- fácil de revisar, retomar e atualizar.

Este protocolo deve ser usado para:

- especificações funcionais;
- modelagem de dados;
- ingestão e padronização de fontes;
- regras de negócio;
- dashboards e relatórios;
- indicadores e funnels;
- alertas e rotas operacionais;
- auditoria de qualidade;
- integração de múltiplos rascunhos ou versões;
- documentação técnica e handoff.

---

## 2. Arquitetura de papéis

## 2.1. Papel do professor

O professor atua como:

- coordenador do projeto;
- aprovador formal de cada fase;
- controlador do escopo;
- juiz final da adequação metodológica, técnica e funcional;
- decisor final em caso de conflito entre fontes, versões ou estratégias de implementação.

Em termos práticos:  
**Professor = autoridade final sobre conteúdo, escopo, prioridade e aprovação.**

---

## 2.2. Papel do agente revisor

O agente revisor deve ser usado para:

1. revisar e validar o plano operacional de cada fase;
2. verificar aderência ao `AGENTS.md`;
3. auditar coerência metodológica, conceitual e documental;
4. verificar alinhamento entre o artefato e a documentação canônica do CONEMO;
5. avaliar integridade das regras de negócio;
6. avaliar riscos de segurança, PII e uso indevido de dados;
7. identificar redundâncias, lacunas e extrapolação de escopo;
8. recomendar correções antes da aprovação de cada fase.

Em resumo:  
**Agente revisor = controle de qualidade metodológica, factual, editorial e de governança.**

---

## 2.3. Papel do agente executor

Neste projeto, o Codex, ou outro agente executor, deve ser usado para:

1. criar e editar arquivos-fonte autorizados;
2. implementar apenas a fase aprovada;
3. consolidar rascunhos e versões validadas;
4. editar scripts, SQL, `.md`, `.qmd`, `.Rmd`, `.docx` e outros artefatos autorizados;
5. gerar outputs técnicos quando necessário;
6. organizar logs, tabelas, documentação e handoff;
7. respeitar estritamente o `RULES.md` e este `Workflow-Projeto.md`;
8. não iniciar novas fases por conta própria;
9. não tomar decisões clínicas;
10. usar obrigatoriamente programação letrada sempre que houver produção de código, intercalando código com explicação clara em linguagem natural;
11. seguir obrigatoriamente as melhores práticas de programação adotadas no projeto, incluindo legibilidade, nomes significativos, convenções consistentes, documentação, comentários úteis, testes, tratamento de erros e eficiência quando aplicável;
12. não considerar uma fase de código concluída se a lógica implementada não estiver explicada de forma compreensível para revisão humana.

Em resumo:  
**Agente executor = executor técnico do plano validado, com código auditável, documentado e legível por humanos.**


---

## 3. Tipos de tarefa cobertos por este workflow

O fluxo deve começar pela identificação do tipo principal de tarefa.

### Tipo A. Especificação funcional
Exemplos:
- requisitos de dashboard;
- definição de outputs;
- regras de acesso;
- regras de alertas;
- definição de entidades e objetos do sistema.

### Tipo B. Modelagem de dados
Exemplos:
- esquema relacional;
- dimensões e fatos;
- chaves e identificadores;
- versionamento;
- metadados de coleta.


### Tipo C. Ingestão e curadoria
Exemplos:
- intake de CSV ou JSON;
- validação de schema;
- deduplicação;
- normalização de tipos;
- reconciliação de identificadores.

### Tipo D. Indicadores e marts
Exemplos:
- funil operacional;
- indicadores clínicos;
- indicadores de adesão;
- timelines;
- agregados por UBS e gestão.

### Tipo E. Alertas e monitoramento operacional
Exemplos:
- risco suicidário;
- piora clínica;
- engajamento;
- rotas operacionais;
- status de tratamento do alerta.

### Tipo F. Dashboard, relatórios e exportação
Exemplos:
- estruturas para visualização;
- filtros por perfil;
- exportação CSV;
- visões clínicas;
- visões de pesquisa e gestão.

### Tipo G. Auditoria e reconciliação
Exemplos:
- auditoria de qualidade;
- revisão de regra de negócio;
- reconciliação entre versões;
- conferência de fontes;
- validação final.

### Tipo H. Documentação e handoff
Exemplos:
- plano de fase;
- notas de decisão;
- codebook;
- registro de validação;
- handoff de execução.

Escolher um tipo principal é obrigatório.  
Se a tarefa combinar dois ou mais tipos, a sequência deve ser explicitada antes da execução.

---

## 4. Hierarquia de fontes

Em tarefas do CONEMO, use sempre esta ordem de prioridade:

1. instruções explícitas do professor;
2. documentação canônica do projeto;
3. materiais validados do CONEMO;
4. fontes primárias do sistema, exports e schemas;
5. rascunhos internos e notas auxiliares;
6. documentação externa oficial e literatura científica, quando necessária.

Regras obrigatórias:

1. um resumo derivado nunca substitui a documentação canônica quando houver regras, thresholds, datas, escores, rotas ou interpretações funcionais;
2. quando duas versões divergirem, deve-se definir uma versão canônica antes de editar;
3. nenhum dado empírico deve ser incorporado sem conferência na fonte relevante;
4. se faltar uma fonte obrigatória, a fase deve parar antes da implementação.

---

## 5. Princípio geral do fluxo

Cada fase deve seguir um ciclo curto e auditável.  
A lógica é:

1. solicitar plano da fase;
2. validar o plano;
3. autorizar a execução;
4. executar apenas a fase aprovada;
5. relatar a conclusão;
6. auditar a entrega;
7. aprovar ou corrigir;
8. só então abrir a próxima fase.

Esse ciclo vale para tarefas técnicas, analíticas e documentais.

---

## 6. Ciclo-padrão de cada fase

## Etapa A. Definição do escopo imediato

Antes de qualquer ação, registrar:

- qual é a fase;
- qual é o artefato a ser produzido;
- qual é o material de base;
- quais entidades, fatos ou regras serão afetados;
- o que está fora do escopo.

Sem isso, a fase não começa.

---

## Etapa B. Solicitação do plano operacional

O agente executor deve apresentar apenas o plano da fase.

O plano deve informar:

1. objetivo da fase;
2. tipo principal de tarefa;
3. arquivos e fontes a consultar;
4. arquivos a criar ou modificar;
5. artefatos esperados;
6. critérios de validação;
7. itens explicitamente fora do escopo;
8. riscos, dependências e conflitos de fonte;
9. impacto esperado sobre regras de negócio, segurança ou perfis de acesso, quando aplicável.
10. formato do artefato final e, se houver código, como a explicação em linguagem natural acompanhará a implementação;
11. abordagem prevista para testes, validação técnica, tratamento de erros e documentação de inputs e outputs.

Nesta etapa, não se executa nada.

---

## Etapa C. Validação do plano

O professor submete o plano ao agente revisor.  
O agente revisor avalia:

- aderência ao `AGENTS.md`;
- aderência a este workflow;
- coerência com o escopo aprovado;
- aderência à documentação canônica do CONEMO;
- riscos metodológicos;
- riscos técnicos;
- riscos de segurança e PII;
- necessidade de reconciliação entre fontes ou rascunhos.

Sem validação, não há autorização.

---

## Etapa D. Autorização formal

Somente após a validação o professor autoriza a execução.

A autorização deve indicar:

- nome da fase;
- artefato autorizado;
- limites da fase;
- arquivos autorizados;
- proibição de avançar para a fase seguinte sem nova autorização.

---

## Etapa E. Execução da fase


## Etapa E. Execução da fase

O agente executor:

- edita apenas os arquivos autorizados;
- produz apenas os artefatos da fase;
- registra decisões relevantes;
- atualiza documentação mínima;
- não muda o escopo;
- não inicia novas fases por conta própria;
- não altera silenciosamente regras já validadas;
- não toma decisão clínica;
- segue obrigatoriamente o `RULES.md`;
- usa programação letrada quando houver produção de código;
- entrega código com explicação em linguagem natural suficiente para leitura humana;
- segue as práticas de legibilidade, documentação, nomenclatura, testes, tratamento de erros e eficiência definidas para o projeto. 

---

## Etapa F. Relatório de conclusão

Ao final, o agente executor deve informar:

1. arquivos criados ou modificados;
2. conteúdo principal implementado;
3. fontes efetivamente usadas;
4. outputs gerados;
5. testes ou verificações realizados;
6. regras de negócio tocadas;
7. pendências;
8. pontos que exigem decisão humana.
9. scripts, notebooks, consultas ou arquivos executáveis produzidos;
10. onde está a explicação humana da lógica implementada;
11. inputs, outputs, transformações, regras e tratamentos de erro mais relevantes da fase.

---

## Etapa G. Auditoria da entrega

O professor traz o relatório e, se necessário, trechos do material.

O agente revisor avalia:

- se a fase foi realmente concluída;
- se o artefato corresponde ao plano;
- se há erros factuais;
- se há violação da documentação canônica;
- se houve extrapolação de escopo;
- se há risco de segurança, PII ou mau uso de dados;
- se a próxima fase pode ser aberta.

---

## Etapa H. Aprovação ou correção

Depois da auditoria, há apenas três saídas possíveis:

1. fase aprovada;
2. fase aprovada com ressalvas documentadas;
3. fase devolvida para correção pontual.

Só depois disso o ciclo recomeça.

---

## 7. Fluxos específicos do CONEMO

## 7.1. Fluxo para especificação funcional

Sequência recomendada:

1. partir da documentação canônica;
2. identificar objetivo funcional;
3. identificar usuários e perfis afetados;
4. identificar regras de negócio envolvidas;
5. identificar campos, objetos e outputs necessários;
6. revisar aderência metodológica e operacional;
7. validar a especificação antes de qualquer implementação.

**Produto da fase:** especificação funcional estruturada.  
**Não produzir ainda:** implementação técnica, salvo autorização explícita.

---

## 7.2. Fluxo para modelagem de dados

Sequência recomendada:

1. partir da especificação funcional e dos documentos canônicos;
2. identificar dimensões, fatos, metadados e tabelas de parametrização;
3. preservar a separação entre rastreio web, baseline no app, jornada e acompanhamento humano;
4. explicitar chaves, versionamento e regras de integridade;
5. definir segregação de PII;
6. validar o modelo antes da implementação.

**Produto da fase:** modelo lógico e físico proposto.  
**Não produzir ainda:** ETL completo, salvo autorização explícita.

---

## 7.3. Fluxo para ingestão e curadoria

Sequência recomendada:

1. preservar arquivos brutos sem alteração;
2. registrar intake com metadados de carga;
3. validar schema, tipos, datas e identificadores;
4. deduplicar e reconciliar chaves;
5. separar evento clínico, evento operacional e metadado;
6. registrar anomalias e decisões de transformação;
7. validar a camada curada antes dos marts.

**Produto da fase:** camada curada validada e log de transformação.  
**Não produzir ainda:** painéis finais, salvo autorização explícita.

---

## 7.4. Fluxo para indicadores e marts

Sequência recomendada:

1. partir da camada curada validada;
2. definir pergunta analítica ou operacional;
3. definir indicador, numerador, denominador e janela temporal;
4. distinguir indicador observável de indicador desejado mas indisponível;
5. organizar o consumo por nível do usuário, UBS e gestão;
6. validar fórmulas, filtros e cobertura antes do dashboard.

**Produto da fase:** marts e indicadores validados.  
**Não produzir ainda:** interpretação causal, salvo desenho compatível.

---

## 7.5. Fluxo para alertas e segurança clínica

Sequência recomendada:

1. partir das regras canônicas e parâmetros aprovados;
2. separar alertas de risco suicidário, piora clínica e engajamento operacional;
3. definir regra acionadora, prioridade, rota e status de tratamento;
4. garantir que alerta crítico não termine em visualização passiva;
5. registrar trilha de tratamento do alerta;
6. validar a regra antes da publicação.

**Produto da fase:** motor de alertas parametrizado e auditável.  
**É proibido:** reduzir alerta crítico a visualização simples em painel.

---

## 7.6. Fluxo para dashboard, relatórios e exportação

Sequência recomendada:

1. partir de marts e indicadores já validados;
2. definir a visão por perfil:
   - clínica
   - UBS
   - pesquisa
   - gestão
3. definir filtros, agregações e campos exibidos;
4. proteger PII e restringir exportações conforme perfil;
5. registrar exportações auditáveis;
6. validar coerência funcional antes da entrega.

**Produto da fase:** estrutura de consumo e relatórios validados.  
**Não produzir ainda:** novas regras de negócio, salvo autorização explícita.

---

## 7.7. Fluxo para integração de múltiplos rascunhos

Quando houver versões A, B, C ou notas auxiliares, o fluxo correto é:

1. definir a versão canônica;
2. tratar as demais como suplementos;
3. mapear:
   - sobreposição
   - conflito
   - adição única
   - conteúdo descartável
4. construir matriz de reconciliação;
5. só então fundir o material.

É proibido:

- concatenar arquivos diretamente;
- reaproveitar regras ou números sem conferência na fonte relevante;
- substituir silenciosamente uma versão validada sem nova decisão documentada.

---

## 8. Checkpoints obrigatórios de qualidade

Nenhuma fase pode ser aprovada sem passar por todos os checkpoints aplicáveis.

## 8.1. Checkpoint de escopo
Pergunta:
**a fase entregou exatamente o que foi autorizado?**

Verificar:

- aderência ao pedido;
- ausência de expansão indevida;
- respeito aos limites da fase.

---

## 8.2. Checkpoint funcional
Pergunta:
**o artefato respeita a lógica real do CONEMO?**

Verificar:

- coerência com o fluxo do app;
- coerência com as jornadas;
- coerência com follow-up e baseline;
- coerência com perfis de acesso;
- coerência com alertas e suporte humano.

---

## 8.3. Checkpoint factual e de fontes
Pergunta:
**as afirmações factuais e regras estão corretas?**

Verificar:

- nomes;
- datas;
- definições;
- thresholds;
- escores;
- regras de negócio;
- fidelidade às fontes canônicas.

---

## 8.4. Checkpoint de qualidade de dados
Pergunta:
**os dados e transformações são consistentes?**

Verificar:

- schema;
- tipos;
- datas;
- identificadores;
- duplicidades;
- derivados;
- coerência entre camadas.

---

## 8.5. Checkpoint de segurança e PII
Pergunta:
**houve proteção adequada dos dados sensíveis?**

Verificar:

- segregação entre analítico e PII;
- ausência de exposição indevida;
- controle por perfil;
- rastreabilidade de exportação;
- uso de chaves substitutas quando aplicável.

---

## 8.6. Checkpoint de alerta e segurança clínica
Pergunta:
**o tratamento dos alertas respeita a criticidade do protocolo?**

Verificar:

- prioridade;
- rota;
- status de tratamento;
- separação entre risco suicidário, piora e engajamento;
- ausência de visualização passiva como única resposta.

---

## 8.7. Checkpoint técnico
Pergunta:
**o artefato técnico está utilizável, consistente e auditável por um revisor humano?**

Verificar, quando aplicável:

- consistência de scripts e consultas;
- paths relativos;
- nomenclatura coerente e significativa;
- formatação consistente;
- comentários e espaços em branco usados para melhorar legibilidade;
- documentação de propósito, uso, arquitetura, inputs e outputs;
- presença de programação letrada ou explicação textual equivalente quando houver código;
- separação adequada entre ingestão, transformação, aplicação de regra de negócio, validação e output;
- logs;
- outputs verificáveis;
- testes e verificações realizados;
- tratamento de erros previsíveis;
- eficiência e ausência de loops ou iterações desnecessárias quando houver alternativa mais adequada;
- versionamento.

---

## 8.8. Checkpoint de documentação
Pergunta:
**há documentação suficiente para revisão e retomada?**

Verificar:

- plano atualizado;
- relatório de conclusão;
- fontes usadas;
- testes realizados;
- pendências;
- handoff.
- localização da documentação explicativa do código;
- indicação de como rerodar scripts, notebooks ou consultas;
- descrição mínima dos inputs e outputs técnicos da fase.

---

## 9. Prompt-padrão para o agente executor

## 9.1. Prompt para pedir o plano de uma fase

```text
Leia o RULES.md e o Workflow-Projeto.md deste repositório.

Apresente o plano operacional da Fase X do projeto CONEMO.

O plano deve informar:
1. objetivo da fase;
2. tipo principal de tarefa;
3. arquivos e fontes que serão consultados;
4. arquivos que poderão ser criados ou modificados;
5. artefatos esperados;
6. como a fase será validada;
7. o que ficará explicitamente fora do escopo;
8. riscos, conflitos de fonte, dependências e impactos sobre regras de negócio, perfis de acesso ou segurança;
9. se houver código, em que formato ele será entregue e como a explicação em linguagem natural acompanhará a implementação;
10. abordagem prevista para testes, documentação de inputs/outputs e tratamento de erros.

Não execute ainda. Aguarde autorização.
```
---

## 9.2. Prompt para relatório de conclusão

```text
Apresente o relatório de conclusão da Fase X do projeto CONEMO.

Informe:
1. arquivos criados ou modificados;
2. conteúdo principal implementado;
3. fontes efetivamente usadas;
4. outputs gerados;
5. testes e verificações realizados;
6. regras de negócio tocadas;
7. pendências;
8. pontos que exigem decisão humana;
9. scripts, notebooks, consultas ou arquivos executáveis produzidos;
10. onde está a explicação em linguagem natural da lógica implementada;
11. quais inputs, outputs, transformações e tratamentos de erro foram mais relevantes.

Não inicie a próxima fase.
```
