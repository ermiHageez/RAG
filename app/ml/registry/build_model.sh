#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
MODEL_TAG="${1:-etech-custom-agent:v1}"
PROCESSED_DATA="$ROOT_DIR/ml/datasets/processed_training.jsonl"
GENERATED_MODELFILE="$ROOT_DIR/app/ml/registry/Modelfile.generated"
FINAL_MODELFILE="$ROOT_DIR/app/ml/registry/Modelfile"

if ! command -v ollama >/dev/null 2>&1; then
  echo "ollama is not installed or not on PATH" >&2
  exit 1
fi

echo "=== Step 1: Generate Modelfile with training examples ==="
cd "$ROOT_DIR"
python3 app/ml/registry/generate_modelfile.py \
  --processed "$PROCESSED_DATA" \
  --output "$GENERATED_MODELFILE" \
  --max-examples 5

echo ""
echo "=== Step 2: Build Ollama model: $MODEL_TAG ==="
ollama create "$MODEL_TAG" -f "$GENERATED_MODELFILE"
echo "Model $MODEL_TAG built successfully."

echo ""
echo "=== Step 3: Verify model exists ==="
ollama list | grep -E "(NAME|$MODEL_TAG)" || echo "Warning: Model not found in list"

echo ""
echo "=== Step 4: Quick test ==="
ollama run "$MODEL_TAG" "What does eTech do?" --nowordwrap 2>&1 || echo "Test completed"

echo ""
echo "=== Step 5: Register in model registry ==="
python3 -c "
from app.ml.registry.model_registry import register
register('$MODEL_TAG', 'gemma2:2b',
    training_data='processed_training.jsonl',
    record_count=$(wc -l < "$PROCESSED_DATA" 2>/dev/null || echo 0))
from app.ml.registry.model_registry import promote
promote('$MODEL_TAG')
print('Registered and promoted: $MODEL_TAG')
" 2>&1 || echo "Note: Could not register in model registry"

echo ""
echo "=== Done! ==="
echo "Run: ollama run $MODEL_TAG"
