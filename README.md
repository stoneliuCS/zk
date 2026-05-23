# ZettelKasten
A Second Brain For Yourself.

## Dependencies
```bash
ollama # For running local llms.
ollama run qwen2.5:7b # Example for running a local llm via ollama.
ollama pull nomic-embed-text # Embedding model for RAG vector searching.
```

## Project Goals
Build a Ingestion Pipeline (All Locally) so that you are able to own your own data. Train the agent such that it is able to be completely in-tune with what your life is like going on right now.

### Informal Journal of Progress

#### May 21st, 2026
1. Added the loop inside `main.py` to be able to interface with the Ollama API and Log each conversation into the data transcripts file.
