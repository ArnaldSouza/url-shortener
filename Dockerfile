FROM python:3.12-slim

# Install uv (copied from the official uv image)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create a non-root user to run the app
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app

# Put the project virtualenv on PATH so we can call tools directly,
# and tell uv not to try to manage the environment at runtime.
ENV PATH="/app/.venv/bin:$PATH" \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Install dependencies first, leveraging Docker layer caching.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy the application code and install the project itself.
COPY app ./app
RUN uv sync --frozen --no-dev

# Hand ownership of the app (including .venv) to the non-root user.
RUN chown -R appuser:appuser /app
USER appuser

# Run the API directly from the venv (no uv run, no runtime re-sync).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
