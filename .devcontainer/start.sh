#!/usr/bin/env bash
set -euo pipefail

if ! curl --silent --fail http://127.0.0.1:8000/api/health >/dev/null; then
  (
    cd backend
    nohup ../.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload \
      > /tmp/sentiment-analysis-backend.log 2>&1 < /dev/null &
  )
fi

if ! curl --silent --fail http://127.0.0.1:5173/ >/dev/null; then
  (
    cd sentiment-dashboard
    nohup npm run dev -- --host 0.0.0.0 --port 5173 \
      > /tmp/sentiment-analysis-frontend.log 2>&1 < /dev/null &
  )
fi

for attempt in $(seq 1 30); do
  if curl --silent --fail http://127.0.0.1:8000/api/health >/dev/null \
    && curl --silent --fail http://127.0.0.1:5173/ >/dev/null; then
    echo "Dashboard running at port 5173; backend health check passed on port 8000."
    exit 0
  fi
  sleep 1
done

echo "The app did not start. Check /tmp/sentiment-analysis-backend.log and /tmp/sentiment-analysis-frontend.log."
exit 1
