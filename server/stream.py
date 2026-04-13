from __future__ import annotations
import asyncio
import json
from council.config import CouncilConfig
from council.models import ModelResponse, query_all_stream, query_model
from council.debate import build_debate_prompt
from council.table import build_extraction_prompt, parse_extraction


async def council_stream(question: str, config: CouncilConfig):
    """Async generator yielding JSON strings for SSE data lines."""

    # ── Round 1 ──────────────────────────────────────────────────────────────
    yield json.dumps({"type": "phase", "phase": "round1"})

    round1: list[ModelResponse] = []
    async for response in query_all_stream(config.models, question, config):
        round1.append(response)
        yield json.dumps({
            "type": "model_response",
            "phase": "round1",
            "model_id": response.model_id,
            "display_name": response.display_name,
            "content": response.content,
            "error": response.error,
            "elapsed": round(response.elapsed, 1),
        })

    active = [r for r in round1 if not r.failed]
    if len(active) < 2:
        yield json.dumps({"type": "error", "message": "Fewer than 2 models responded in Round 1."})
        yield json.dumps({"type": "done"})
        return

    # ── Round 2: Debate ───────────────────────────────────────────────────────
    yield json.dumps({"type": "phase", "phase": "debate"})

    debate_tasks = []
    for r in active:
        others = [o for o in active if o.model_id != r.model_id]
        prompt = build_debate_prompt(question, r, others)
        debate_tasks.append(query_model(r.model_id, prompt, config))

    debate: list[ModelResponse] = list(await asyncio.gather(*debate_tasks))
    for r in debate:
        yield json.dumps({
            "type": "model_response",
            "phase": "debate",
            "model_id": r.model_id,
            "display_name": r.display_name,
            "content": r.content,
            "error": r.error,
            "elapsed": round(r.elapsed, 1),
        })

    # ── Agreement Table ───────────────────────────────────────────────────────
    yield json.dumps({"type": "phase", "phase": "extracting"})

    extraction_prompt = build_extraction_prompt(question, round1, debate)
    extraction_response = await query_model(config.synthesizer, extraction_prompt, config)

    if not extraction_response.failed:
        try:
            claims = parse_extraction(extraction_response.content, active)
            yield json.dumps({
                "type": "table",
                "claims": claims,
                "models": [
                    {"model_id": r.model_id, "display_name": r.display_name}
                    for r in active
                ],
            })
        except Exception as e:
            yield json.dumps({"type": "table_error", "message": str(e)})
    else:
        yield json.dumps({"type": "table_error", "message": extraction_response.error})

    # ── Synthesis ─────────────────────────────────────────────────────────────
    yield json.dumps({"type": "phase", "phase": "synthesizing"})

    round1_text = "\n\n".join(
        f"[{r.display_name}]: {r.content}" for r in round1 if not r.failed
    )
    debate_text = "\n\n".join(
        f"[{r.display_name}]: {r.content}" for r in debate if not r.failed
    )
    synthesis_prompt = f"""You have moderated a multi-model AI council on this question:

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

    final = await query_model(config.synthesizer, synthesis_prompt, config)
    synthesizer_name = next(
        (r.display_name for r in round1 if r.model_id == config.synthesizer),
        config.synthesizer,
    )
    yield json.dumps({
        "type": "final_answer",
        "content": final.content if not final.failed else f"Synthesis failed: {final.error}",
        "synthesizer": synthesizer_name,
    })

    yield json.dumps({"type": "done"})
