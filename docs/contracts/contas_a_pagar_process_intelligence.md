# CONTRACT — PROCESS INTELLIGENCE
## Processo: Contas a Pagar (Protheus)

**Versão do contrato:** v1 (canônico)  
**Este documento é a fonte única de verdade** para modelagem dbt, event log, análises de process mining e integrações com IA (Cortex). Alterações em modelos, código ou documentação devem aderir a este contrato.

---

## 1. OBJETIVO

Definir o contrato semântico e técnico para modelagem de Process Intelligence do processo de Contas a Pagar no Protheus.

Este documento é a fonte única de verdade para:

- modelagem dbt
- event log
- análises de process mining
- integrações com IA (Cortex)

---

## 2. DEFINIÇÃO DO CASO

### Regra fundamental

> **1 caso = 1 título financeiro (SE2)**

### Chave do caso (case_id)

Composição obrigatória:

- E2_FILIAL
- E2_PREFIXO
- E2_NUM
- E2_PARCELA
- E2_TIPO
- E2_FORNECE
- E2_LOJA

### Regra de normalização

Todos os campos textuais devem usar `TRIM` nos componentes da chave para evitar colisão por espaços do Protheus.

Exemplo de normalização de um componente:

```sql
TRIM(campo)
```

O `case_id` é a concatenação dos 7 campos, cada um normalizado com `TRIM` antes da concatenação (ex.: separador `|` entre campos).
