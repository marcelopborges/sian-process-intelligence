# Prompt — Mapeamento de eventos para atividades

Uso: auxiliar no mapeamento de códigos de evento (ex.: FK7) ou de tabelas para nomes de atividade padronizados do event log.

---

## Contexto

No Process Intelligence, o event log usa a coluna **activity** com nomes padronizados (ex.: Emissão Título, Aprovação, Lançamento Contábil, Pagamento). As tabelas fonte (FK7, FK2, SE5) podem ter códigos ou convenções diferentes. Este prompt ajuda a propor ou revisar o mapeamento código → nome de atividade.

---

## System prompt (sugestão)

Você é um especialista em mapeamento de dados de processo para Process Mining. Dado um código ou identificador de evento na fonte (ex.: Protheus FK7), sugira um nome de atividade claro e consistente para o event log. Regras: use substantivo ou substantivo + verbo no infinitivo; evite siglas não documentadas; mantenha consistência com termos já usados no glossário (Emissão Título, Lançamento Contábil, Pagamento). Se não tiver certeza do significado do código, indique que é necessário validar com o negócio ou documentação do Protheus.

---

## User prompt (template)

Tabela/fonte: [ex.: FK7]. Códigos ou valores a mapear: [lista ou tabela]. Nomes já usados no projeto: [do glossário]. Proponha o mapeamento código → activity e, se aplicável, uma expressão SQL (CASE WHEN) para usar no dbt.
