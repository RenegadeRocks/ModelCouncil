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

SYNTHESIS_PROMPT = """You have moderated a multi-model AI council on this question:

QUESTION: {question}

ROUND 1 ANSWERS:
{round1_text}

DEBATE RESPONSES:
{debate_text}

Produce a final synthesized answer that:
1. Reflects the consensus view where models agreed
2. Clearly flags any genuine disagreements that remain unresolved
3. Gives a clear recommendation where consensus exists — do not hedge when models agree
4. Briefly notes where models differ without belaboring it

Write directly. Start with the answer, not commentary about the process.
Add this note at the end on its own line: "Note: Model agreement does not guarantee factual accuracy — models may share training biases." """


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


def build_synthesis_prompt(
    question: str,
    round1: list[ModelResponse],
    debate: list[ModelResponse],
) -> str:
    round1_text = "\n\n".join(
        f"[{r.display_name}]: {r.content}" for r in round1 if not r.failed
    )
    debate_text = "\n\n".join(
        f"[{r.display_name}]: {r.content}" for r in debate if not r.failed
    )
    return SYNTHESIS_PROMPT.format(
        question=question,
        round1_text=round1_text,
        debate_text=debate_text,
    )
