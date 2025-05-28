# app/utils/year_data_loader.py
"""
Light-weight loader for tax-year / province tax constants.

• Uses PyYAML if available; otherwise falls back to json.loads()
  (so the .yaml file must use JSON-compatible syntax when PyYAML absent).

• Two supported layouts:
    1. Nested
        2025:
          ON: { federal_personal_amount: … }
          QC: { … }
    2. Flat  (assumed Ontario)
        2025:
          federal_personal_amount: …

Keeps an in-memory cache and rolls back to the closest earlier year.
"""

from __future__ import annotations

import datetime as _dt
import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # no PyYAML available → fallback parser
    yaml = None  # noqa: N816 (lower-case on purpose)

from app.services.strategy_engine.tax_rules import TaxYearData

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = REPO_ROOT / "backend" / "data" / "tax_years.yml"
YEAR_DIR = REPO_ROOT / "tax"

# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _looks_like_prov_code(s: str) -> bool:
    """True if `s` is exactly two uppercase letters (ON, QC, BC…)."""
    return isinstance(s, str) and len(s) == 2 and s.isalpha() and s.isupper()


def _normalise_year_block(block: dict) -> Dict[str, TaxYearData]:
    """
    Ensure each year maps to {province: TaxYearData}.
    – If *all* top-level keys look like province codes → already nested.
    – Otherwise wrap the whole block under "ON".
    """
    if block and all(_looks_like_prov_code(k) for k in block.keys()):
        return block  # nested structure as-is
    return {"ON": block}  # treat flat mapping as Ontario


def _parse_stream(fh) -> Dict[str, Any]:
    """
    Parse a file-handle:

    * If PyYAML is available and functional → use yaml.safe_load().
    * Otherwise fall back to json.loads()   (file must be JSON-compatible).

    Any AttributeError / NotImplementedError coming from a stub
    yaml.safe_load will trigger the JSON fallback automatically.
    """
    # -- First preference: real PyYAML ---------------------------------
    if yaml is not None:
        try:
            return yaml.safe_load(fh) or {}
        except (AttributeError, NotImplementedError):
            # stubbed yaml, continue to JSON fallback
            pass

    # -- Fallback: JSON ------------------------------------------------
    text = fh.read()
    try:
        return json.loads(text) or {}
    except json.JSONDecodeError as exc:  # neither YAML nor JSON worked
        raise ValueError(
            "Unable to parse tax tables: PyYAML missing / stubbed and "
            "file is not valid JSON.  Install `pyyaml` or convert the "
            "YAML file to JSON syntax."
        ) from exc


def _load_yaml() -> Dict[int, Dict[str, TaxYearData]]:
    """Parse tax_years.yml into {year:int → {prov:str → TaxYearData}}."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"tax_years.yml not found at {DATA_PATH}")

    with DATA_PATH.open(encoding="utf-8") as fh:
        raw: Dict[str, Any] = _parse_stream(fh)

    out: Dict[int, Dict[str, TaxYearData]] = {}
    for yr_str, block in raw.items():
        out[int(yr_str)] = _normalise_year_block(block)
    return out


def _load_single_year(year: int) -> Dict[str, TaxYearData] | None:
    """Load a year-specific file like tax/2025.yaml if present."""
    path = YEAR_DIR / f"{year}.yaml"
    if not path.exists():
        return None

    with path.open(encoding="utf-8") as fh:
        raw: Dict[str, Any] = _parse_stream(fh)

    if str(year) in raw:
        block = raw[str(year)]
    elif year in raw:
        block = raw[year]
    else:
        block = raw
    return _normalise_year_block(block)


@lru_cache(maxsize=1)
def _data_cache() -> Dict[int, Dict[str, TaxYearData]]:
    """YAML/JSON is parsed only once per interpreter run."""
    return _load_yaml()


# --------------------------------------------------------------------------- #
# public API
# --------------------------------------------------------------------------- #
def load_tax_year_data(year: int, province: str = "ON") -> TaxYearData:
    """
    Return tax constants for a given calendar `year` and `province`.

    Rolls back to the closest earlier year present in the tables.
    """
    year_block = _load_single_year(year)
    chosen_year = year

    if year_block is None:
        table = _data_cache()

        available_years = [y for y in table if y <= year]
        if not available_years:
            raise KeyError(f"No tax table available for years ≤ {year}")

        chosen_year = max(available_years)
        year_block = table[chosen_year]

    try:
        return year_block[province]
    except KeyError:  # province missing
        raise NotImplementedError(
            f"Province '{province}' not present for tax year {chosen_year}"
        ) from None


# --------------------------------------------------------------------------- #
# CLI smoke-test  →  python -m app.utils.year_data_loader
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    print(load_tax_year_data(_dt.datetime.now().year, "ON"))

