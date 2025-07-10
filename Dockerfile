# Stage 1: Builder stage
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \  
    PIP_NO_CACHE_DIR=1


WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


RUN pip install uv


COPY requirements.txt .
RUN uv install -r requirements.txt

# Stage 2: Production stage
FROM python:3.11-slim

WORKDIR /app


COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages


COPY . .


EXPOSE 3021


ENV IS_DEV=False
ENV SECURE_LOGIN=True

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3021"]