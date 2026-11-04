# URL Shortener

![CI](https://github.com/ArnaldSouza/url-shortener/actions/workflows/ci.yml/badge.svg)

A URL shortener with asynchronous click analytics, built to explore
queue-based architecture. Click tracking and analytics run in the background
through a task queue, so recording a click never blocks the redirect response.

Built with FastAPI, PostgreSQL, Redis and Celery, fully containerized with
Docker Compose.
