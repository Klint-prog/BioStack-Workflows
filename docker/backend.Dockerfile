FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    BIOSTACK_WORKSPACE=/workspace

WORKDIR /app

COPY pyproject.toml README.md ./
COPY biostack ./biostack
COPY workflows ./workflows
COPY tests ./tests

RUN python -m pip install --upgrade pip \
    && python -m pip install -e ".[web,dev]"

COPY docker/entrypoint.sh /usr/local/bin/biostack-entrypoint.sh
RUN chmod +x /usr/local/bin/biostack-entrypoint.sh \
    && mkdir -p /workspace

WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/biostack-entrypoint.sh"]
CMD ["biostack", "--help"]
