# Travel Planner API

A RESTful API for managing travel projects and artwork-based places to visit, built with **FastAPI**, **PostgreSQL** (async via `asyncpg`), and **SQLAlchemy**.

Artwork data is sourced from the [Art Institute of Chicago API](https://api.artic.edu/docs/).

Follows **Clean Architecture** — Domain, Application, Infrastructure, and Presentation layers with strict inward dependency rules.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI |
| Database | PostgreSQL (async, `asyncpg`) |
| ORM | SQLAlchemy 2 (async) |
| Migrations | Alembic |
| Dependency management | [uv](https://github.com/astral-sh/uv) |
| Validation | Pydantic v2, pydantic-settings |
| HTTP client | httpx |
| Logging | Loguru (`enqueue=True` — non-blocking) |
| Linting / formatting | Ruff |
| Type checking | ty |
| Testing | pytest, pytest-asyncio, pytest-cov |
| Pre-commit hooks | ruff, ty |
| Containerisation | Docker, Docker Compose |
| CI | GitHub Actions |

---

## Features

- Full CRUD for travel projects
- Add/update/list places within a project (validated against the Art Institute of Chicago API)
- Automatic project completion when all places are marked as visited
- Prevents deletion of projects that contain visited places
- Enforces a 1–10 places-per-project limit with duplicate detection
- Pagination and filtering on all list endpoints
- In-memory TTL caching for third-party API responses
- Optional HTTP Basic Authentication
- Async structured logging via Loguru
- Database migrations managed with Alembic
- OpenAPI docs at `/docs`
- Docker support with Docker Compose

---

## Quick Start

### Option 1 — Docker Compose (recommended)

```bash
cp .env.example .env
docker compose up --build
```

The API will be available at **http://localhost:8002**.

> The DB is exposed on host port `5433` and the API on `8002` to avoid conflicts with common local services.

---

### Option 2 — Local (Python 3.12+)

**Prerequisites:** Python 3.12+, [uv](https://github.com/astral-sh/uv), and a running PostgreSQL instance.

```bash
# 1. Install dependencies
uv sync

# 2. Copy and configure the environment file
cp .env.example .env
# Edit DATABASE_URL to point at your PostgreSQL instance

# 3. Apply database migrations
uv run alembic upgrade head

# 4. Start the server
uv run uvicorn app.presentation.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at **http://localhost:8000**.

---

## Environment Variables

Copy `.env.example` to `.env` and adjust as needed.

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_DB` | `travel_planner` | PostgreSQL database name (Docker Compose) |
| `POSTGRES_USER` | `postgres` | PostgreSQL user (Docker Compose) |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password (Docker Compose) |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/travel_planner` | SQLAlchemy async connection URL (local dev) |
| `DOCKER_DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@db:5432/travel_planner` | SQLAlchemy async URL used inside Docker Compose |
| `TEST_DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5433/travel_planner_test` | Connection URL for the integration test database |
| `ARTWORK_API_BASE_URL` | `https://api.artic.edu/api/v1` | Art Institute of Chicago API base URL |
| `ARTWORK_CACHE_TTL` | `3600` | Artwork response cache TTL in seconds |
| `ENABLE_AUTH` | `false` | Set `true` to require HTTP Basic Auth on all endpoints |
| `AUTH_USERNAME` | `admin` | Basic auth username |
| `AUTH_PASSWORD` | `admin` | Basic auth password |

---

## API Documentation

Interactive Swagger UI: **http://localhost:8002/docs**

ReDoc: **http://localhost:8002/redoc**

---

## Postman Collection

Import `postman_collection.json` from the root of this repository into Postman.

The collection includes:
- All project and place endpoints
- Happy-path requests pre-filled with real Art Institute artwork IDs
- Error-case requests (duplicate place, place limit exceeded, invalid artwork ID)
- A test script that automatically stores `project_id` and `place_id` variables after creation

**Useful artwork IDs for testing:**

| ID | Title | Artist |
|---|---|---|
| `27992` | A Sunday on La Grande Jatte — 1884 | Georges Seurat |
| `111628` | Nighthawks | Edward Hopper |
| `16487` | American Gothic | Grant Wood |
| `14586` | The Bedroom | Vincent van Gogh |
| `20684` | The Old Guitarist | Pablo Picasso |

---

## Endpoints Overview

### Projects

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/projects` | List projects (paginated, filterable by `is_completed`) |
| `POST` | `/api/v1/projects` | Create a project (optionally with initial places) |
| `GET` | `/api/v1/projects/{id}` | Get a project with its places |
| `PUT` | `/api/v1/projects/{id}` | Update project name / description / start_date |
| `DELETE` | `/api/v1/projects/{id}` | Delete a project (blocked if any place is visited) |

### Places

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/projects/{id}/places` | List places (paginated, filterable by `is_visited`) |
| `POST` | `/api/v1/projects/{id}/places` | Add a place (validated against Art Institute API) |
| `GET` | `/api/v1/projects/{id}/places/{pid}` | Get a single place |
| `PATCH` | `/api/v1/projects/{id}/places/{pid}` | Update `notes` and/or `is_visited` |

### Other

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |

---

## Example Requests

### Create a project with places

```bash
curl -X POST http://localhost:8002/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Chicago Art Tour",
    "description": "Must-see works at the Art Institute",
    "start_date": "2026-07-01",
    "places": [
      { "external_id": 27992 },
      { "external_id": 111628 }
    ]
  }'
```

### Add a place to an existing project

```bash
curl -X POST http://localhost:8002/api/v1/projects/1/places \
  -H "Content-Type: application/json" \
  -d '{ "external_id": 16487 }'
```

### Mark a place as visited and add a note

```bash
curl -X PATCH http://localhost:8002/api/v1/projects/1/places/1 \
  -H "Content-Type: application/json" \
  -d '{ "is_visited": true, "notes": "Stunning in person!" }'
```

### Enable Basic Auth

```bash
# In .env
ENABLE_AUTH=true
AUTH_USERNAME=traveller
AUTH_PASSWORD=secret123

# Pass credentials with every request
curl -u traveller:secret123 http://localhost:8002/api/v1/projects
```

---

## Testing

The project uses **pytest** with **pytest-asyncio** (`asyncio_mode = "auto"`) and **pytest-cov** for coverage. Integration tests run against a real PostgreSQL instance.

### Prerequisites for integration tests

A running PostgreSQL server accessible at the `TEST_DATABASE_URL` in your `.env`. The test suite automatically creates the `travel_planner_test` database and manages the schema.

### Run all tests

```bash
uv run pytest
```

### Run only unit tests

```bash
uv run pytest tests/unit -v
```

### Run only integration tests

```bash
uv run pytest tests/integration -v
```

### Run tests with coverage report

```bash
uv run pytest --cov=app --cov-report=term-missing
```

### Test structure

```
tests/
├── conftest.py                        # Shared helpers (make_project, make_place)
├── unit/
│   ├── conftest.py                    # Mocked repo / service fixtures
│   └── use_cases/
│       ├── projects/                  # Unit tests for all project use cases
│       └── places/                    # Unit tests for all place use cases
└── integration/
    ├── conftest.py                    # Real AsyncEngine, DB setup, FastAPI client
    ├── test_projects.py               # End-to-end project API tests
    └── test_places.py                 # End-to-end places API tests
```

---

## CI / CD

The project uses **GitHub Actions** (`.github/workflows/ci.yml`) with four jobs:

| Job | Depends on | What it does |
|---|---|---|
| `lint` | — | Runs `ruff format --check` and `ruff check` |
| `unit-tests` | `lint` | Runs `pytest tests/unit` — no database required |
| `integration-tests` | `lint` | Spins up a PostgreSQL service container and runs `pytest tests/integration` |
| `coverage` | `unit-tests` + `integration-tests` | Runs the full test suite, generates `coverage.xml`, publishes a markdown summary via `irongut/CodeCoverageSummary`, and **fails the build if total coverage drops below 80%** |

Coverage results are posted as a named GitHub Check on every commit and pull request.

---

## Pre-commit Hooks

```bash
# Install hooks (one-time)
uv run pre-commit install

# Run manually against all files
uv run pre-commit run --all-files
```

Hooks configured in `.pre-commit-config.yaml`:
- **ruff** — lint and auto-fix
- **ruff-format** — code formatting
- **ty** — static type checking

---

## Database Migrations

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Create a new migration after changing ORM models
uv run alembic revision --autogenerate -m "describe change"

# Roll back one step
uv run alembic downgrade -1
```

---

## Project Structure

```
├── app/
│   ├── domain/                        # Enterprise business rules
│   │   ├── entities/                  # Project, Place dataclasses
│   │   └── exceptions.py              # Domain-level exceptions
│   ├── application/                   # Application business rules
│   │   ├── ports/                     # Abstract repository & service interfaces
│   │   └── use_cases/
│   │       ├── common.py              # Shared PagedResult generic
│   │       ├── projects/              # create, get, list, update, delete
│   │       └── places/                # add, get, list, update
│   ├── infrastructure/                # Frameworks & drivers
│   │   ├── config.py                  # pydantic-settings configuration
│   │   ├── database.py                # Async SQLAlchemy engine & session
│   │   ├── logging.py                 # Loguru setup (enqueue=True)
│   │   ├── persistence/               # ORM models & repository implementations
│   │   └── external/                  # Art Institute API client (TTL cache)
│   └── presentation/                  # FastAPI delivery layer
│       ├── main.py                    # App factory, lifespan, request middleware
│       ├── dependencies.py            # DB session & auth FastAPI dependencies
│       ├── mappers.py                 # Domain → response schema mappers
│       └── api/v1/
│           ├── projects/              # Projects router & schemas
│           └── places/                # Places router & schemas
├── tests/
│   ├── conftest.py                    # Shared test helpers
│   ├── unit/                          # Isolated use-case tests (mocked deps)
│   └── integration/                   # Full-stack API tests (real PostgreSQL)
├── alembic/                           # Database migrations
│   └── versions/
│       └── 0001_initial_schema.py
├── .github/
│   └── workflows/
│       └── ci.yml                     # Lint → Unit → Integration → Coverage
├── main.py                            # Uvicorn entry point
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml                     # Dependencies & tool config (uv)
├── .pre-commit-config.yaml
├── .env.example
└── postman_collection.json
```
