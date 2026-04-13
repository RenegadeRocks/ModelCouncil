import pytest
from council.models import ModelResponse, DISPLAY_NAMES
from council.config import CouncilConfig, VALID_MODELS


def make_config(**kwargs):
    defaults = dict(
        models=["gpt-4o", "claude-sonnet-4-6", "gemini-1.5-pro"],
        synthesizer="gpt-4o", debate_rounds=1,
        openai_api_key="test", anthropic_api_key="test", google_api_key="test"
    )
    defaults.update(kwargs)
    return CouncilConfig(**defaults)


def test_model_response_failed_when_error_set():
    r = ModelResponse(model_id="gpt-4o", display_name="GPT-4o", content="", error="API error")
    assert r.failed is True


def test_model_response_not_failed_when_no_error():
    r = ModelResponse(model_id="gpt-4o", display_name="GPT-4o", content="Hello")
    assert r.failed is False


def test_display_names_exist_for_all_valid_models():
    for model_id in VALID_MODELS:
        assert model_id in DISPLAY_NAMES, f"Missing display name for {model_id}"


@pytest.mark.asyncio
async def test_query_openai_success(mocker):
    mock_client = mocker.AsyncMock()
    mock_client.chat.completions.create.return_value = mocker.MagicMock(
        choices=[mocker.MagicMock(message=mocker.MagicMock(content="Paris"))]
    )
    mocker.patch("council.models.AsyncOpenAI", return_value=mock_client)
    from council.models import query_openai
    result = await query_openai("What is the capital of France?", make_config())
    assert result.content == "Paris"
    assert result.failed is False


@pytest.mark.asyncio
async def test_query_openai_failure(mocker):
    mock_client = mocker.AsyncMock()
    mock_client.chat.completions.create.side_effect = Exception("Rate limit")
    mocker.patch("council.models.AsyncOpenAI", return_value=mock_client)
    from council.models import query_openai
    result = await query_openai("test", make_config())
    assert result.failed is True
    assert "Rate limit" in result.error


@pytest.mark.asyncio
async def test_query_all_returns_one_response_per_model(mocker):
    from council.models import query_all, query_model
    async def mock_query(model_id, prompt, config):
        return ModelResponse(model_id=model_id, display_name=model_id, content=f"answer-{model_id}")
    mocker.patch("council.models.query_model", side_effect=mock_query)
    config = make_config(models=["gpt-4o", "claude-sonnet-4-6"])
    results = await query_all(["gpt-4o", "claude-sonnet-4-6"], "test", config)
    assert len(results) == 2
    assert {r.model_id for r in results} == {"gpt-4o", "claude-sonnet-4-6"}
