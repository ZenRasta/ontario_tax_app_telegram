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
Strategy" buttons link to the calculator at the `/calculator` route.

## Tax data

The consolidated tax tables live in `backend/data/tax_years.yml`.  Additional
per‑year files are stored under the top‑level `tax/` directory.  These YAML files
are parsed at runtime by the backend via PyYAML.

## Environment variables

Set the following variables in your deployment environment or in a `.env` file.  Hosting platforms such as Vercel, Render or Heroku expose dashboards for managing these values.

| Variable | Purpose |
| -------- | ------- |
| `OPENROUTER_API_KEY` | API key for optional LLM explanations. |
| `OPENROUTER_MODEL` | (Optional) OpenRouter model. Defaults to `openai/o4-mini`. |
| `TELEGRAM_BOT_TOKEN` | Token for the Telegram bot. |
| `WEBHOOK_URL` | Public URL for webhook mode. Leave unset when using polling. |
| `ALLOWED_CORS_ORIGINS` | Comma‑separated list of origins allowed by the backend. |
| `VITE_API_PREFIX` | Frontend build‑time URL to the backend API (e.g. `https://your-backend.example.com/v1`). |

The backend automatically loads environment variables from a `.env` file in the `backend/` directory.  The frontend uses variables prefixed with `VITE_` during its build step.

## Deployment

### Frontend (Vercel)

1. Create a new Vercel project and set the **root directory** to `frontend`.
2. Use `npm run build` as the build command and `dist` as the output directory.
3. Define the `VITE_API_PREFIX` environment variable pointing to your deployed backend URL.
4. Deploy and note the resulting public URL.
5. In Telegram's BotFather, configure the mini app **App URL** to the Vercel deployment URL.

### Backend and Bot (Render/Heroku)

1. Create a new web service from this repository.  The provided `Procfile` starts the FastAPI app with Gunicorn.
2. Configure environment variables such as `TELEGRAM_BOT_TOKEN`, `OPENROUTER_API_KEY`, and `ALLOWED_CORS_ORIGINS`.
3. For **webhook** operation:
   - Set `WEBHOOK_URL` to your public backend URL.
   - Register the webhook with Telegram using `https://api.telegram.org/bot<token>/setWebhook?url=<WEBHOOK_URL>`.
4. For **polling** operation:
   - Add a worker process that runs the polling script in the `bot/` directory.
5. After deployment, verify the API with `curl https://<backend-url>/health` and ensure your frontend origin is included in `ALLOWED_CORS_ORIGINS` for CORS.

## Telegram bot

The project includes a simple Telegram bot that echoes tax strategy summaries
using the existing LLM service. Configure your bot token in the `.env` file:

```
TELEGRAM_BOT_TOKEN=your-telegram-token
```

Keep real tokens out of version control. After installing backend dependencies
with Poetry, start the bot from the repository root:

```
poetry run python bot/main.py
```

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
