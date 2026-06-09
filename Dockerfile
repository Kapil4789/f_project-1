FROM python:3.14-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl procps\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt



FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl procps\
    && rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos '' appuser

COPY --from=builder /usr/local  /usr/local


COPY . .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

ENV FLASK_ENV=development
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

#CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

#CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app", "--timeout=60", "--log-level=info", "--access-logfile=-", "--error-logfile=-"]

