# Stage 1: Build the application with Poetry
FROM python:3.9-slim as builder

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy only files necessary for dependency installation
COPY pyproject.toml poetry.lock* ./

# Install dependencies
# --no-root: don't install the project itself yet
# --no-dev: don't install dev dependencies
RUN poetry config virtualenvs.create false && poetry install --no-root --no-dev --no-interaction --no-ansi

# Stage 2: Create the runtime image
FROM python:3.9-slim

WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY ./app /app/app
COPY ./data /app/data

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# Adjust if your main.py is elsewhere or app instance is named differently
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
