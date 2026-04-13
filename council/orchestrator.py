from __future__ import annotations
import asyncio
import time
from rich.console import Console
from rich.rule import Rule
from rich.panel import Panel
from council.config import CouncilConfig
from council.models import ModelResponse, query_all, query_model

console = Console()


async def run_round1(question: str, config: CouncilConfig) -> list[ModelResponse]:
    console.print(Rule("[bold blue]Round 1: Initial Answers[/bold blue]"))
    start = time.monotonic()
    responses = await query_all(config.models, question, config)
    elapsed = time.monotonic() - start

    for r in responses:
        if r.failed:
            console.print(f"\n[bold red][{r.display_name}] FAILED[/bold red]: {r.error}")
        else:
            console.print(f"\n[bold green][{r.display_name}][/bold green] ({r.elapsed:.1f}s)")
            console.print(r.content)

    active = [r for r in responses if not r.failed]
    console.print(
        f"\n[dim]Round 1 complete in {elapsed:.1f}s. "
        f"{len(active)}/{len(config.models)} models responded.[/dim]"
    )
    return responses


async def run_debate(
    question: str,
    round1: list[ModelResponse],
    config: CouncilConfig,
) -> list[ModelResponse]:
    from council.debate import build_debate_prompt

    console.print(Rule("[bold yellow]Round 2: Debate[/bold yellow]"))
    active = [r for r in round1 if not r.failed]

    if len(active) < 2:
        console.print("[red]Not enough models for a debate (need at least 2).[/red]")
        return []

    debate_tasks = []
    for r in active:
        others = [o for o in active if o.model_id != r.model_id]
        prompt = build_debate_prompt(question, r, others)
        debate_tasks.append(query_model(r.model_id, prompt, config))

    start = time.monotonic()
    debate_responses = list(await asyncio.gather(*debate_tasks))
    elapsed = time.monotonic() - start

    for r in debate_responses:
        if r.failed:
            console.print(f"\n[bold red][{r.display_name}] FAILED[/bold red]: {r.error}")
        else:
            console.print(f"\n[bold yellow][{r.display_name}][/bold yellow] ({r.elapsed:.1f}s)")
            console.print(r.content)

    console.print(f"\n[dim]Round 2 complete in {elapsed:.1f}s.[/dim]")
    return debate_responses
