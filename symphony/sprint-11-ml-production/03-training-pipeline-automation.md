# Sprint 11 — ML Production: Training Pipeline Automation

## Goal
Automate the full ML lifecycle: raw data → processed dataset → fine-tune model → deploy. Every step is scripted, versioned, and reproducible.

## Steps

### 3.1 Run the Dataset Builder as a Scheduled Task

**File:** `app/ml/dataset_builder.py` + `scheduler.py`

- Refactor `build()` to be importable and callable from a scheduler:
  ```python
  def build(
      raw_path: str = "ml/datasets/raw_interactions.jsonl",
      output_path: str = "ml/datasets/processed_training.jsonl",
      min_chars: int = 4,
  ) -> BuildResult:
  ```
- Create `app/ml/scheduler.py` that calls `build()` every hour (via `asyncio` loop or separate thread)
- Only regenerate when new records have been added since last build (track via file mtime or record count in a state file)
- Output path includes date stamp: `processed_training-{YYYY-MM-DD-HH}.jsonl`
- Old builds are archived (keep last 24)

### 3.2 Create a Fine-Tuning Script

**File:** `app/ml/finetune.py` (new)

- Script that takes a processed JSONL dataset and fine-tunes a LoRA adapter using `llama.cpp` or `Ollama`:
  - Download base model if not cached
  - Convert processed JSONL to `.txt` training file (llama.cpp format)
  - Run `llama-finetune` or call Ollama's `/api/create` with a Modelfile that includes the training data
  - Output: a new tagged model (e.g., `etech-agent:v2-{date}`)
- Guarded by `FINETUNE_ENABLED` env var (default `False`)
- Log training metrics (loss, tokens/sec) to a `training_runs.jsonl` file

### 3.3 Add Model Versioning

**File:** `app/ml/registry/model_registry.py` (new)

- Track every model version in a `model_registry.json`:
  ```json
  {
    "versions": [
      {
        "tag": "etech-agent:v1",
        "base_model": "gemma2:2b",
        "training_data": "processed_training-2026-06-24.jsonl",
        "training_date": "2026-06-24T10:00:00Z",
        "record_count": 27,
        "eval_score": null,
        "status": "active"
      }
    ],
    "active": "etech-agent:v1"
  }
  ```
- `promote(tag: str)` — sets `active` to the given tag and updates the LLM config
- `rollback()` — reverts to previous version
- `list_versions()` — returns all versions with metadata

### 3.4 Build the Custom Ollama Model

**File:** `app/ml/registry/build_model.sh` (update)

- Run `bash app/ml/registry/build_model.sh` to create the `inventory-custom-agent:v1` model
- Add a `--with-training-data` flag that includes the latest processed dataset in the Modelfile's `MESSAGE` or `SYSTEM` block
- Register the built model in `model_registry.json` via step 3.3

### 3.5 Wire Training Data into the Agent System Prompt

**File:** `app/ml/registry/Modelfile`

- Update the Modelfile to reference the latest processed training data as few-shot examples:
  ```
  SYSTEM """
  You are eTech's AI Sales & Marketing Agent.
  
  {{ .System }}
  
  Training examples:
  {{ range .TrainingExamples }}
  User: {{ .query }}
  Assistant: {{ .response }}
  {{ end }}
  """
  ```
- When a new model version is promoted, update the Ollama model and restart the LLM connections

### 3.6 Add a CI/CD Pipeline Script

**File:** `app/ml/pipeline.py` (new)

- A single orchestrator script that runs the full pipeline:
  1. Check for new raw data → if none, exit
  2. Run `dataset_builder.build()`
  3. Run quality checks
  4. If quality score > threshold, run `finetune.py`
  5. Run evaluation benchmarks
  6. If eval score > previous version, run `promote(new_tag)`
  7. Send notification via alert webhook
- Designed to be called from cron, GitHub Actions, or any CI runner
- Idempotent: safe to run multiple times

## Acceptance Criteria
- [ ] `processed_training.jsonl` is regenerated hourly with new data
- [ ] Fine-tuning script produces a working Ollama model
- [ ] Model registry tracks all versions with training metadata
- [ ] `inventory-custom-agent:v1` is built and registered
- [ ] Training examples are injected into the model's system prompt
- [ ] Full pipeline script runs end-to-end and is idempotent
- [ ] Pipeline notifies via webhook on success/failure
