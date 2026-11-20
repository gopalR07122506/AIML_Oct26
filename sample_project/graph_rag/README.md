# Graph RAG Project (Neo4j + Ollama + LLM Router)

All settings and credentials live in the `.env` file. No secrets are written in the code.

## .env settings
| Key | Meaning |
|---|---|
| NEO4J_URI | Neo4j Bolt address (default bolt://localhost:7687) |
| NEO4J_USER / NEO4J_PASSWORD | Neo4j login (password: minimum 8 characters) |
| OLLAMA_HOST | Ollama server address |
| LLM_MODEL | Chat model for extraction, routing, answers |
| EMBED_MODEL / EMBED_DIM | Embedding model and its vector size (nomic-embed-text = 768) |

## 1. Setup
```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
docker compose up -d                                  # Neo4j reads user/password from .env
ollama pull llama3.2
ollama pull nomic-embed-text
```
Neo4j Browser: http://localhost:7474

## 2. Build the graph
```bash
python graphrag.py ingest data/company.txt
```

## 3. Ask questions
```bash
python graphrag.py ask "Who works on Project Atlas?"          # graph route
python graphrag.py ask "What is Project Atlas about?"         # vector route
python graphrag.py ask "What is the capital of France?"       # direct route
python graphrag.py chat
```

## Notes
- Change the Neo4j password in `.env` BEFORE the first `docker compose up`. If you change it later, run `docker compose down -v` first (this deletes stored data).
- Do not share or commit `.env`. Share `.env.example` instead (a .gitignore is included).
