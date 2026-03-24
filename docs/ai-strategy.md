# Estratégia de IA — Fases e guardrails

Documento detalhado de como a IA será integrada ao projeto em fases: onde ajuda, onde não é fonte de verdade, riscos e oportunidades. Ver também ADR-006 e docs/ai-integration.md.

---

## Princípio central

**IA como camada de interpretação e recomendação sobre dados e métricas já produzidos pelo pipeline (dbt + PM4Py/SimPy).** Métricas e regras de negócio vêm do código e do dbt; a IA não inventa números nem substitui validação humana.

---

## Fase 1 — Copiloto de engenharia e documentação

**Objetivo**: Usar IA no dia a dia de desenvolvimento e documentação, sem impacto direto em dados ou relatórios oficiais.

**Onde a IA ajuda**:
- Geração e revisão de SQL (dbt), com contexto do projeto (nomes de tabelas, convenções).
- Sugestões de documentação (comentários, descrições de modelos, glossário).
- Revisão de textos técnicos e ADRs.

**Onde a IA não é usada como verdade**:
- Definição final de regras de negócio e de modelo de dados; sempre validar com negócio e com dados reais.
- Testes e métricas oficiais; não usar IA para “inventar” testes ou valores esperados.

**Riscos**: Código ou documentação sugeridos podem estar errados ou desatualizados. **Guardrails**: revisão humana, testes automatizados, convenções documentadas (glossário, ADRs).

**Oportunidades**: Acelerar escrita de SQL e docs; manter padrão de nomenclatura com prompts em `prompts/` (ex.: prompt_sql_copilot.md).

---

## Fase 2 — Interpretação de variantes e gargalos; sumarização executiva

**Objetivo**: Gerar texto interpretativo e sumários a partir dos resultados de Process Mining (variantes, gargalos) já calculados pelo pipeline.

**Onde a IA ajuda**:
- Interpretar tabelas de variantes (ex.: “as 3 variantes mais frequentes representam X% dos casos; a variante Y indica desvio de aprovação”).
- Interpretar resultados de gargalos (ex.: “a atividade A concentra Z% do tempo de espera; recomenda-se revisar alocação de recurso”).
- Produzir sumário executivo em linguagem natural a partir de métricas (tempo de ciclo, quantidade de casos, top variantes, top gargalos).

**Onde a IA não é usada como verdade**:
- Os números (contagens, percentuais, tempos) vêm sempre do output do mining; o prompt deve receber esses dados e apenas reformular/interpretar.
- Nenhuma conclusão nova que dependa de cálculo deve ser “inventada” pelo modelo; se faltar métrica, a IA deve indicar que não tem o dado.

**Riscos**: Modelo pode parafrasear de forma enganosa ou adicionar nuance não suportada pelos dados. **Guardrails**: (1) passar dados estruturados no prompt; (2) instrução explícita “não inventar métricas”; (3) exibir lado a lado o dado bruto e o texto (auditoria).

**Oportunidades de produto**: Relatório executivo “one-click” a partir do event log; painel com “resumo em texto” ao lado de gráficos.

---

## Fase 3 — Recomendações de melhoria e agente analista

**Objetivo**: Gerar recomendações de melhoria de processo com base em mining (e opcionalmente simulação); preparar atuação como “agente analista”.

**Onde a IA ajuda**:
- Listar recomendações priorizadas (ex.: “reduzir fila na atividade X”, “unificar variante Y”) com base em gargalos e variantes.
- Responder perguntas do tipo “por que o tempo de ciclo aumentou?” usando resultados de mining (dados passados no contexto).
- (Agente) Executar fluxo: receber pergunta → (opcional) rodar mining/simulação → montar contexto → chamar LLM → devolver resposta + origem dos dados.

**Onde a IA não é usada como verdade**:
- Recomendações são sugestões; decisão de implementar é humana.
- Qualquer número citado na recomendação deve ter origem no resultado de mining/simulação passado no prompt.

**Riscos**: Recomendações genéricas ou fora do contexto; usuário tratar saída como decisão automática. **Guardrails**: (1) cada recomendação referenciar dado concreto (atividade, métrica); (2) disclaimer em UI (“sugestão com base nos dados; validar com negócio”); (3) logging de prompts/respostas para auditoria (sem logar dados sensíveis).

**Oportunidades de produto**: “Assistente de processo” que sugere melhorias; futuramente agente que pode ser invocado pelo Cortex.

---

## Fase 4 — Integração com Cortex

**Objetivo**: Expor Process Intelligence como capability orquestrada pelo Cortex; manter IA como camada interna (interpretação/recomendações), não como substituto dos dados.

**Onde a IA ajuda**:
- Continua atuando nas fases 2 e 3 (interpretação, sumário, recomendações) dentro dos jobs orquestrados pelo Cortex.
- Possível exposição de “endpoint de análise” que devolve métricas + texto interpretativo.

**Onde a IA não é usada como verdade**:
- Cortex dispara jobs (dbt, Python mining/simulação); os artefatos oficiais (tabelas, arquivos) são produzidos por esse pipeline, não pelo LLM.
- Contratos de API devem deixar claro o que é “métrica” (fonte: pipeline) e o que é “texto interpretativo” (fonte: IA).

**Riscos**: Acoplamento de contratos (Cortex espera formato X; mudança quebra integração). **Guardrails**: Documentar contrato (schema de payload, versão); versionar APIs.

**Oportunidades**: Process Intelligence como serviço reutilizável; dashboards e relatórios alimentados por Cortex + este repositório.

---

## Resumo: onde IA ajuda vs não é verdade

| Área | IA ajuda | IA não é fonte de verdade |
|------|----------|----------------------------|
| SQL / documentação | Copiloto, sugestões | Regras de negócio, modelo final |
| Métricas | — | Sempre do dbt e do mining/simulação |
| Variantes / gargalos | Interpretação em texto | Números e listas (PM4Py) |
| Sumário executivo | Redação a partir de dados | Dados passados no prompt |
| Recomendações | Sugestões priorizadas | Decisão de implementar; números citados |
| Agente analista | Respostas com contexto | Dados vêm do pipeline; não inventar |

---

## Checklist de guardrails (implementação)

- [ ] Prompts recebem contexto estruturado (dados reais) e instrução “não inventar métricas”.
- [ ] Resultados de IA exibidos junto com origem (tabela, métrica, período).
- [ ] Logging de uso (ex.: qual prompt, qual modelo) sem logar conteúdo sensível.
- [ ] Revisão humana para primeiros relatórios/recomendações até estabilizar qualidade.
- [ ] Documentação de limites e riscos em docs/ai-integration.md e neste arquivo.
