# URL Shortener

![CI](https://github.com/ArnaldSouza/url-shortener/actions/workflows/ci.yml/badge.svg)

A URL shortener with asynchronous click analytics, built to explore
queue-based architecture. Click tracking and analytics run in the background
through a task queue, so recording a click never blocks the redirect response.

Built with FastAPI, PostgreSQL, Redis and Celery, fully containerized with
Docker Compose.

## Architecture

The core design goal is that recording a click must never slow down the
redirect. The redirect endpoint looks up the target URL, enqueues the click,
and responds immediately. A separate Celery worker consumes the queue and
writes analytics to PostgreSQL at its own pace.

```mermaid
flowchart LR
    Client([Client])
    API[FastAPI]
    Redis[(Redis<br/>broker + cache)]
    Worker[Celery Worker]
    DB[(PostgreSQL)]

    Client -->|GET /short_code| API
    API -->|307 redirect| Client
    API -.->|enqueue click| Redis
    Redis -.->|consume task| Worker
    Worker -->|insert event + bump counter| DB
    API -->|read / write| DB
```

The dotted path is asynchronous: the API returns the redirect without waiting
for the worker. If the worker is busy or down, the redirect is unaffected and
the task waits in Redis until it can be processed.

## Key design decisions

- **307 redirect, not 301.** A permanent redirect (301) is cached by browsers,
  which would bypass the API on repeat visits and lose click data. A temporary
  redirect (307) ensures every visit reaches the API, where the click is
  counted.

- **Asynchronous click counting.** The redirect enqueues the click and returns
  immediately instead of writing to the database inline. This keeps the
  redirect fast and resilient: a slow or unavailable worker never affects the
  response.

- **Atomic counter increment.** The click counter is updated with
  `UPDATE ... SET click_count = click_count + 1` in the database, not by reading
  the value into Python and writing it back. This avoids a lost-update race when
  concurrent clicks are processed.

- **Random short codes, not sequential IDs.** Codes are generated with the
  `secrets` module instead of being derived from the primary key. Sequential
  codes would be enumerable, letting anyone scan every link; random codes are
  not. The database unique constraint guards against the rare collision.

- **Cache-aside for the most-clicked link.** The most-clicked stats endpoint
  reads from Redis first and falls back to the database on a miss, caching the
  result with a short TTL. The TTL bounds staleness without any explicit
  invalidation logic.

- **Privacy by design in analytics.** Click events store only a coarse device
  category (`mobile`, `desktop`, `bot`, `unknown`) derived from the user agent.
  The raw user agent is inspected and discarded; no IP address or raw user
  agent is ever stored.

- **Fixed-window rate limiting.** Link creation is limited per IP using an
  atomic Redis `INCR` with a TTL. A fixed window can allow a brief burst at the
  window boundary; a sliding window would prevent this at the cost of more
  complexity (see Possible improvements).

- **No SSRF by design.** The API never fetches the submitted URL. It only
  validates and stores the string, so a malicious target URL cannot be used to
  make the server issue requests.

## Tech stack

- **FastAPI** - web framework and request validation
- **PostgreSQL** - persistent storage for links and click events
- **Redis** - Celery broker, response cache, and rate-limit counter
- **Celery** - asynchronous task queue for click processing
- **SQLAlchemy 2.0** - ORM and query layer
- **Alembic** - database migrations
- **Docker Compose** - local orchestration of all services
- **pytest** - test suite
- **uv** - dependency management
- **ruff** - linting

## Getting started

### Prerequisites

- Docker and Docker Compose

### Run with Docker Compose

Start all services (API, Celery worker, PostgreSQL, Redis):

```bash
docker compose up -d --build
```

Apply the database migrations (the schema is managed by Alembic, so this step
creates the tables on a fresh database):

```bash
docker compose exec api alembic upgrade head
```

The API is now available at `http://localhost:8000`. Interactive API docs
(Swagger UI) are at `http://localhost:8000/docs`.

### Local development

Dependencies are managed with [uv](https://docs.astral.sh/uv/). To run the
app outside Docker, start only the backing services and run the API and worker
locally:

```bash
docker compose up -d db redis
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
uv run celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

The `--pool=solo` flag is required for the Celery worker on Windows.

## API endpoints

| Method | Path                  | Description                                      |
|--------|-----------------------|--------------------------------------------------|
| POST   | `/links`              | Create a short link. Rate limited per IP.        |
| GET    | `/{short_code}`       | Redirect to the target URL and record the click. |
| GET    | `/stats/most-clicked` | Return the most-clicked link (cached).           |
| GET    | `/health`             | Liveness check.                                  |

### Example

```bash
# Create a short link
curl -X POST http://localhost:8000/links \
  -H "Content-Type: application/json" \
  -d '{"target_url": "https://example.com"}'

# Response: {"short_code": "Ab3xK9z", "target_url": "...", "click_count": 0, ...}

# Follow the short link (records a click asynchronously)
curl -i http://localhost:8000/Ab3xK9z
```
