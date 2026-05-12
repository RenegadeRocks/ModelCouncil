from __future__ import annotations
import json
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

DEFAULT_MODELS = ["openai/gpt-4.1", "anthropic/claude-sonnet-4-6", "google/gemini-2.5-pro-preview"]


@dataclass
class CouncilConfig:
    models: list[str]
    synthesizer: str
    debate_rounds: int
    openrouter_api_key: str


_PROJECT_ROOT = Path(__file__).parent.parent


def load_config(config_path: Path = _PROJECT_ROOT / "config.json") -> CouncilConfig:
    load_dotenv()

    if config_path.exists():
        with open(config_path) as f:
            data = json.load(f)
    else:
        data = {}

    models = data.get("models", DEFAULT_MODELS)
    if len(models) < 2:
        raise ValueError("At least 2 models required in config.json")
    synthesizer = data.get("synthesizer", models[0])
    debate_rounds = data.get("debate_rounds", 1)
    if len(models) > 4:
        raise ValueError("At most 4 models allowed in config.json")
    if synthesizer not in models:
        raise ValueError(
            f"Synthesizer '{synthesizer}' must be one of the configured models: {models}"
        )

    return CouncilConfig(
        models=models,
        synthesizer=synthesizer,
        debate_rounds=debate_rounds,
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
    )
