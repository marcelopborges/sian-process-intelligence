"""Mapas de keywords e tabelas esperadas para inferência de eventos a partir do SX3."""

# Tabela esperada por atividade (boost de confiança)
EXPECTED_TABLE: dict[str, str] = {
    "TITULO_CRIADO": "SE2",
    "TITULO_LIBERADO": "SE2",
    "LANCAMENTO_CONTABIL": "FK2",
    "PAGAMENTO_REALIZADO": "SE5",
    "BAIXA_SEM_SE5": "SE2",
}

KEYWORD_MAP: dict[str, list[str]] = {
    "TITULO_CRIADO": ["EMISSAO", "EMISSA", "EMIT"],
    "TITULO_LIBERADO": ["LIBERACAO", "LIBERAC", "DATALIB", "DT LIBERAC"],
    "LANCAMENTO_CONTABIL": ["LANC", "DIARIO", "CONTABIL"],
    "PAGAMENTO_REALIZADO": [
        "PAGAMENTO",
        "MOVIMENTACAO",
        "CREDITO",
        "DEBITO",
        "BANCO",
        "DATA DA MOVIMENT",
    ],
    "BAIXA_SEM_SE5": ["BAIXA", "DATA DE BAIXA", "STATUS DA BAIXA"],
    "EVENTO_FINANCEIRO_GERADO": ["EVENTO", "FINANCEIRO", "GERADO"],
}
