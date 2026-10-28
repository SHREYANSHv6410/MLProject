FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies directly (no apt-get overhead needed)
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source code and artifacts
COPY backend/ backend/
COPY scripts/ scripts/
COPY data/ data/
COPY artifacts/ artifacts/

ENV PYTHONPATH=/app
ENV PORT=8000
ENV HOST=0.0.0.0
ENV ENVIRONMENT=production

EXPOSE 8000

# Zero-dependency health check using Python standard library urllib
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
