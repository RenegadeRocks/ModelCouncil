from __future__ import annotations
import asyncio
import time
from dataclasses import dataclass, field
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from google import genai as google_genai

DISPLAY_NAMES: dict[str, str] = {
    "gpt-4o": "GPT-4o",
    "claude-sonnet-4-6": "Claude Sonnet 4.6",
    "gemini-1.5-pro": "Gemini 1.5 Pro",
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


async def query_openai(prompt: str, config) -> ModelResponse:
    model_id = "gpt-4o"
    start = time.monotonic()
    try:
        client = AsyncOpenAI(api_key=config.openai_api_key)
        response = await client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
        )
        return ModelResponse(
            model_id=model_id,
            display_name=DISPLAY_NAMES[model_id],
            content=response.choices[0].message.content or "",
            elapsed=time.monotonic() - start,
        )
    except Exception as e:
        return ModelResponse(
            model_id=model_id,
            display_name=DISPLAY_NAMES[model_id],
            content="",
            error=str(e),
            elapsed=time.monotonic() - start,
        )


async def query_anthropic(prompt: str, config) -> ModelResponse:
    model_id = "claude-sonnet-4-6"
    start = time.monotonic()
    try:
        client = AsyncAnthropic(api_key=config.anthropic_api_key)
        response = await client.messages.create(
            model=model_id,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return ModelResponse(
            model_id=model_id,
            display_name=DISPLAY_NAMES[model_id],
            content=response.content[0].text,
            elapsed=time.monotonic() - start,
        )
    except Exception as e:
        return ModelResponse(
            model_id=model_id,
            display_name=DISPLAY_NAMES[model_id],
            content="",
            error=str(e),
            elapsed=time.monotonic() - start,
        )


async def query_gemini(prompt: str, config) -> ModelResponse:
    model_id = "gemini-1.5-pro"
    start = time.monotonic()
    try:
        client = google_genai.Client(api_key=config.google_api_key)
        response = await client.aio.models.generate_content(
            model=model_id,
            contents=prompt,
        )
        return ModelResponse(
            model_id=model_id,
            display_name=DISPLAY_NAMES[model_id],
            content=response.text,
            elapsed=time.monotonic() - start,
        )
    except Exception as e:
        return ModelResponse(
            model_id=model_id,
            display_name=DISPLAY_NAMES[model_id],
            content="",
            error=str(e),
            elapsed=time.monotonic() - start,
        )


_QUERY_FNS = {
    "gpt-4o": query_openai,
    "claude-sonnet-4-6": query_anthropic,
    "gemini-1.5-pro": query_gemini,
}


async def query_model(model_id: str, prompt: str, config) -> ModelResponse:
    fn = _QUERY_FNS.get(model_id)
    if fn is None:
        raise ValueError(f"No query function for model: {model_id}")
    return await fn(prompt, config)


async def query_all(model_ids: list[str], prompt: str, config) -> list[ModelResponse]:
    tasks = [query_model(mid, prompt, config) for mid in model_ids]
    return list(await asyncio.gather(*tasks))
