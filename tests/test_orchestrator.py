import pytest
from council.models import ModelResponse, DISPLAY_NAMES
from council.config import CouncilConfig


def make_config(models=None):
    return CouncilConfig(
        models=models or ["gpt-4o", "claude-sonnet-4-6", "gemini-1.5-pro"],
        synthesizer="gpt-4o",
        debate_rounds=1,
        openai_api_key="test",
        anthropic_api_key="test",
        google_api_key="test",
    )


def make_response(model_id, content="test answer", error=None):
    return ModelResponse(
        model_id=model_id,
        display_name=DISPLAY_NAMES.get(model_id, model_id),
        content=content,
        error=error,
    )


@pytest.mark.asyncio
async def test_run_round1_returns_all_responses(mocker):
    from council.orchestrator import run_round1
    mock_responses = [
        make_response("gpt-4o", "PostgreSQL"),
        make_response("claude-sonnet-4-6", "CockroachDB"),
        make_response("gemini-1.5-pro", "Cassandra"),
    ]
    mocker.patch("council.orchestrator.query_all", return_value=mock_responses)
    config = make_config()
    results = await run_round1("Best database?", config)
    assert len(results) == 3
    assert results[0].model_id == "gpt-4o"


@pytest.mark.asyncio
async def test_run_round1_includes_failed_response(mocker):
    from council.orchestrator import run_round1
    mock_responses = [
        make_response("gpt-4o", "PostgreSQL"),
        make_response("claude-sonnet-4-6", error="Rate limit exceeded"),
        make_response("gemini-1.5-pro", "Cassandra"),
    ]
    mocker.patch("council.orchestrator.query_all", return_value=mock_responses)
    config = make_config()
    results = await run_round1("Best database?", config)
    assert len(results) == 3
    failed = [r for r in results if r.failed]
    assert len(failed) == 1
    assert failed[0].model_id == "claude-sonnet-4-6"


@pytest.mark.asyncio
async def test_run_debate_skips_failed_round1_model(mocker):
    from council.orchestrator import run_debate

    round1 = [
        make_response("gpt-4o", "PostgreSQL"),
        make_response("claude-sonnet-4-6", error="timeout"),
        make_response("gemini-1.5-pro", "Cassandra"),
    ]
    debate_responses = [
        make_response("gpt-4o", "I agree with Gemini"),
        make_response("gemini-1.5-pro", "I disagree with GPT"),
    ]
    mocker.patch("council.orchestrator.query_model", side_effect=debate_responses)
    config = make_config()
    results = await run_debate("Best database?", round1, config)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_run_debate_returns_empty_when_only_one_active(mocker):
    from council.orchestrator import run_debate

    round1 = [
        make_response("gpt-4o", "PostgreSQL"),
        make_response("claude-sonnet-4-6", error="timeout"),
        make_response("gemini-1.5-pro", error="timeout"),
    ]
    config = make_config()
    results = await run_debate("Best database?", round1, config)
    assert results == []
