# Ragchat

Chat with your documents using RAG. Upload PDFs, ask questions, get cited answers.

[![CI](https://github.com/krrishapatel/ragchat/actions/workflows/ci.yml/badge.svg)](https://github.com/krrishapatel/ragchat/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## How it works

```
PDF upload → chunk → embed (Ollama) → store (ChromaDB)
                                            ↓
Question → embed → similarity search → LLM generates cited answer
```

**Stack:** FastAPI, ChromaDB, LangChain, Ollama (local LLM)

## Quick start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally

```bash
# Pull required models
ollama pull llama3.2
ollama pull nomic-embed-text
```

### Install & run

```bash
git clone https://github.com/krrishapatel/ragchat.git
cd ragchat
pip install -e ".[dev]"

# Start the API server
ragchat serve
```

API docs available at http://localhost:8000/docs

### CLI usage

```bash
# Ingest a PDF
ragchat ingest path/to/document.pdf

# Ask a question
ragchat query "What are the key findings?"
```

### Docker

```bash
docker compose up
```

This starts both Ollama and the ragchat API. Access at http://localhost:8000.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/ingest` | Upload a PDF (multipart form) |
| POST | `/query` | Ask a question (JSON body) |

### Example

```bash
# Upload a PDF
curl -X POST http://localhost:8000/ingest \
  -F "file=@paper.pdf"

# Ask a question
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main conclusion?"}'
```

Response:
```json
{
  "answer": "The main conclusion is that...",
  "sources": [
    {"filename": "paper.pdf", "page": 12, "snippet": "..."}
  ]
}
```

## Development

```bash
# Run tests
pytest -v

# Lint
ruff check .
ruff format .
```

## Architecture

```
ragchat/
├── app/
│   ├── api.py        # FastAPI endpoints
│   ├── cli.py        # CLI interface
│   ├── config.py     # Settings (env vars)
│   ├── ingest.py     # PDF parsing + chunking + embedding
│   └── query.py      # RAG retrieval + LLM generation
├── tests/
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## License

MIT
