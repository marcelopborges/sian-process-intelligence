"""
Abstração para integração com LLMs.

Permite trocar provedor (OpenAI, Anthropic, modelo interno) sem alterar
chamadores em analysis.py e recommendations.py. Não expõe dados sensíveis
em logs; API key e endpoint vêm de ambiente.
"""
from __future__ import annotations

from typing import Any


def complete(
    prompt: str,
    system_prompt: str | None = None,
    max_tokens: int = 2048,
    **kwargs: Any,
) -> str:
    """
    Envia prompt ao LLM e retorna resposta em texto.

    Args:
        prompt: Prompt do usuário.
        system_prompt: Instruções de sistema (opcional).
        max_tokens: Limite de tokens na resposta.
        **kwargs: Temperatura, etc.

    Returns:
        Texto da resposta. Em caso de falha (sem config, API error), levantar exceção
        ou retornar string de fallback conforme política do projeto.

    TODO:
        - Ler LLM_API_KEY, LLM_MODEL, LLM_BASE_URL de config.
        - Chamar API do provedor configurado.
        - Tratar erros e timeouts.
        - Não logar conteúdo de prompt/response se houver dados sensíveis.
    """
    raise NotImplementedError("LLM client a implementar quando integrar modelo.")
