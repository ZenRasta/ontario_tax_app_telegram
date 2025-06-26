# Multi-stage build for both frontend and backend
FROM node:18-slim as frontend-builder

# Build frontend
WORKDIR /app
COPY package*.json ./
COPY frontend/package*.json ./frontend/
RUN npm install
COPY frontend/ ./frontend/
RUN npm run --workspace frontend build

# Python backend stage
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for the server
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

WORKDIR /app

# Copy and install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY tax/ ./tax/

# Copy frontend build and server files
COPY --from=frontend-builder /app/dist ./dist
COPY package*.json ./
COPY server/ ./server/
RUN npm install --production

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose the port
EXPOSE 8080

# Start script that runs both frontend server and backend
CMD ["sh", "-c", "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 & npm start"]
