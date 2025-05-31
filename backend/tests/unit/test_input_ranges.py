import copy
import pytest

from app.data_models.scenario import ScenarioInput

EXAMPLE = ScenarioInput.Config.json_schema_extra["example"].copy()

# Mapping of field -> (min_allowed, max_allowed or None)
FIELD_RANGES = {
    "age": (50, 100),
    "rrsp_balance": (100, None),
    "defined_benefit_pension": (0, None),
    "cpp_at_65": (0, 18000),
    "oas_at_65": (0, 8500),
    "tfsa_balance": (0, 200000),
    "desired_spending": (20000, 300000),
    "expect_return_pct": (0.5, 12),
    "stddev_return_pct": (0.5, 25),
    "life_expectancy_years": (5, 40),
}


def _make_base():
    return copy.deepcopy(EXAMPLE)


@pytest.mark.parametrize("field,minimum,maximum", FIELD_RANGES.items())
def test_field_below_and_above_range(field, minimum, maximum):
    data = _make_base()
    if isinstance(minimum, int):
        invalid_low = minimum - 1
    else:
        invalid_low = minimum - 0.1
    data[field] = invalid_low
    with pytest.raises(ValueError):
        ScenarioInput(**data)

    if maximum is not None:
        data = _make_base()
        if isinstance(maximum, int):
            invalid_high = maximum + 1
        else:
            invalid_high = maximum + 0.1
        data[field] = invalid_high
        with pytest.raises(ValueError):
            ScenarioInput(**data)


def test_bracket_fill_ceiling_out_of_range():
    data = _make_base()
    params = data.get("params", {}).copy()
    params["bracket_fill_ceiling"] = 29999
    data["params"] = params
    with pytest.raises(ValueError):
        ScenarioInput(**data)

    params = data.get("params", {}).copy()
    params["bracket_fill_ceiling"] = 250001
    data["params"] = params
    with pytest.raises(ValueError):
        ScenarioInput(**data)
