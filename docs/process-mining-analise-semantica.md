# Análise semântica — Process Mining Contas a Pagar (Protheus)

Documento de apoio à análise crítica do fluxo de contas a pagar: visão semântica dos caminhos, inconsistências, sugestões de enriquecimento do log e de tabelas Protheus.

---

## 1. Visão semântica do processo

### a) Pagamento real (com SE5)

- **Definição:** Casos que terminam em **PAGAMENTO_REALIZADO** (evidência bancária no SE5).
- **Interpretação:** Fluxo que passou por borderô/CNAB ou integração bancária; há registro de pagamento no banco.
- **Caminho típico:**  
  `TITULO_CRIADO → EVENTO_FINANCEIRO_GERADO → TITULO_LIBERADO → LANCAMENTO_CONTABIL → PAGAMENTO_REALIZADO`
- **Observação:** Não confundir com “pagamento” apenas contábil; aqui há **movimentação financeira real**.

### b) Baixa manual / operacional (sem SE5)

- **Definição:** Casos que terminam em **BAIXA_SEM_SE5** (saldo zerado + E2_BAIXA preenchida, sem registro em SE5).
- **Interpretação:** Baixa no título (provisão, acordo, transferência, compensação interna, ajuste manual) **sem** passagem por arquivo bancário/SE5.
- **Caminho típico:**  
  `TITULO_CRIADO → EVENTO_FINANCEIRO_GERADO → TITULO_LIBERADO → LANCAMENTO_CONTABIL → BAIXA_SEM_SE5`
- **Risco de processo:** Volume alto (ex.: ~39k casos) exige política clara: quando é aceitável não passar por SE5 (ex.: baixa por acordo, compensação) vs. quando deveria haver pagamento bancário e não há.

### c) Fluxos incompletos ou anômalos

- **Definição:** Casos que **não** terminam em PAGAMENTO_REALIZADO nem em BAIXA_SEM_SE5 (ex.: só TITULO_CRIADO, ou só EVENTO_FINANCEIRO_GERADO).
- **Interpretação:** Título ainda em andamento, cancelado, ou **inconsistência** (ex.: evento técnico sem título criado no mesmo case_id).
- **Exemplo crítico:** Variante com **apenas EVENTO_FINANCEIRO_GERADO** (42.626 casos na análise técnica) indica que o case_id do FK7 não está alinhado ao case_id do SE2, ou títulos criados só no financeiro sem emissão de título contábil no SE2 no mesmo caso.

---

## 2. Inconsistências e perguntas de investigação

### 2.1 Por que existem casos com apenas EVENTO_FINANCEIRO_GERADO?

- **Hipótese 1:** Chave de caso (case_id) no FK7 não casa com a chave do SE2 (ex.: documento financeiro referenciando outro título ou filial).
- **Hipótese 2:** Título “virtual” ou evento gerado antes do título contábil ser efetivado no SE2.
- **Hipótese 3:** Dados de sistemas diferentes (financeiro vs. contábil) com regras de chave distintas.
- **Ação sugerida:** Cruzar FK7 com SE2 pela chave de 7 campos; contar quantos FK7 não têm SE2 correspondente e quantos SE2 não têm FK7. No **semantic log** (ancorado em TITULO_CRIADO) essa variante some se o case_id for só o do SE2.

### 2.2 Por que alguns casos pulam TITULO_LIBERADO?

- **Interpretação:** TITULO_LIBERADO vem de E2_DATALIB. Se há LANCAMENTO_CONTABIL ou pagamento/baixa sem TITULO_LIBERADO, pode ser:
  - Liberação automática (campo não preenchido),
  - Ou fluxo que não exige liberação (ex.: valor baixo, conta específica).
- **Ação sugerida:** Incluir no log um atributo derivado `tem_titulo_liberado` (booleano) e comparar variantes com e sem essa etapa.

### 2.3 BAIXA_SEM_SE5 acontece antes ou depois de LANCAMENTO_CONTABIL?

- **Relevância:** Se BAIXA_SEM_SE5 ocorre **antes** de LANCAMENTO_CONTABIL, o título foi baixado sem lançamento contábil prévio (possível ajuste manual ou regra de negócio específica).
- **Métrica:** O script `process_mining_semantic_analysis.py` imprime quantos casos têm BAIXA_SEM_SE5 antes vs. depois de LANCAMENTO_CONTABIL.
- **Ação sugerida:** Separar variantes “BAIXA_SEM_SE5 depois de LANCAMENTO” (fluxo esperado) das “BAIXA_SEM_SE5 antes de LANCAMENTO” (exceção a documentar).

---

## 3. Enriquecimento do event log

Colunas adicionais sugeridas para melhorar a análise:

| Coluna sugerida        | Fonte / observação |
|------------------------|--------------------|
| `tipo_baixa`           | Derivado: manual (E2_LOJA/usuário) vs. automática (job, integração). Ajuda a separar baixa operacional manual de automática. |
| `origem_pagamento`     | SE5 + FK1/FK5: borderô, CNAB, manual, compensação. Diferencia pagamento bancário de outros tipos. |
| `indicador_cnab`       | Booleano: passou por FK5 (CNAB)? Útil para filtrar “pagamento bancário típico”. |
| `usuario_baixa`        | E2_LOJA ou tabela de usuários na baixa. Análise por responsável e detecção de padrões manuais. |
| `timestamp_negocio`    | Data de negócio (E2_EMISSAO, E2_BAIXA) vs. `timestamp_tecnico` (DBALTERACAO). Já temos `timestamp_confiabilidade`; expandir para colunas explícitas. |
| `valor_titulo`         | E2_VALOR no nível do caso. Análise por faixa de valor (ex.: baixas manuais em valores altos). |
| `filial` / `conta`     | Componentes do case_id ou dimensões. Segmentar por unidade ou conta. |

Prioridade para as próximas rodadas: `origem_pagamento` (ou indicador CNAB), `tipo_baixa` e `usuario_baixa`.

---

## 4. Tabelas Protheus que podem fechar o fluxo

Além de **SE2, FK7, FK2, SE5, FK1, FK5, FK6**, outras tabelas úteis:

| Tabela / conceito     | Uso |
|----------------------|-----|
| **SE1** (contas a receber) | Compensação: título a pagar baixado contra título a receber. |
| **Movimentação bancária (conta corrente)** | Conferir se há débito em conta em casos “BAIXA_SEM_SE5” (pagamento fora do SE5?). |
| **Histórico de baixa / tabela de baixa** | Origem da baixa (manual, job, integração), usuário, data. |
| **E2_DATACAN / E2_USUACAN** | Cancelamento; no ambiente atual podem estar vazios, mas ajudam a marcar “TITULO_CANCELADO” quando preenchidos. |
| **Controle de borderô** | Qual borderô (FK1) gerou qual SE5; fechar ciclo pagamento bancário. |
| **Contas contábeis (plano de contas)** | Filtrar por tipo de conta (ex.: provisionado vs. não provisionado) para interpretar BAIXA_SEM_SE5. |

Perguntas que essas tabelas ajudam a responder:

- Pagamentos manuais: usuário e data da baixa (E2_LOJA, tabela de baixa).
- Compensações internas: SE1 + SE2 (titulos a pagar x a receber).
- Baixa direta no título: E2_BAIXA preenchida sem SE5 e sem FK1/FK5; cruzar com histórico/usuário.

---

## 5. Análise crítica (processo financeiro)

- **Separação COM_SE5 vs SEM_SE5:** Necessária para não misturar “pagamento bancário” com “baixa operacional”. Métricas de tempo e variantes devem ser analisadas por segmento.
- **Variante “só EVENTO_FINANCEIRO_GERADO”:** Inconsistência de modelagem ou de chave de caso; no semantic log ancorado em TITULO_CRIADO ela deixa de aparecer, mas a causa (FK7 sem SE2 no mesmo caso) deve ser tratada na origem dos dados.
- **Volume de BAIXA_SEM_SE5:** 39k+ casos exige regra de negócio clara e, se possível, sinalização no log (tipo_baixa, origem) para auditoria e conformidade.
- **Ordem BAIXA vs LANCAMENTO:** Casos com BAIXA_SEM_SE5 antes de LANCAMENTO_CONTABIL são exceção de processo e devem ser listados e revisados.

---

## 6. Uso do script de análise semântica

```bash
# Preferir log semântico (já ancorado em TITULO_CRIADO)
python scripts/process_mining_semantic_analysis.py data/marts/cp_event_log_semantic.parquet

# Ou log técnico
python scripts/process_mining_semantic_analysis.py data/marts/event_log.parquet

# Opções
python scripts/process_mining_semantic_analysis.py data/marts/cp_event_log_semantic.parquet \
  --min-dfg-ratio 0.03 --tree-coverage 0.85
```

Saídas em `output/process_mining/`:

- `dfg_com_se5.png`, `dfg_sem_se5.png` — DFG por segmento.
- `heuristics_net_com_se5.png`, `heuristics_net_sem_se5.png` — Heuristics Net por segmento.
- `dfg_filtered_frequency.png` — DFG com arcos pouco frequentes removidos.
- `process_tree_dominant.png` — Process tree apenas com variantes que cobrem X% dos casos (ex.: 80%).

O script ainda imprime no console: classificação semântica (a, b, c), indicadores para inconsistências (EVENTO_FINANCEIRO_GERADO isolado, pulo de TITULO_LIBERADO, BAIXA antes/depois de LANCAMENTO).
