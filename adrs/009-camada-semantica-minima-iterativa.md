# ADR-009: Abordagem iterativa de camada semântica mínima

**Status**: Aceito  
**Data**: 2025-03  
**Contexto**: Nível de definição de camada semântica (nomes de negócio, métricas, hierarquias) no início do projeto.

## Contexto

Uma camada semântica completa (catálogo de métricas, mapeamento de nomes de negócio para tabelas/colunas, regras de agregação) facilita autoatendimento e ferramentas de BI, mas exige acordo com várias áreas e pode atrasar a entrega de valor. O projeto começa como laboratório e precisa entregar resultados de Process Intelligence (mining, simulação) sem bloquear em definições semânticas amplas.

## Decisão

Adotar uma **camada semântica mínima e iterativa**:

- **Mínima**: Definir apenas o necessário para o primeiro processo (Contas a Pagar): nomes de atividades no event log, case_id e atributos de caso essenciais (ex.: filial, fornecedor, valor), e métricas básicas (tempo de ciclo, quantidade de casos, variantes). Documentar no glossário (`docs/glossary.md`) e nos modelos dbt (comentários, descrições).
- **Iterativa**: Expandir conforme necessidade: novas métricas, novos processos, mapeamentos para ferramentas de BI ou para a camada de IA. Não construir um catálogo semântico grande antecipadamente; cada adição deve ter uso concreto (relatório, análise, recomendação).

Ferramentas de camada semântica (ex.: Cube, LookML, Metabase semantic layer) podem ser avaliadas depois; no início, a "semântica" vive em documentação e em convenções de nomenclatura no dbt e no código Python.

## Consequências

- **Positivas**: Entrega mais rápida; menos dependência de acordos amplos; evolução guiada por uso real.
- **Negativas**: Possível retrabalho de nomenclatura se houver mudança de convenção; BI/IA podem precisar de mapeamentos adicionais depois.
- **Riscos**: Proliferação de sinônimos ou interpretações diferentes; mitigação: glossário central e revisão em PRs quando novos termos forem introduzidos.

## Alternativas consideradas

1. **Camada semântica completa desde o início**: Rejeitado; atrasaria o laboratório e exigiria alinhamento que ainda não existe.
2. **Sem camada semântica (apenas técnico)**: Rejeitado; mesmo mínimo, nomes de atividades e métricas precisam ser estáveis e documentados para mining e IA.
3. **Adotar ferramenta de semantic layer já**: Rejeitado para a fase inicial; dbt + glossário + convenções são suficientes até haver demanda clara por catálogo rico.
