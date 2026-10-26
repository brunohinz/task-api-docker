# task-api-docker

A small REST API for tracking tasks or payment agreements. It is built with **FastAPI**, **SQLAlchemy 2** and **SQLite**, has tests, and is packaged with **Docker / docker-compose**.

## Features

- CRUD on `/tasks`: create, list, get, partial update (PATCH) and delete.
- Fields: `title`, `description`, `amount` (decimal, ≥ 0), `due_date`, and `status` (`open` | `done` | `cancelled`).
- Validation with Pydantic: invalid input returns `422` with details, and a missing task returns `404`.
- List filters: `status`, `overdue=true` (open tasks past their due date), `q` (title search), and `limit`/`offset` pagination.
- Interactive docs at `/docs` (Swagger UI), generated automatically by FastAPI.
- Tests use an isolated in-memory database.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at http://localhost:8000 and the docs at http://localhost:8000/docs.

## Run with Docker

```bash
docker compose up --build
```

Data is kept in the `task-data` volume (`/data/tasks.db`).

## curl examples

```bash
# create
curl -X POST localhost:8000/tasks -H 'Content-Type: application/json' \
  -d '{"title":"Send contract","amount":"1200.00","due_date":"2026-11-15"}'
# {"title":"Send contract","description":null,"amount":"1200.00","due_date":"2026-11-15","status":"open","id":1,"created_at":"..."}

# list (with filters)
curl localhost:8000/tasks
curl "localhost:8000/tasks?status=open&overdue=true"
curl "localhost:8000/tasks?q=contract&limit=10"

# get one
curl localhost:8000/tasks/1

# update
curl -X PATCH localhost:8000/tasks/1 -H 'Content-Type: application/json' -d '{"status":"done"}'

# delete (204 No Content)
curl -X DELETE localhost:8000/tasks/1

# validation error (422)
curl -X POST localhost:8000/tasks -H 'Content-Type: application/json' -d '{"title":"","amount":-5}'
```

## Tests

```bash
pytest -v
```

## Configuration

| Variable | Default |
|---|---|
| `DATABASE_URL` | `sqlite:///./tasks.db` |

## Project structure

```text
app/main.py       routes
app/models.py     SQLAlchemy model
app/schemas.py    Pydantic schemas and validation
app/database.py   engine and session
tests/            pytest tests
```

## Limitations and roadmap

- There is no authentication yet. The plan is to add API keys or JWT.
- Tables are created on startup. The plan is to add Alembic migrations.
- SQLite only for now. PostgreSQL would need only a different `DATABASE_URL` and a driver.

## License

MIT © Bruno Hinz Cristiani
