import pytest
from council.models import ModelResponse, DISPLAY_NAMES
from council.config import CouncilConfig, VALID_MODELS


def make_config(**kwargs):
    defaults = dict(
        models=["openai/gpt-4o", "anthropic/claude-sonnet-4-6", "google/gemini-1.5-pro"],
        synthesizer="openai/gpt-4o",
        debate_rounds=1,
        openrouter_api_key="test-or",
    )
    defaults.update(kwargs)
    return CouncilConfig(**defaults)


def test_model_response_failed_when_error_set():
    r = ModelResponse(model_id="openai/gpt-4o", display_name="GPT-4o", content="", error="API error")
    assert r.failed is True


def test_model_response_not_failed_when_no_error():
    r = ModelResponse(model_id="openai/gpt-4o", display_name="GPT-4o", content="Hello")
    assert r.failed is False


def test_display_names_exist_for_all_valid_models():
    for model_id in VALID_MODELS:
        assert model_id in DISPLAY_NAMES, f"Missing display name for {model_id}"


@pytest.mark.asyncio
async def test_query_model_success(mocker):
    mock_client = mocker.AsyncMock()
    mock_client.chat.completions.create.return_value = mocker.MagicMock(
        choices=[mocker.MagicMock(message=mocker.MagicMock(content="Paris"))]
    )
    mocker.patch("council.models.AsyncOpenAI", return_value=mock_client)
    from council.models import query_model
    result = await query_model("openai/gpt-4o", "What is the capital of France?", make_config())
    assert result.content == "Paris"
    assert result.failed is False


@pytest.mark.asyncio
async def test_query_model_failure(mocker):
    mock_client = mocker.AsyncMock()
    mock_client.chat.completions.create.side_effect = Exception("Rate limit")
    mocker.patch("council.models.AsyncOpenAI", return_value=mock_client)
    from council.models import query_model
    result = await query_model("openai/gpt-4o", "test", make_config())
    assert result.failed is True
    assert "Rate limit" in result.error


@pytest.mark.asyncio
async def test_query_all_returns_one_response_per_model(mocker):
    from council.models import query_all, query_model as qm
    async def mock_query(model_id, prompt, config):
        return ModelResponse(model_id=model_id, display_name=model_id, content=f"answer-{model_id}")
    mocker.patch("council.models.query_model", side_effect=mock_query)
    config = make_config(models=["openai/gpt-4o", "anthropic/claude-sonnet-4-6"])
    results = await query_all(["openai/gpt-4o", "anthropic/claude-sonnet-4-6"], "test", config)
    assert len(results) == 2
    assert {r.model_id for r in results} == {"openai/gpt-4o", "anthropic/claude-sonnet-4-6"}


@pytest.mark.asyncio
async def test_query_model_uses_openrouter_base_url(mocker):
    """Verify that query_model connects via OpenRouter, not direct provider APIs."""
    captured = {}
    def capture_client(api_key, base_url):
        captured["base_url"] = base_url
        m = mocker.AsyncMock()
        m.chat.completions.create.return_value = mocker.MagicMock(
            choices=[mocker.MagicMock(message=mocker.MagicMock(content="ok"))]
        )
        return m
    mocker.patch("council.models.AsyncOpenAI", side_effect=capture_client)
    from council.models import query_model, OPENROUTER_BASE_URL
    await query_model("openai/gpt-4o", "test", make_config())
    assert captured["base_url"] == OPENROUTER_BASE_URL
