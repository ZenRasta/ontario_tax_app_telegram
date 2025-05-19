# Ontario TaxApp v2

This repository contains two main components:

- **backend/** – a FastAPI application managed with [Poetry](https://python-poetry.org/). Requires Python 3.9 or newer (see `pyproject.toml` for the exact version range).
- **frontend/** – a React application using Vite and TypeScript.

## Requirements

- Python 3.9+
 - Node.js 18.18+ or 20.9+

## Setup

### Backend
Requires **Python 3.10** or later.
```bash
cd backend
poetry install
```

### Frontend
```bash
cd frontend
npm install
# New dependencies were added:
#   classnames
#   @floating-ui/dom
# Run `npm install` again if you installed packages before this change.
# If you encounter peer dependency errors for `@types/react-dom`,
# ensure the dev dependency is pinned to a React 18 compatible version:
#
#   npm install --save-dev @types/react-dom@18.0.11
# If npm prints "Unsupported engine" warnings, upgrade Node to
# a compatible version (Node.js 18.18+ or 20.9+).
```

## Running in Development

### API Server
Run the FastAPI server from the `backend` directory:
```bash
poetry run uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.

### React Dev Server
Start the React development server from the `frontend` directory:
```bash
npm run dev
```
The app will be served by Vite (typically on `http://localhost:5173`).

## Usage Examples

Check that the API is running:
```bash
curl http://localhost:8000/api/v1/health
```

Run a basic simulation:
```bash
curl -X POST http://localhost:8000/api/v1/simulate \
  -H 'Content-Type: application/json' \
  -d '{
    "strategy_code": "GM",
    "scenario": {
      "age": 65,
      "rrsp_balance": 500000,
      "defined_benefit_pension": 20000,
      "cpp_at_65": 12000,
      "oas_at_65": 8000,
      "tfsa_balance": 100000,
      "desired_spending": 60000,
      "expect_return_pct": 5,
      "stddev_return_pct": 8,
      "life_expectancy_years": 25,
      "province": "ON",
      "goal": "maximize_spending"
    }
  }'
```

### Linting & Tests

Backend linting and tests:
```bash
cd backend
poetry run ruff check .
poetry run pytest
```

Frontend linting and tests:
```bash
cd frontend
npm run lint
npm test # if tests are present
```
