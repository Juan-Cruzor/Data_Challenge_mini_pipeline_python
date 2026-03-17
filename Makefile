build:
	docker compose build

up:
	docker compose up

down:
	docker compose down -v

logs:
	docker compose logs -f

tests:
	docker compose run app pytest -q

api:
	curl "http://localhost:8000/daily_stats?date=2025-01-15"

psql:
	docker exec -it $$(docker ps -qf name=postgres) psql -U postgres -d events