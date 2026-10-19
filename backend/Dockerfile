FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# opencv-python needs these two libraries, slim does not have them
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first so the slow install is cached until requirements change.
# The extra index gives the CPU-only torch wheel (no CUDA packages).
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

COPY app/ app/
COPY weights/ weights/

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# Python instead of curl, because slim has no curl. start-period gives the model time to load.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# One worker: each process holds its own model copy and its own lock.
# "*" trusts X-Forwarded-For from anyone. Only safe if just the proxy can reach this container.
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
