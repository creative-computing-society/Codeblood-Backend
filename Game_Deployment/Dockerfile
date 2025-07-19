# Stage 1: Builder stage
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


RUN pip install uv


COPY requirements.txt .
RUN uv pip install -r requirements.txt --system


RUN pip install uvicorn

# Stage 2: Production stage
FROM python:3.13-slim

WORKDIR /app


COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn


COPY . .


ENV PATH="/usr/local/bin:$PATH"

EXPOSE 2130

ENV IS_DEV=False
ENV SECURE_LOGIN=True

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "2130"]

#NOTE: 127.0.0.1 will work with the OAuth. 