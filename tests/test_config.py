import json
import pytest
from pathlib import Path
from council.config import load_config, CouncilConfig, VALID_MODELS


def test_load_defaults_when_no_config_file(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google")
    config = load_config(tmp_path / "nonexistent.json")
    assert len(config.models) == 3
    assert config.synthesizer == config.models[0]
    assert config.openai_api_key == "test-openai"


def test_load_custom_models(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    monkeypatch.setenv("GOOGLE_API_KEY", "k")
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({
        "models": ["gpt-4o", "claude-sonnet-4-6"],
        "synthesizer": "gpt-4o",
    }))
    config = load_config(cfg_file)
    assert config.models == ["gpt-4o", "claude-sonnet-4-6"]
    assert config.synthesizer == "gpt-4o"


def test_raises_on_too_few_models(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    monkeypatch.setenv("GOOGLE_API_KEY", "k")
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"models": ["gpt-4o"], "synthesizer": "gpt-4o"}))
    with pytest.raises(ValueError, match="At least 2 models"):
        load_config(cfg_file)


def test_raises_on_invalid_model(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    monkeypatch.setenv("GOOGLE_API_KEY", "k")
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"models": ["gpt-4o", "llama-unknown"], "synthesizer": "gpt-4o"}))
    with pytest.raises(ValueError, match="Unknown model"):
        load_config(cfg_file)


def test_raises_when_synthesizer_not_in_models(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    monkeypatch.setenv("GOOGLE_API_KEY", "k")
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({
        "models": ["gpt-4o", "claude-sonnet-4-6"],
        "synthesizer": "gemini-1.5-pro",
    }))
    with pytest.raises(ValueError, match="Synthesizer"):
        load_config(cfg_file)
