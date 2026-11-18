# ---- base: Python + libraries (cached, so rebuilds are fast) ----
FROM python:3.11-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pytest httpx

# ---- app: code + freshly trained model, served by FastAPI ----
FROM base AS app
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
