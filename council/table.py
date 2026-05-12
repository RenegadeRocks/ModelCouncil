from __future__ import annotations
import json
import re
import sys
from council.models import ModelResponse
from rich.console import Console
from rich.table import Table

POSITION_SYMBOLS: dict[str, str] = {
    "AGREE": "[green]✅ Agree[/green]",
    "DISAGREE": "[red]❌ Disagree[/red]",
    "PARTIAL": "[yellow]⚠  Partial[/yellow]",
}

EXTRACTION_PROMPT = """You are analyzing a multi-model AI debate. Extract key claims and model positions.

QUESTION: {question}

ROUND 1 ANSWERS:
{round1}

DEBATE RESPONSES:
{debate}

Identify 3-5 key claims from the Round 1 answers. For each claim, determine each model's position from their debate response.

Respond ONLY with valid JSON — no other text:
{{
  "claims": [
    {{
      "claim": "Brief claim text (max 10 words)",
      "positions": {{
        "model_id_here": "AGREE",
        "model_id_here": "DISAGREE",
        "model_id_here": "PARTIAL"
      }}
    }}
  ]
}}

Use exactly: AGREE, DISAGREE, or PARTIAL. Use the model IDs exactly as shown in the answers."""


def build_extraction_prompt(
    question: str,
    round1: list[ModelResponse],
    debate: list[ModelResponse],
) -> str:
    round1_text = "\n\n".join(
        f"[{r.model_id}] {r.display_name}:\n{r.content}"
        for r in round1
        if not r.failed
    )
    debate_text = "\n\n".join(
        f"[{r.model_id}] {r.display_name}:\n{r.content}"
        for r in debate
        if not r.failed
    )
    return EXTRACTION_PROMPT.format(
        question=question,
        round1=round1_text,
        debate=debate_text,
    )


def parse_extraction(json_text: str, active_models: list[ModelResponse]) -> list[dict]:
    text = json_text.strip()
    match = re.search(r"```(?:json)?\s*\n(.*?)```", text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    data = json.loads(text)
    return data.get("claims", [])


def render_table(claims: list[dict], active_models: list[ModelResponse]) -> None:
    console = Console(file=sys.stdout)
    table = Table(
        title="Agreement Table",
        show_header=True,
        header_style="bold magenta",
        border_style="magenta",
    )
    table.add_column("Key Claim", style="cyan", max_width=42)
    for model in active_models:
        table.add_column(model.display_name, justify="center", min_width=14)

    for claim_data in claims:
        row = [claim_data["claim"]]
        for model in active_models:
            position = claim_data["positions"].get(model.model_id, "—")
            row.append(POSITION_SYMBOLS.get(position, position))
        table.add_row(*row)

    console.print(table)
