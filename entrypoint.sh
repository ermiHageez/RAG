#!/bin/bash
set -e

if [ -z "$GROQ_API_KEY" ]; then
    echo "ERROR: GROQ_API_KEY is not set"
    exit 1
fi

if [ -z "$N8N_WEBHOOK_URL" ]; then
    echo "WARN: N8N_WEBHOOK_URL is not set — n8n integration will be mocked"
fi

trap 'echo "Shutting down..."; exit 0' SIGTERM SIGINT

exec "$@"
