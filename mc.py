#!/usr/bin/env python3
"""Model Council — multi-model AI debate console."""
import asyncio
import sys
from pathlib import Path

import click

from council.config import load_config
from council.orchestrator import run_council


@click.command()
@click.argument("prompt")
@click.option(
    "--config",
    "config_path",
    default=None,
    show_default=True,
    help="Path to config.json (default: project root config.json)",
)
def main(prompt: str, config_path: str | None) -> None:
    """Send PROMPT to your model council, let them debate, get a synthesized answer."""
    try:
        path = Path(config_path) if config_path else None
        config = load_config(path) if path else load_config()
    except ValueError as e:
        click.echo(f"Config error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error loading config: {e}", err=True)
        sys.exit(1)

    asyncio.run(run_council(prompt, config))


if __name__ == "__main__":
    main()
