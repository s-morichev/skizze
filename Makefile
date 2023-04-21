format:
	poetry run black app
	poetry run isort app

lint:
	poetry run black --check app
	poetry run isort --check-only app
	poetry run mypy app
	poetry run flake8 app

dev-run:
	docker compose up -d --build

dev-stop:
	docker compose down -v

restart:
	docker compose down
	docker compose up -d --build

run-test-db:
	docker run --env POSTGRES_USER=user --env POSTGRES_PASSWORD=password --env POSTGRES_DB=test_database \
    	--name skizze_test_backend_postgres -p 45432:5432 -d postgres:15.1-alpine

test:
	coverage run -m pytest -s ./app/tests
	coverage html

stop-test-db:
	docker rm --force skizze_test_backend_postgres
