# Samadhan Setu — API

FastAPI backend. See the top-level `README.md` for the full setup walkthrough.

Quick reference:
- Entry point: `app/main.py` (`create_app()`)
- Routers: `app/routers/*.py`, all mounted under `/api/v1`
- AI engine: `app/ai/` — trains automatically on first boot from `app/ai/data/train_challenges.json`
- Migrations: `alembic upgrade head` (from this `api/` directory)
- Seed data: `python ../scripts/seed.py` (from this directory) or `python scripts/seed.py` (from repo root)
- Tests: `pytest -q`
- Docs: once running, visit `http://localhost:8000/docs`
