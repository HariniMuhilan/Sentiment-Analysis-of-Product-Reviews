#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r backend/requirements.txt
.venv/bin/python -m nltk.downloader vader_lexicon
npm ci --prefix sentiment-dashboard

(
  cd backend
  ../.venv/bin/python seed_demo_data.py \
    --file ../Datasets/VirtualAssistantDevices/processed/virtual_assistant_reviews.csv
)
