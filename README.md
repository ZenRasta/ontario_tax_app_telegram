# Ontario TaxApp v2

This repository contains two main components:

- **backend/** – a FastAPI application managed with [Poetry](https://python-poetry.org/).
- **frontend/** – a React application using Vite and TypeScript.

## Setup

### Backend
```bash
cd backend
poetry install
```

### Frontend
```bash
cd frontend
npm install
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

## 2025 Tax Assumptions

Tax calculations rely on indexed figures for the 2025 calendar year. Key
constants include the basic personal amounts, Ontario surtax brackets and the
Old Age Security (OAS) clawback threshold of `$93\,454`.

## Strategy-Specific Inputs

Each withdrawal method exposes optional parameters. Omitting them triggers
default behaviours. Notable examples:

- **Bracket Filling** – ceiling defaults to the OAS clawback threshold when not
  provided.
- **CPP/OAS Delay** – missing start ages are set to 70.
- **Interest Offset** – interest rate and loan percent default to 5 % and
  20 %, respectively.

