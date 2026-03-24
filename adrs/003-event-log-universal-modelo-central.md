# ADR-003: Event log universal como modelo central

**Status**: Aceito  
**Data**: 2025-03  
**Contexto**: Necessidade de um modelo de dados comum para Process Mining e simulação.

## Contexto

Process Mining e ferramentas de simulação esperam dados em formato de **event log**: sequência de eventos por caso, com pelo menos caso (case_id), atividade (activity) e timestamp. Atributos adicionais (recurso, custo, atributos de caso) enriquecem análises. Cada processo de negócio (contas a pagar, compras, RH) tem tabelas fonte diferentes, mas a saída analítica deve seguir um mesmo padrão para permitir algoritmos e pipelines reutilizáveis.

## Decisão

Adotar um **modelo de event log universal** como artefato central produzido pelo dbt e consumido pelo Python:

- **Campos obrigatórios**: `case_id`, `activity` (nome da atividade), `timestamp` (timestamp do evento).
- **Campos recomendados**: `activity_instance_id` (opcional, para eventos duplicados no mesmo caso/atividade), atributos de caso (ex.: filial, fornecedor, valor), atributos de evento (ex.: recurso, duração).
- **Convenção**: Um mart `event_log` por processo (ex.: `mart_cp_event_log` para contas a pagar), com mesma estrutura de colunas; nomenclatura de atividades padronizada e documentada no glossário.

Esse event log é a **fonte de verdade** para mineração (PM4Py) e para construção de modelos de simulação (SimPy); a IA interpreta resultados gerados a partir dele, não inventa dados.

## Consequências

- **Positivas**: Algoritmos de mining e simulação reutilizáveis; onboarding de novos processos simplificado; interoperabilidade com padrões (XES, CSV) via mapeamento.
- **Negativas**: Exige disciplina na nomenclatura de atividades e no preenchimento de timestamps; modelos dbt devem garantir consistência.
- **Riscos**: Timestamps ausentes ou incoerentes prejudicam mining; mitigação: testes dbt e validações em Python.

## Alternativas consideradas

1. **Um formato por processo**: Rejeitado; aumentaria duplicação de código em Python e manutenção.
2. **Apenas XES nativo**: Rejeitado; BigQuery e dbt trabalham melhor com tabelas relacionais; export para XES quando necessário pode ser feito em Python.
3. **Event log apenas em Python (sem mart dbt)**: Rejeitado; ter o event log como mart no BigQuery permite auditoria, reprodutibilidade e uso por outras ferramentas (ex.: BI).

---

## Decisões subsequentes (Contas a Pagar)

- **Colunas obrigatórias** no mart_cp_event_log: além de case_id e activity, passam a incluir `event_timestamp_original`, `event_order`, `event_timestamp_adjusted`, `timestamp_confiabilidade` (NEGOCIO/TECNICO). Ordenação estável para mining via event_timestamp_adjusted.
- **Atividades padronizadas**: TITULO_CRIADO, TITULO_LIBERADO, EVENTO_FINANCEIRO_GERADO, LANCAMENTO_CONTABIL, PAGAMENTO_REALIZADO, BAIXA_SEM_SE5, TITULO_CANCELADO. BAIXA_MANUAL renomeado para BAIXA_SEM_SE5.
- **FK2**: no log principal, um evento LANCAMENTO_CONTABIL por caso (agregado). Valor no evento agregado tratado com cautela (preferir NULL na V1).
- Detalhes em docs/domain-contas-a-pagar.md e docs/architecture.md.
