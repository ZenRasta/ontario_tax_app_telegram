# retirement_planner_app

Project description here.

## Dependencies

The backend reads tax tables from YAML files. A real installation of
**PyYAML** is therefore required. Continuous integration checks that
`import yaml` succeeds, and `poetry install` will provide the package.

## Environment variables

Create a `.env` file in this directory with your OpenRouter configuration:

```
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_MODEL=openai/o4-mini
```

`OPENROUTER_MODEL` defaults to `openai/o4-mini` if omitted.


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
