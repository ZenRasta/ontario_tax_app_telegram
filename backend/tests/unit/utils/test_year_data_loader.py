import importlib
import subprocess
import sys
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


def test_load_tax_year_data_installed(tmp_path):
    root = Path(__file__).resolve().parents[4]
    backend = root / "backend"
    subprocess.run(["poetry", "build", "-f", "wheel"], cwd=backend, check=True)
    wheel = next((backend / "dist").glob("*.whl"))

    install_dir = tmp_path / "site"
    subprocess.run([
        sys.executable,
        "-m",
        "pip",
        "install",
        str(wheel),
        "--target",
        str(install_dir),
    ], check=True)

    code = (
        "import app.utils.year_data_loader as ydl;"
        "print(ydl.load_tax_year_data(2025)['federal_personal_amount'])"
    )
    out = subprocess.check_output([sys.executable, "-c", code], env={"PYTHONPATH": str(install_dir)})
    assert out.strip() == b"15705"
