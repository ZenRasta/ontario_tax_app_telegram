"""Utility functions for interacting with the OpenRouter API."""
from __future__ import annotations

import httpx

from ..core.config import settings


async def chat_completion(
    messages: list[dict[str, str]],
    model: str | None = None,
) -> str:
    """Call the OpenRouter chat completion endpoint.

    Args:
        messages: Conversation messages following the OpenAI chat format.
        model: Optional model override. Defaults to ``settings.OPENROUTER_MODEL``.

    Returns:
        The trimmed content string from the first choice in the response.

    Raises:
        RuntimeError: If ``OPENROUTER_API_KEY`` is not configured.
        httpx.HTTPStatusError: If the API returns a non-success status code.
        httpx.RequestError: For network related errors.
    """

    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    base_url = settings.OPENROUTER_BASE_URL
    chosen_model = model or settings.OPENROUTER_MODEL

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": chosen_model, "messages": messages},
        )
        resp.raise_for_status()
        data = resp.json()
        content = data.get("choices", [])[0]["message"].get("content", "")
        return content.strip()
