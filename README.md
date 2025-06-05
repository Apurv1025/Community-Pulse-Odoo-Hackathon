# Community-Pulse-Odoo-Hackathon

# TEAM 319

## video links
- part 1 : https://drive.google.com/file/d/1P8l_dHX7Fxzzc0VVUQYe9EA2HCxnHmcP/view?usp=sharing
- part 2 : https://drive.google.com/file/d/1nTNG6rGRsGKkhpkVZxlSukN1-7VgaFc4/view?usp=sharing

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

# make a worker server
- create a venv

`cd /Users/apurv/Community-Pulse-Odoo-Hackathon`
`celery -A backend.celery_app worker --loglevel=info`

# make beats server

- create a venv

`celery -A backend.email_tasks beat --loglevel=info`   

## run redis if not already running

`redis-serve`

[text](https://drive.google.com/file/d/1qU1RMRF95TMKK4i_X07s159ZEvhBjMCe/view?usp=sharing)