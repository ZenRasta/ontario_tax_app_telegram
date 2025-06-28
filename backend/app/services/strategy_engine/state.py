# app/services/strategy_engine/state.py
"""
Holds per‑run mutable state for the deterministic engine.

• `YearScratch` – raw numbers for one calendar year
• `EngineState` – balances + list[YearScratch]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:  # avoid circular import at runtime
    from ...data_models.scenario import ScenarioInput


# ------------------------------------------------------------------ #
# Scratch row – accumulates numbers before we convert to YearlyResult
# ------------------------------------------------------------------ #
@dataclass
class YearScratch:
    year: int
    age: int
    spouse_age: Optional[int]

    begin_rrif: Decimal
    begin_tfsa: Decimal
    begin_non_reg: Decimal

    gross_rrif: Decimal
    cpp: Decimal
    oas_gross: Decimal
    db_pension: Decimal
    other_taxable_income: Decimal

    taxable_income: Decimal
    fed_tax: float
    prov_tax: float
    oas_claw: float
    total_tax: float
    after_tax_income: Decimal
    oas_net: Decimal
    spending: Decimal

    end_rrif: Decimal
    end_tfsa: Decimal
    end_non_reg: Decimal


# ------------------------------------------------------------------ #
# Engine‑scope state object
# ------------------------------------------------------------------ #
@dataclass
class EngineState:
    """
    •  `balances` always represent **start** of the year being processed.
    •  Each strategy must:
         1. read  self.balances
         2. compute everything for that calendar year
         3. call  self.record(row)  → pushes YearScratch + rolls balances
    """
    scenario: "ScenarioInput"
    start_year: int
    balances: Dict[str, Decimal] = field(default_factory=dict)
    rows: List[YearScratch] = field(default_factory=list)

    # -------------------------------------------------------------- #
    def record(self, row: YearScratch) -> None:
        """Append a scratch row and roll balances forward."""
        self.rows.append(row)
        self.balances = {
            "rrif": row.end_rrif,
            "tfsa": row.end_tfsa,
            "non_reg": row.end_non_reg,
        }

    # -------------------------------------------------------------- #
    @classmethod
    def initial(cls, scenario: "ScenarioInput", start_year: int) -> "EngineState":
        return cls(
            scenario=scenario,
            start_year=start_year,
            balances={
                "rrif": Decimal(str(scenario.rrsp_balance)),
                "tfsa": Decimal(str(scenario.tfsa_balance)),
                "non_reg": Decimal("0"),
            },
        )
