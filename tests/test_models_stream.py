import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from council.models import ModelResponse, query_all_stream


async def fake_query_with_delay(model_id, prompt, config):
    delay = 0.05 if model_id == "fast-model" else 0.15
    await asyncio.sleep(delay)
    return ModelResponse(model_id=model_id, display_name=model_id, content="ok")


@pytest.mark.asyncio
async def test_query_all_stream_yields_in_completion_order():
    """Faster models should be yielded before slower ones."""
    model_ids = ["slow-model", "fast-model"]

    results = []
    with patch("council.models.query_model", side_effect=fake_query_with_delay):
        async for r in query_all_stream(model_ids, "test", config=None):
            results.append(r.model_id)

    assert results == ["fast-model", "slow-model"]


@pytest.mark.asyncio
async def test_query_all_stream_yields_all_models():
    model_ids = ["a", "b", "c"]

    async def fake_query(model_id, prompt, config):
        return ModelResponse(model_id=model_id, display_name=model_id, content="ok")

    results = []
    with patch("council.models.query_model", side_effect=fake_query):
        async for r in query_all_stream(model_ids, "test", config=None):
            results.append(r.model_id)

    assert set(results) == {"a", "b", "c"}
    assert len(results) == 3
