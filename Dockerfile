# Asset già compilati e inclusi nel repository: nessun Node.js a runtime.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --require-hashes -r requirements.txt \
    && useradd --create-home --uid 10001 aip
COPY --chown=aip:aip app ./app
COPY --chown=aip:aip migrations ./migrations
COPY --chown=aip:aip alembic.ini ./
USER aip
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --no-access-log"]
