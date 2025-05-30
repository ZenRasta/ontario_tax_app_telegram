# retirement_planner_app

Project description here.

## Dependencies

The backend reads tax tables from YAML files. A real installation of
**PyYAML** is therefore required. Continuous integration checks that
`import yaml` succeeds, and `poetry install` will provide the package.

## Debug API

For troubleshooting, the backend exposes a debug route listing registered
withdrawal strategies:

```
GET /api/v1/debug/strategies
```

The endpoint returns a JSON array of strategy codes such as `"GM"`.

## Simulation Endpoint

The `/api/v1/simulate` route accepts a scenario along with the list of
strategy codes to evaluate:

```json
{
  "scenario": { "age": 65, "rrsp_balance": 500000, "goal": "maximize_spending" },
  "strategies": ["GM", "MIN"]
}
```

It returns an array of `ResultSummary` objects—one for each requested
strategy.
