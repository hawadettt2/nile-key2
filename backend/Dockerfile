FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app

ENV PYTHONUNBUFFERED=1

USER root

EXPOSE 8000

# The db-data volume mounts as root:root, which makes it read-only for the
# non-root appuser and triggers "sqlite3.OperationalError: attempt to write a
# readonly database". Fix: take ownership of /app/data at runtime (as root),
# then drop privileges to the non-root appuser before starting uvicorn.
CMD ["sh", "-c", "chown -R appuser:appuser /app/data 2>/dev/null; exec setpriv --reuid=appuser --regid=appuser --clear-groups uvicorn main:app --host 0.0.0.0 --port 8000"]
