
# Data pipeline
Mini data pipeline that processes user events, generates metrics and gets them with an API.

## Stack

- Python
- FastAPI
- PostgreSQL
- Docker
- Pytest

## Run project

Start services:

docker-compose up --build

## Process events

python -m app.pipeline data/events.json

## Endpoint

GET /daily_stats?date=2025-01-15

Example:

http://localhost:8000/daily_stats?date=2025-01-15

## Tests

pytest

## Design decisions

- PostgreSQL used for analytics storage
- Incremental ingestion via event hashing
- FastAPI used for simple REST API
- Docker ensures reproducible environment
