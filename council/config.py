from __future__ import annotations
import json
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

VALID_MODELS = {"gpt-4o", "claude-sonnet-4-6", "gemini-1.5-pro"}
DEFAULT_MODELS = ["gpt-4o", "claude-sonnet-4-6", "gemini-1.5-pro"]


@dataclass
class CouncilConfig:
    models: list[str]
    synthesizer: str
    debate_rounds: int
    openai_api_key: str
    anthropic_api_key: str
    google_api_key: str


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
    for m in models:
        if m not in VALID_MODELS:
            raise ValueError(
                f"Unknown model '{m}'. Valid options: {sorted(VALID_MODELS)}"
            )
    if synthesizer not in models:
        raise ValueError(
            f"Synthesizer '{synthesizer}' must be one of the configured models: {models}"
        )

    return CouncilConfig(
        models=models,
        synthesizer=synthesizer,
        debate_rounds=debate_rounds,
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
    )
