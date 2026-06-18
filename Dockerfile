FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY requirements.txt ./ 2>/dev/null || true

RUN pip install --no-cache-dir -e ".[api,nlp]" 2>/dev/null || \
    pip install --no-cache-dir numpy scipy pydantic cryptography fastapi uvicorn

COPY hsrai/ ./hsrai/
COPY urcm/ ./urcm/
COPY isre/ ./isre/

RUN pip install --no-cache-dir -e ".[api]"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "-m", "uvicorn", "hsrai.api.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
