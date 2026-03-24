# ADR-007: Arquitetura desacoplada para eventual integração com Cortex / Argos

**Status**: Provisório (estudo)  
**Data**: 2025-03 · Atualizado: 2026-03  

## Vigência

**Diretriz de desenho** para o repositório enquanto o Cortex (orquestração) e o Argos (observabilidade) evoluem ou não existem no mesmo estágio. Não define SLA nem integração obrigatória.

## Contexto

No futuro, Process Intelligence pode ser orquestrada por outro sistema ou consumida por observabilidade. Acoplar o laboratório a SDKs ou APIs desses sistemas antes de contratos estáveis aumentaria retrabalho.

## Decisão (direção de trabalho)

Manter o núcleo do estudo **sem dependência de Cortex ou Argos** em build ou execução diária do repositório:

- **Entradas**: dados e modelos (ex.: BigQuery, dbt) via convenções do próprio repo; não via chamadas obrigatórias ao Cortex.
- **Saídas**: tabelas, arquivos em `data/outputs/`, etc.; integrações futuras consumiriam esses artefatos ou contratos a definir.
- **Extensão**: quando necessário, adapters em **`src/app/connectors/`** (ou serviços externos) podem encapsular chamadas a outros sistemas sem acoplar o núcleo analítico.

## Consequências

- **Esperadas**: Repo testável e evoluível independentemente do roadmap do Cortex.
- **Cuidados**: Quando existir integração real, será preciso documentar contratos para evitar divergência de formatos.

## Alternativas consideradas

1. **Dependência do Cortex desde o primeiro dia**: Evitada no estudo.
2. **Ignorar integração futura**: Menos documentação de pontos de extensão; o ADR prefere deixar o gancho explícito.
3. **Mini-orquestrador neste repo**: Makefile e scripts bastam para o laboratório; orquestração corporativa é outro tema.
