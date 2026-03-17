# Events Data Pipeline

A streaming data pipeline that ingests user events from a JSON file, validates
and normalizes them with **Pydantic**, computes daily metrics, stores results in
**PostgreSQL**, and exposes them via a **FastAPI** REST endpoint.

It started as something simple and eventually more feautres were addded to make it more complex and scalable.

Supports **incremental processing** via a watermark. Each run only processes
events newer than the previous successful run.

## Project Structure
.
├── app/
│   ├── __init__.py
│   ├── aggregate.py        # In-memory metrics accumulation
│   ├── data_warehouse.py   # PostgreSQL upsert logic
│   ├── db.py               # DB connection factory
│   ├── idempotency.py      # Per-event duplicate detection
│   ├── logger.py           # Structured file logger
│   ├── main.py             # FastAPI app & endpoints
│   ├── models.py           # Pydantic validation & normalization models
│   ├── pipeline.py         # Main orchestrator
│   ├── stream.py           # Lazy JSON / NDJSON reader with watermark filter
│   ├── validation.py       # Pydantic validation entry point
│   ├── watermark.py        # High-water mark read/write
│   ├── write_csv.py        # CSV output writer
│   └── write_parquet.py    # Date-partitioned Parquet writer
├── scripts/
│   └── init.sql            # PostgreSQL schema (auto-run on first DB start)
├── tests/
│   └── test_pipeline.py    # Full unit test suite (no live DB needed)
├── data/
│   └── events.json         # Input events file
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
└── Make file               #Unfinished

## Stack
- Python
- FastAPI
- PostgreSQL
- Docker
- Pytest

## How to Run - install 

### Docker Compose

Starts PostgreSQL, creates the schema, runs the pipeline and serves the API.

## Place your events file at:
cp /path/to/your/events.json data/events.json

## Start everything
docker compose up --build

The API will be available at **http://localhost:8000**.


## Stop (keep DB data)
docker compose down

## Stop and delete DB volume
docker compose down -v

## Design decisions

- Used functional programming except for the pydantic model that defined a more automatic way to validate and normalize
- Used a watermark. Idempotency check does a SELECT against PostgreSQL for every single event. At scale that's expensive.
- Incremental ingestion via event hashing
- FastAPI used for simple REST API along with Pydantic to have a more automatic way of       define the validation and normalization.
- Docker to have an easier way to reproduce and try the pipeline.
- Used a generator to yield the json objects in the input file, that way it is more memory efficent and evventually handle larger files.


## Things I would have done with more time.

-I would separate them to make them a **microservice** architecture
-I would implement Kafka or **clickhouse** into the pipeline.
-I would try to simulate a streaming mode.
-I would add **observability** metrics.
- I would implement a manager class. Instead of passing conn and cursor everywhere manually, a context manager class would handle open/close/rollback automatically and remove the try/finally boilerplate from pipeline.py
-I would add a Date-range endpoint to query metrics across multiple days in one call
- **GitHub Actions CI** — run `pytest` on every push
- **Structured JSON logging** — easier to ingest into a log aggregator

