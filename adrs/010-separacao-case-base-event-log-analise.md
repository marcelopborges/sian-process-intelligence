# ADR-010: Separação entre case_base, event_log e análises derivadas

**Status**: Provisório (estudo)  
**Data**: 2025-03 · Atualizado: 2026-03  

## Vigência

Organização **conceitual** dos artefatos durante o estudo. Nomes exatos de tabelas e materializações seguem o projeto dbt e podem mudar; o importante é não misturar finalidades.

## Contexto

Dados de processo aparecem em níveis distintos: visão por **caso**, por **evento** (event log) e **resultados de análise** (variantes, gargalos, texto de IA). Colapsar tudo em uma única visão dificulta testes e reuso (mining precisa sobretudo do event log).

## Decisão (direção de trabalho)

Manter separados, no desenho do estudo:

1. **Case base** (mart): tipicamente uma linha por caso de processo, para KPIs e visão gerencial.
2. **Event log** (mart): uma linha por evento/atividade com timestamps e chaves de caso — base para PM4Py e parâmetros de simulação.
3. **Análises inteligentes / derivadas**: saídas de mining, simulação e IA; **não** substituem os marts como fonte primária de fatos de processo.

No dbt: marts distintos conforme modelados (ex.: referências a `mart_cp_*` no estudo de CP). No Python: leitura via `src/app/connectors` / `src/app/core`; mining em `src/app/mining`; simulação em `src/app/simulation`; IA em `src/app/ai`.

## Consequências

- **Esperadas**: Responsabilidades mais claras para quem mantém modelos e scripts.
- **Cuidados**: Consistência de `case_id` e convenções entre camadas — ponto de atenção contínua no laboratório.

## Alternativas consideradas

1. **Só event log**: Possível para mining puro; perde simplicidade para relatórios por caso.
2. **Uma tabela única “tudo em uma linha”**: Rejeitada por misturar granularidades.
3. **Escrever análises de volta como fonte de verdade no warehouse**: Rejeitada; análises permanecem derivadas no desenho pretendido.

---

## Nota (CP em estudo)

Detalhes sobre materialização TABLE vs VIEW, camadas operacionais dinâmicas e regras de timestamp são **hipóteses de modelagem** documentadas em `docs/` e no código dbt — sujeitas a revisão antes de qualquer uso produtivo.
