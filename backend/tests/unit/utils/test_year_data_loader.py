import importlib
from pathlib import Path
import pytest

import app.utils.year_data_loader as ydl


def test_parse_stream_json_fallback(monkeypatch, tmp_path):
    monkeypatch.setattr(ydl, "yaml", None)
    p = tmp_path / "simple.yaml"
    p.write_text('{"2025": {"ON": {"flag": 1}}}')
    with p.open() as fh:
        data = ydl._parse_stream(fh, p)
    assert data["2025"]["ON"]["flag"] == 1


def test_parse_stream_error_message(monkeypatch, tmp_path):
    monkeypatch.setattr(ydl, "yaml", None)
    p = tmp_path / "bad.yaml"
    p.write_text("key: value\n# comment")
    with p.open() as fh:
        with pytest.raises(ValueError) as exc:
            ydl._parse_stream(fh, p)
    assert str(p) in str(exc.value)
