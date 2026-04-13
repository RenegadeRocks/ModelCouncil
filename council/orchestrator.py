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
