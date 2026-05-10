# ── STAGE 1: Build Frontend ──────────────────────────────────────────────────
FROM node:18-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN VITE_API_BASE_URL="" npm run build

# ── STAGE 2: Build Backend ───────────────────────────────────────────────────
FROM python:3.11-slim

# Create a non-root user with a home directory
RUN groupadd -r appuser && useradd -r -g appuser -m appuser

WORKDIR /app

# Install system deps for PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Copy built frontend from Stage 1
COPY --from=frontend-builder /frontend/dist ./dist

# Fix permissions
RUN chown -R appuser:appuser /app /home/appuser
USER appuser

EXPOSE 8000

# Start command
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", \
     "main:app", "--bind", "0.0.0.0:8000", "--timeout", "120", "--worker-tmp-dir", "/dev/shm"]
