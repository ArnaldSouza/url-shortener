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
