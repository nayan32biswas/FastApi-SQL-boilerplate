# FastAPI and SQL boilerplate Backend

## Start Project

- Make sure python version 3.11 or above.
- Install poetry.
- Install postgres.
- Make a copy of **example.env** and rename to **.env**
- Change `DB_URL` in **.env** according to your database connection.

Finally run below commands to start the project.

```bash
poetry shell
poetry install
alembic revision --autogenerate -m "Init"
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Start project with docker

- Make a copy of **example.env** and rename to **.env**
- Change `DB_URL` in **.env** according to your database connection.

Run below commands to start the project with docker.

```bash
docker-compose build
docker-compose run server alembic revision --autogenerate -m "Init"
docker-compose run server alembic upgrade head
docker-compose up server
```

## Development

For the development run bellow command to enable the pre-commit hook for the first time.

```bash
pre-commit install && pre-commit run --all-files
```
