# Ontario Tax App

This repository provides a small demo retirement planning application.  The
backend is written with **FastAPI** and the frontend uses **React** with Vite.
It simulates RRSP/RRIF withdrawal strategies for Ontario residents.

## Installation

Clone the repository and install the backend and frontend dependencies.

### Backend

```bash
cd backend
poetry install
```

A real installation of **PyYAML** is required because the backend reads its tax
tables from YAML files.  `poetry install` will install PyYAML for you.

### Frontend

```bash
cd frontend
npm ci
```

### Landing page

The landing page is now the default entry at `frontend/index.html`.  Open this
file in a browser to preview the marketing design.  The "Figure out my RRIF
Strategy" buttons link to the calculator located at
`frontend/calculator.html`.

## Tax data

The consolidated tax tables live in `backend/data/tax_years.yml`.  Additional
per‑year files are stored under the top‑level `tax/` directory.  These YAML files
are parsed at runtime by the backend via PyYAML.

## Running tests

### Backend

```bash
cd backend
poetry run pytest
```

### Frontend

```bash
cd frontend
npm test
```

