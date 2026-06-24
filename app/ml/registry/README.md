# Ollama Registry

This folder contains the Modelfile and build script for the custom Ollama model.

## Build the model

Run this from the repository root:

```bash
bash app/ml/registry/build_model.sh
```

What the script does:

1. Runs `ollama create inventory-custom-agent:v1 -f app/ml/registry/Modelfile`
2. Runs `ollama list` so you can confirm the model exists

## Manual build command

If you want to run the commands yourself:

```bash
ollama create inventory-custom-agent:v1 -f app/ml/registry/Modelfile
ollama list
```

## Modelfile summary

- Base model: `gemma2:2b`
- Temperature: `0.2`
- Context window: `2048`
- Threads: `2`
- System role: Inventory AI core system

## Verify

Check that the model appears in the list:

```bash
ollama list
```

