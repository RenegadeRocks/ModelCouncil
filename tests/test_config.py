import json
import pytest
from pathlib import Path
from council.config import load_config, CouncilConfig, VALID_MODELS


def test_load_defaults_when_no_config_file(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-or")
    config = load_config(tmp_path / "nonexistent.json")
    assert len(config.models) == 3
    assert config.synthesizer == config.models[0]
    assert config.openrouter_api_key == "test-or"
    assert config.debate_rounds == 1


def test_load_custom_models(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({
        "models": ["openai/gpt-4o", "anthropic/claude-sonnet-4-6"],
        "synthesizer": "openai/gpt-4o",
    }))
    config = load_config(cfg_file)
    assert config.models == ["openai/gpt-4o", "anthropic/claude-sonnet-4-6"]
    assert config.synthesizer == "openai/gpt-4o"


def test_raises_on_too_few_models(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"models": ["openai/gpt-4o"], "synthesizer": "openai/gpt-4o"}))
    with pytest.raises(ValueError, match="At least 2 models"):
        load_config(cfg_file)


def test_raises_on_invalid_model(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"models": ["openai/gpt-4o", "llama-unknown"], "synthesizer": "openai/gpt-4o"}))
    with pytest.raises(ValueError, match="Unknown model"):
        load_config(cfg_file)


def test_raises_on_missing_api_key(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({
        "models": ["openai/gpt-4o", "anthropic/claude-sonnet-4-6"],
        "synthesizer": "openai/gpt-4o",
    }))
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        load_config(cfg_file)


def test_raises_on_zero_debate_rounds(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({
        "models": ["openai/gpt-4o", "anthropic/claude-sonnet-4-6"],
        "debate_rounds": 0,
    }))
    with pytest.raises(ValueError, match="debate_rounds"):
        load_config(cfg_file)


def test_valid_models_list_matches_display_names():
    """Every valid model should have a corresponding display name."""
    from council.models import DISPLAY_NAMES
    for model_id in VALID_MODELS:
        assert model_id in DISPLAY_NAMES, f"Missing display name for {model_id}"


def test_raises_when_synthesizer_not_in_models(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({
        "models": ["openai/gpt-4o", "anthropic/claude-sonnet-4-6"],
        "synthesizer": "google/gemini-1.5-pro",
    }))
    with pytest.raises(ValueError, match="Synthesizer"):
        load_config(cfg_file)
