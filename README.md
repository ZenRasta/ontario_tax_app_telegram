# Ontario TaxApp v2

This repository contains two main components:

- **backend/** – a FastAPI application managed with [Poetry](https://python-poetry.org/).
- **frontend/** – a React application using Vite and TypeScript.

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

