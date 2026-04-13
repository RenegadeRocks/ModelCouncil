import pytest
from council.models import ModelResponse, DISPLAY_NAMES
from council.config import CouncilConfig


def make_config(models=None):
    return CouncilConfig(
        models=models or ["openai/gpt-4o", "anthropic/claude-sonnet-4-6", "google/gemini-1.5-pro"],
        synthesizer="openai/gpt-4o",
        debate_rounds=1,
        openrouter_api_key="test-or",
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
        make_response("openai/gpt-4o", "PostgreSQL"),
        make_response("anthropic/claude-sonnet-4-6", "CockroachDB"),
        make_response("google/gemini-1.5-pro", "Cassandra"),
    ]
    mocker.patch("council.orchestrator.query_all", return_value=mock_responses)
    config = make_config()
    results = await run_round1("Best database?", config)
    assert len(results) == 3
    assert results[0].model_id == "openai/gpt-4o"


@pytest.mark.asyncio
async def test_run_round1_includes_failed_response(mocker):
    from council.orchestrator import run_round1
    mock_responses = [
        make_response("openai/gpt-4o", "PostgreSQL"),
        make_response("anthropic/claude-sonnet-4-6", error="Rate limit exceeded"),
        make_response("google/gemini-1.5-pro", "Cassandra"),
    ]
    mocker.patch("council.orchestrator.query_all", return_value=mock_responses)
    config = make_config()
    results = await run_round1("Best database?", config)
    assert len(results) == 3
    failed = [r for r in results if r.failed]
    assert len(failed) == 1
    assert failed[0].model_id == "anthropic/claude-sonnet-4-6"


@pytest.mark.asyncio
async def test_run_debate_skips_failed_round1_model(mocker):
    from council.orchestrator import run_debate

    round1 = [
        make_response("openai/gpt-4o", "PostgreSQL"),
        make_response("anthropic/claude-sonnet-4-6", error="timeout"),
        make_response("google/gemini-1.5-pro", "Cassandra"),
    ]
    debate_responses = [
        make_response("openai/gpt-4o", "I agree with Gemini"),
        make_response("google/gemini-1.5-pro", "I disagree with GPT"),
    ]
    mocker.patch("council.orchestrator.query_model", side_effect=debate_responses)
    config = make_config()
    results = await run_debate("Best database?", round1, config)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_run_debate_returns_empty_when_only_one_active(mocker):
    from council.orchestrator import run_debate

    round1 = [
        make_response("openai/gpt-4o", "PostgreSQL"),
        make_response("anthropic/claude-sonnet-4-6", error="timeout"),
        make_response("google/gemini-1.5-pro", error="timeout"),
    ]
    config = make_config()
    results = await run_debate("Best database?", round1, config)
    assert results == []


@pytest.mark.asyncio
async def test_run_synthesis_returns_content(mocker):
    from council.orchestrator import run_synthesis

    round1 = [
        make_response("openai/gpt-4o", "PostgreSQL"),
        make_response("anthropic/claude-sonnet-4-6", "CockroachDB"),
    ]
    debate = [
        make_response("openai/gpt-4o", "I disagree with Claude"),
        make_response("anthropic/claude-sonnet-4-6", "I partially agree"),
    ]
    mocker.patch(
        "council.orchestrator.query_model",
        return_value=make_response("openai/gpt-4o", "Final: PostgreSQL for most cases"),
    )
    config = make_config()
    result = await run_synthesis("Best database?", round1, debate, config)
    assert "PostgreSQL" in result


@pytest.mark.asyncio
async def test_run_synthesis_returns_error_message_on_failure(mocker):
    from council.orchestrator import run_synthesis

    round1 = [make_response("openai/gpt-4o", "answer")]
    debate = [make_response("openai/gpt-4o", "debate")]
    mocker.patch(
        "council.orchestrator.query_model",
        return_value=ModelResponse(
            model_id="openai/gpt-4o", display_name="GPT-4o",
            content="", error="timeout"
        ),
    )
    config = make_config()
    result = await run_synthesis("question?", round1, debate, config)
    assert "Synthesis failed" in result
