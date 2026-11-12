# 1. Base Image: Lightweight official Python runtime
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. Set working directory inside container
WORKDIR /app

# 3. Layer Caching Rule: Copy dependencies first and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy application source code, catalog, and frontend assets
COPY app/ ./app/
COPY data/ ./data/
COPY static/ ./static/

# 5. Security Best Practice: Run as a non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# 6. Expose application network port
EXPOSE 8000

# 7. Start FastAPI production server with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
