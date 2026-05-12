from __future__ import annotations
import asyncio
import time
from rich.console import Console
from rich.rule import Rule
from rich.panel import Panel
from council.config import CouncilConfig
from council.models import ModelResponse, query_all, query_model

import sys
console = Console(file=sys.stdout)


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


async def run_extraction(
    question: str,
    round1: list[ModelResponse],
    debate: list[ModelResponse],
    config: CouncilConfig,
) -> list[dict]:
    from council.table import build_extraction_prompt, parse_extraction, render_table

    active = [r for r in round1 if not r.failed]
    prompt = build_extraction_prompt(question, round1, debate)
    extraction_response = await query_model(config.synthesizer, prompt, config)

    if extraction_response.failed:
        console.print(f"[red]Claim extraction failed: {extraction_response.error}[/red]")
        return []

    try:
        claims = parse_extraction(extraction_response.content, active)
        render_table(claims, active)
        return claims
    except Exception as e:
        console.print(f"[yellow]Could not parse agreement table ({e}). Showing raw positions.[/yellow]")
        for r in debate:
            if not r.failed:
                console.print(f"\n[bold]{r.display_name}[/bold]: {r.content[:400]}")
        return []


async def run_synthesis(
    question: str,
    round1: list[ModelResponse],
    debate: list[ModelResponse],
    config: CouncilConfig,
) -> str:
    from council.debate import build_synthesis_prompt

    synthesis_prompt = build_synthesis_prompt(question, round1, debate)
    response = await query_model(config.synthesizer, synthesis_prompt, config)
    if response.failed:
        return f"Synthesis failed: {response.error}"
    return response.content


async def run_council(question: str, config: CouncilConfig) -> None:
    console.print(Panel(
        f"[bold]{question}[/bold]",
        title="[cyan]⚡ Model Council[/cyan]",
        border_style="cyan",
    ))

    # Round 1
    round1 = await run_round1(question, config)
    active = [r for r in round1 if not r.failed]
    if len(active) < 2:
        console.print("[bold red]Council aborted: fewer than 2 models responded.[/bold red]")
        return

    # Round 2: Debate
    debate = await run_debate(question, round1, config)

    # Agreement table
    console.print(Rule("[bold magenta]Agreement Table[/bold magenta]"))
    await run_extraction(question, round1, debate, config)

    # Final synthesized answer
    console.print(Rule("[bold green]── Final Answer ──[/bold green]"))
    synthesizer_name = next(
        (r.display_name for r in round1 if r.model_id == config.synthesizer),
        config.synthesizer,
    )
    final = await run_synthesis(question, round1, debate, config)
    console.print(Panel(
        final,
        title=f"[green]Synthesized by {synthesizer_name}[/green]",
        border_style="green",
    ))
