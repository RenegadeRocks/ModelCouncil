from council.models import ModelResponse
from council.debate import build_debate_prompt


def make_response(model_id, content, display_name=None, error=None):
    return ModelResponse(
        model_id=model_id,
        display_name=display_name or model_id,
        content=content,
        error=error,
    )


def test_debate_prompt_contains_question():
    own = make_response("openai/gpt-4o", "PostgreSQL is best", "GPT-4o")
    others = [make_response("anthropic/claude-sonnet-4-6", "CockroachDB is best", "Claude")]
    prompt = build_debate_prompt("Best database?", own, others)
    assert "Best database?" in prompt


def test_debate_prompt_contains_own_answer():
    own = make_response("openai/gpt-4o", "PostgreSQL is best", "GPT-4o")
    others = [make_response("anthropic/claude-sonnet-4-6", "CockroachDB is best", "Claude")]
    prompt = build_debate_prompt("Best database?", own, others)
    assert "PostgreSQL is best" in prompt


def test_debate_prompt_contains_other_answers():
    own = make_response("openai/gpt-4o", "PostgreSQL is best", "GPT-4o")
    others = [
        make_response("anthropic/claude-sonnet-4-6", "CockroachDB is best", "Claude"),
        make_response("google/gemini-1.5-pro", "Cassandra is best", "Gemini"),
    ]
    prompt = build_debate_prompt("Best database?", own, others)
    assert "CockroachDB is best" in prompt
    assert "Cassandra is best" in prompt


def test_debate_prompt_excludes_failed_others():
    own = make_response("openai/gpt-4o", "PostgreSQL is best", "GPT-4o")
    failed = ModelResponse(model_id="google/gemini-1.5-pro", display_name="Gemini", content="", error="timeout")
    others = [make_response("anthropic/claude-sonnet-4-6", "CockroachDB is best", "Claude"), failed]
    prompt = build_debate_prompt("Best database?", own, others)
    assert "timeout" not in prompt
    assert "CockroachDB is best" in prompt


def test_debate_prompt_contains_agree_disagree_instruction():
    own = make_response("openai/gpt-4o", "answer", "GPT-4o")
    others = [make_response("anthropic/claude-sonnet-4-6", "other answer", "Claude")]
    prompt = build_debate_prompt("question", own, others)
    assert "AGREE" in prompt
    assert "DISAGREE" in prompt
