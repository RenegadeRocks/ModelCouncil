from __future__ import annotations
from council.models import ModelResponse

DEBATE_PROMPT = """You are one of several AI models that answered this question:

QUESTION: {question}

Your answer was:
{own_answer}

The other models answered:
{other_answers}

Now review the other models' answers carefully. For each key point or claim made across all answers:
- State clearly: AGREE, DISAGREE, or PARTIALLY AGREE
- Explain briefly why (1-2 sentences)

Do not simply restate your own answer. Focus on genuine differences in reasoning, approach, or conclusion.
Be specific. If you disagree, say what you disagree with exactly."""


def build_debate_prompt(
    question: str,
    own_response: ModelResponse,
    other_responses: list[ModelResponse],
) -> str:
    other_answers = "\n\n".join(
        f"[{r.display_name}]:\n{r.content}"
        for r in other_responses
        if not r.failed
    )
    return DEBATE_PROMPT.format(
        question=question,
        own_answer=own_response.content,
        other_answers=other_answers,
    )
