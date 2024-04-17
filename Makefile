migrate:
	docker-compose run server alembic upgrade head

docker_build:
	docker-compose build

docker_up_server:
	docker-compose up server

docker_exec:
	docker-compose exec server bash

test:
	docker-compose run --rm server ./scripts/test.sh

format:
	docker-compose run --rm server ./scripts/format.sh

lint:
	docker-compose run --rm server ./scripts/lint.sh
