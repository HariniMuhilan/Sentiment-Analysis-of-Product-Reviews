FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for build tools and curl health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download VADER lexicon into standard NLTK path (required for sentiment analysis)
RUN python -c "import nltk; nltk.download('vader_lexicon')" || \
    echo "VADER lexicon may be missing but will continue without download error"

COPY . .

# Add sqlite3 support for SQLite database persistence
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
