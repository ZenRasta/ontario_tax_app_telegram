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

## Environment variables

The backend reads optional settings from a `.env` file in the `backend` directory. To enable the explanation features, provide an OpenRouter API key and model name, for example:

```
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_MODEL=openai/o4-mini
```

`OPENROUTER_MODEL` defaults to `openai/o4-mini` if left unset.

## Strategy report

After running a simulation, the results screen includes a **View Report**
button.  This opens a printable summary with any explanation text provided by
the LLM service.  Use the **Export PDF** button to trigger the browser's print
dialog and save the report as a PDF file.

The PDF feature relies on the `react-to-print` package which is installed when
you run `npm ci` in the `frontend` directory.  Generating the explanation text
requires the `OPENROUTER_API_KEY` environment variable described above.

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

