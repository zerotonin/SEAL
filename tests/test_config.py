# ╔══════════════════════════════════════════════════════════════════╗
# ║  sealsim — tests.test_config                                     ║
# ║  « env wins, placeholders lose, missing fails loudly »           ║
# ╠══════════════════════════════════════════════════════════════════╣
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import json

import pytest

from sealsim import config as cfg


def test_env_variable_wins(monkeypatch, tmp_path):
    monkeypatch.setenv("SEALSIM_DATA_ROOT", str(tmp_path))
    assert cfg.get("data_root") == str(tmp_path)
    assert cfg.data_root() == tmp_path


def test_placeholder_counts_as_unset(monkeypatch, tmp_path):
    monkeypatch.delenv("SEALSIM_DATA_ROOT", raising=False)
    monkeypatch.setattr(cfg, "local_paths_file", lambda: tmp_path / "local_paths.json")
    (tmp_path / "local_paths.json").write_text(
        json.dumps({"active_profile": "local",
                    "profiles": {"local": {"data_root": "<fill me>"}}}),
        encoding="utf-8",
    )
    assert cfg.get("data_root") is None
    with pytest.raises(cfg.ConfigError, match="local_paths.template.json"):
        cfg.require("data_root")


def test_profile_selection(monkeypatch, tmp_path):
    monkeypatch.delenv("SEALSIM_DATA_ROOT", raising=False)
    monkeypatch.setattr(cfg, "local_paths_file", lambda: tmp_path / "local_paths.json")
    (tmp_path / "local_paths.json").write_text(
        json.dumps({"active_profile": "local",
                    "profiles": {"local": {"data_root": "/a"},
                                 "hpc": {"data_root": "/b", "slurm_account": "acc"}}}),
        encoding="utf-8",
    )
    assert cfg.get("data_root") == "/a"
    assert cfg.get("data_root", profile="hpc") == "/b"
    monkeypatch.setenv("SEALSIM_PROFILE", "hpc")
    assert cfg.get("data_root") == "/b"
    assert "export SBATCH_ACCOUNT=acc" in cfg._export_lines(None)


def test_unknown_key_rejected():
    with pytest.raises(KeyError):
        cfg.get("nonsense")
