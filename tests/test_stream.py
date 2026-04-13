import asyncio
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from council.models import ModelResponse
from council.config import CouncilConfig


def make_config(models=None):
    return CouncilConfig(
        models=models or ["openai/gpt-4.1", "anthropic/claude-sonnet-4-6"],
        synthesizer="anthropic/claude-sonnet-4-6",
        debate_rounds=1,
        openrouter_api_key="test-key",
    )


def make_response(model_id, content="test answer", error=None):
    return ModelResponse(
        model_id=model_id,
        display_name=model_id,
        content=content,
        error=error,
        elapsed=1.0,
    )


async def collect_events(stream):
    events = []
    async for raw in stream:
        events.append(json.loads(raw))
    return events


@pytest.mark.asyncio
async def test_stream_emits_phase_events():
    """Stream must emit phase events for round1, debate, extracting, synthesizing."""
    from server.stream import council_stream

    config = make_config()
    responses = [make_response(mid) for mid in config.models]
    table_json = json.dumps({"claims": [{"claim": "Use PostgreSQL", "positions": {
        "openai/gpt-4.1": "AGREE", "anthropic/claude-sonnet-4-6": "AGREE"
    }}]})

    async def fake_stream(*args, **kwargs):
        for r in responses:
            yield r

    with (
        patch("server.stream.query_all_stream", side_effect=fake_stream),
        patch("server.stream.query_model", new_callable=AsyncMock, return_value=make_response(
            "anthropic/claude-sonnet-4-6", content=table_json
        )),
    ):
        events = await collect_events(council_stream("test question", config))

    types = [e["type"] for e in events]
    assert "phase" in types
    phases = [e["phase"] for e in events if e["type"] == "phase"]
    assert "round1" in phases
    assert "debate" in phases
    assert "done" in [e["type"] for e in events]


@pytest.mark.asyncio
async def test_stream_emits_model_responses_for_round1():
    from server.stream import council_stream

    config = make_config()
    responses = [make_response(mid, f"answer from {mid}") for mid in config.models]
    table_json = json.dumps({"claims": []})

    async def fake_stream(*args, **kwargs):
        for r in responses:
            yield r

    with (
        patch("server.stream.query_all_stream", side_effect=fake_stream),
        patch("server.stream.query_model", new_callable=AsyncMock, return_value=make_response(
            "anthropic/claude-sonnet-4-6", content=table_json
        )),
    ):
        events = await collect_events(council_stream("test question", config))

    round1_events = [e for e in events if e["type"] == "model_response" and e["phase"] == "round1"]
    assert len(round1_events) == 2
    assert all("model_id" in e and "content" in e for e in round1_events)


@pytest.mark.asyncio
async def test_stream_emits_done_on_fewer_than_2_active():
    from server.stream import council_stream

    config = make_config()

    async def fake_stream(*args, **kwargs):
        yield make_response("openai/gpt-4.1", error="API error")
        yield make_response("anthropic/claude-sonnet-4-6", error="API error")

    with patch("server.stream.query_all_stream", side_effect=fake_stream):
        events = await collect_events(council_stream("test question", config))

    types = [e["type"] for e in events]
    assert "error" in types
    assert "done" in types
