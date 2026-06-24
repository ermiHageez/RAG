# ML Dataset Pipeline

This folder contains the offline data collection and training prep flow for memory interactions.

## What gets written

- Raw interaction log: `ml/datasets/raw_interactions.jsonl`
- Processed training data: `ml/datasets/processed_training.jsonl`

## 1. Collect interactions

The API already writes interactions when you call:

- `POST /memory/conversation`
- `POST /memory/{custom_memory_type}`

Each successful save appends one JSON line to the raw dataset file.

## 2. Build the processed dataset

Run this from the repository root:

```bash
python -m app.ml.dataset_builder
```

What it does:

- Reads `ml/datasets/raw_interactions.jsonl`
- Skips records where query or response is shorter than 4 characters
- Writes chat-formatted JSONL to `ml/datasets/processed_training.jsonl`

## 3. Input format

Each raw line should look like this:

```json
{"session_id":"abc","query":"find stock levels","response":{"answer":"SKU A is low"},"timestamp":"2026-06-22T12:00:00Z"}
```

The builder converts it into:

```json
{"messages":[{"role":"user","content":"find stock levels"},{"role":"assistant","content":"SKU A is low"}]}
```

## 4. Quick check

After building, verify the output file exists and has lines:

```bash
wc -l ml/datasets/processed_training.jsonl
head -n 2 ml/datasets/processed_training.jsonl
```

