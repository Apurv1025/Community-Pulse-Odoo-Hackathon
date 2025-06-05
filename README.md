# Community-Pulse-Odoo-Hackathon

## Setup

### Frontend

`cd frontend`

`bun install`

`bun run dev`

### Backend

`cd backend`

`python -m venv .venv`

`source .venv/bin/activate`

`pip install -r requirements.txt`

`fastapi dev main.py`

## in a new terminal for celery

`celery -A backend.email_tasks worker --loglevel=info`

## run redis if not already running

`redis-serve`

[text](https://drive.google.com/file/d/1qU1RMRF95TMKK4i_X07s159ZEvhBjMCe/view?usp=sharing)