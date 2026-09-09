#!/usr/bin/env bash
# Starts the API and web dev servers together. Run from the repo root.
set -e

( cd api && uvicorn app.main:app --reload --port 8000 ) &
API_PID=$!

( cd web && npm run dev ) &
WEB_PID=$!

trap "kill $API_PID $WEB_PID" EXIT
wait
