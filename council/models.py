from __future__ import annotations
import asyncio
import time
from dataclasses import dataclass
from openai import AsyncOpenAI

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

DISPLAY_NAMES: dict[str, str] = {
    "openai/gpt-4.1": "GPT-4.1",
    "openai/gpt-4o": "GPT-4o",
    "anthropic/claude-sonnet-4-6": "Claude Sonnet 4.6",
    "google/gemini-2.5-pro-preview": "Gemini 2.5 Pro",
    "google/gemini-2.0-flash-001": "Gemini 2.0 Flash",
}


@dataclass
class ModelResponse:
    model_id: str
    display_name: str
    content: str
    error: str | None = None
    elapsed: float = 0.0

    @property
    def failed(self) -> bool:
        return self.error is not None


async def query_model(model_id: str, prompt: str, config) -> ModelResponse:
    start = time.monotonic()
    try:
        client = AsyncOpenAI(
            api_key=config.openrouter_api_key,
            base_url=OPENROUTER_BASE_URL,
        )
        response = await client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
        )
        return ModelResponse(
            model_id=model_id,
            display_name=DISPLAY_NAMES.get(model_id, model_id),
            content=response.choices[0].message.content or "",
            elapsed=time.monotonic() - start,
        )
    except Exception as e:
        return ModelResponse(
            model_id=model_id,
            display_name=DISPLAY_NAMES.get(model_id, model_id),
            content="",
            error=str(e),
            elapsed=time.monotonic() - start,
        )


async def query_all(model_ids: list[str], prompt: str, config) -> list[ModelResponse]:
    tasks = [query_model(mid, prompt, config) for mid in model_ids]
    return list(await asyncio.gather(*tasks))


async def query_all_stream(model_ids: list[str], prompt: str, config):
    """Async generator: yields ModelResponse objects as each model completes (fastest first)."""
    tasks = [asyncio.ensure_future(query_model(mid, prompt, config)) for mid in model_ids]
    for future in asyncio.as_completed(tasks):
        yield await future
