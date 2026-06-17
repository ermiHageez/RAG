FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# 1. Added a 1000-second timeout to survive slow speeds
# 2. Added Docker BuildKit caching so if it fails at 200MB, it resumes from 200MB next time
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --default-timeout=1000 --user -r requirements.txt

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app
COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000 8001

ENTRYPOINT ["/entrypoint.sh"]