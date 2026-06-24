#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
MODELFILE_PATH="$ROOT_DIR/app/ml/registry/Modelfile"

if ! command -v ollama >/dev/null 2>&1; then
  echo "ollama is not installed or not on PATH" >&2
  exit 1
fi

cd "$ROOT_DIR"
ollama create inventory-custom-agent:v1 -f "$MODELFILE_PATH"
ollama list
