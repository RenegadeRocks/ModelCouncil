import pytest
from council.models import ModelResponse
from council.table import parse_extraction, build_extraction_prompt, POSITION_SYMBOLS


def make_response(model_id, content="answer", display_name=None, error=None):
    return ModelResponse(
        model_id=model_id,
        display_name=display_name or model_id,
        content=content,
        error=error,
    )


def test_parse_extraction_valid_json():
    json_text = '''
    {
      "claims": [
        {
          "claim": "PostgreSQL is best for writes",
          "positions": {
            "openai/gpt-4o": "AGREE",
            "anthropic/claude-sonnet-4-6": "DISAGREE",
            "google/gemini-1.5-pro": "PARTIAL"
          }
        }
      ]
    }
    '''
    active = [
        make_response("openai/gpt-4o"),
        make_response("anthropic/claude-sonnet-4-6"),
        make_response("google/gemini-1.5-pro"),
    ]
    claims = parse_extraction(json_text, active)
    assert len(claims) == 1
    assert claims[0]["claim"] == "PostgreSQL is best for writes"
    assert claims[0]["positions"]["openai/gpt-4o"] == "AGREE"


def test_parse_extraction_strips_markdown_fences():
    json_text = '```json\n{"claims": []}\n```'
    active = [make_response("openai/gpt-4o")]
    claims = parse_extraction(json_text, active)
    assert claims == []


def test_parse_extraction_raises_on_invalid_json():
    with pytest.raises(Exception):
        parse_extraction("not valid json at all", [])


def test_build_extraction_prompt_contains_question():
    round1 = [make_response("openai/gpt-4o", "PostgreSQL")]
    debate = [make_response("openai/gpt-4o", "I agree")]
    prompt = build_extraction_prompt("Best database?", round1, debate)
    assert "Best database?" in prompt


def test_build_extraction_prompt_excludes_failed_responses():
    round1 = [
        make_response("openai/gpt-4o", "PostgreSQL"),
        make_response("anthropic/claude-sonnet-4-6", error="timeout"),
    ]
    debate = [make_response("openai/gpt-4o", "I agree")]
    prompt = build_extraction_prompt("Best database?", round1, debate)
    assert "timeout" not in prompt


def test_position_symbols_defined_for_all_positions():
    assert "AGREE" in POSITION_SYMBOLS
    assert "DISAGREE" in POSITION_SYMBOLS
    assert "PARTIAL" in POSITION_SYMBOLS
