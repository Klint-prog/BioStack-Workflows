FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    BIOSTACK_WORKSPACE=/workspace

WORKDIR /app

RUN addgroup --system biostack \
    && adduser --system --ingroup biostack --uid 10001 biostack

COPY pyproject.toml README.md ./
COPY biostack ./biostack
COPY workflows ./workflows
COPY tests ./tests

RUN python -m pip install --upgrade pip \
    && python -m pip install -e ".[web,dev]" \
    && mkdir -p /workspace \
    && chown -R biostack:biostack /app /workspace

COPY docker/entrypoint.sh /usr/local/bin/biostack-entrypoint.sh
RUN chmod +x /usr/local/bin/biostack-entrypoint.sh

USER biostack
WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/biostack-entrypoint.sh"]
CMD ["biostack", "--help"]
