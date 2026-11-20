"""
Graph RAG demo: Ollama (LLM + embeddings) + Neo4j (graph + vector index) + LLM router.
All settings are read from the .env file.

Usage:
    python graphrag.py ingest data/company.txt
    python graphrag.py ask "Who works on Project Atlas?"
    python graphrag.py chat
"""
import json
import os
import re
import sys

import ollama
from dotenv import load_dotenv
from neo4j import GraphDatabase

# ---------------- Config (from .env) ----------------
load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        sys.exit(f"Missing {name}. Copy .env.example to .env and fill it in.")
    return value


NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = _require("NEO4J_PASSWORD")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
EMBED_DIM = int(os.getenv("EMBED_DIM", "768"))

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
client = ollama.Client(host=OLLAMA_HOST)


# ---------------- Ollama helpers ----------------
def llm(prompt: str, json_mode: bool = False) -> str:
    kwargs = {"format": "json"} if json_mode else {}
    resp = client.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
        **kwargs,
    )
    return resp["message"]["content"]


def llm_json(prompt: str) -> dict:
    try:
        return json.loads(llm(prompt, json_mode=True))
    except json.JSONDecodeError:
        return {}


def embed(text: str) -> list[float]:
    return client.embed(model=EMBED_MODEL, input=text)["embeddings"][0]


# ---------------- Step 1: INGEST (text -> graph) ----------------
EXTRACT_PROMPT = """Extract knowledge-graph triples from the text below.
Return ONLY JSON in this format:
{{"triples": [{{"head": "...", "head_type": "Person|Project|Technology|Organization|Location|Role", "relation": "...", "tail": "...", "tail_type": "..."}}]}}

Rules:
- Use full names (e.g. "Priya Sharma", not "She"). Resolve pronouns.
- relation is a short verb phrase like WORKS_ON, REPORTS_TO, USES, LEADS, LOCATED_IN, HAS_ROLE.
- Only facts stated in the text.

Text:
{text}
"""


def extract_triples(text: str) -> list[dict]:
    data = llm_json(EXTRACT_PROMPT.format(text=text))
    good = []
    for t in data.get("triples", []):
        if all(isinstance(t.get(k), str) and t.get(k).strip() for k in ("head", "relation", "tail")):
            t["relation"] = re.sub(r"\W+", "_", t["relation"].strip()).upper()
            good.append(t)
    return good


def setup_db():
    with driver.session() as s:
        s.run("CREATE CONSTRAINT entity_key IF NOT EXISTS FOR (e:Entity) REQUIRE e.key IS UNIQUE")
        s.run(
            "CREATE VECTOR INDEX chunk_index IF NOT EXISTS FOR (c:Chunk) ON (c.embedding) "
            "OPTIONS {indexConfig: {`vector.dimensions`: $dim, `vector.similarity_function`: 'cosine'}}",
            dim=EMBED_DIM,
        )


def ingest(path: str):
    setup_db()
    text = open(path, encoding="utf-8").read()
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    for i, chunk in enumerate(chunks):
        triples = extract_triples(chunk)
        print(f"[{i + 1}/{len(chunks)}] {len(triples)} triples <- {chunk[:60]}...")
        with driver.session() as s:
            s.run(
                "MERGE (c:Chunk {id:$id}) SET c.text=$text, c.embedding=$emb",
                id=i, text=chunk, emb=embed(chunk),
            )
            for t in triples:
                s.run(
                    """
                    MERGE (h:Entity {key:$hk}) ON CREATE SET h.name=$hn, h.type=$ht
                    MERGE (t:Entity {key:$tk}) ON CREATE SET t.name=$tn, t.type=$tt
                    MERGE (h)-[:RELATED {type:$rel}]->(t)
                    WITH h, t
                    MATCH (c:Chunk {id:$id})
                    MERGE (c)-[:MENTIONS]->(h)
                    MERGE (c)-[:MENTIONS]->(t)
                    """,
                    hk=t["head"].lower(), hn=t["head"], ht=t.get("head_type", "Entity"),
                    tk=t["tail"].lower(), tn=t["tail"], tt=t.get("tail_type", "Entity"),
                    rel=t["relation"], id=i,
                )
    print("Done. Open http://localhost:7474 and run: MATCH (n)-[r]->(m) RETURN n,r,m")


# ---------------- Step 2: ROUTER ----------------
ROUTER_PROMPT = """You are a query router. Pick the best retrieval strategy for the question.

- "graph": the question is about relationships or connections between things
  (who works on what, who reports to whom, which tools are used by whom, multi-hop questions).
- "vector": the question asks for a description, explanation or summary of something in the documents.
- "direct": general knowledge or chit-chat that has nothing to do with the company documents.

Return ONLY JSON: {{"route": "graph" | "vector" | "direct"}}

Question: {q}
"""


def route(question: str) -> str:
    r = llm_json(ROUTER_PROMPT.format(q=question)).get("route", "vector")
    return r if r in {"graph", "vector", "direct"} else "vector"


# ---------------- Step 3: RETRIEVERS ----------------
ENTITY_PROMPT = """List the named entities (people, projects, technologies, organizations, places)
mentioned in the question. Return ONLY JSON: {{"entities": ["..."]}}

Question: {q}
"""


def graph_context(question: str) -> str:
    entities = llm_json(ENTITY_PROMPT.format(q=question)).get("entities", [])
    facts = set()
    with driver.session() as s:
        for e in entities:
            key = str(e).lower().strip()
            if not key:
                continue
            rows = s.run(
                """
                MATCH (n:Entity) WHERE n.key CONTAINS $k
                MATCH p=(n)-[:RELATED*1..2]-(:Entity)
                UNWIND relationships(p) AS r
                RETURN DISTINCT startNode(r).name AS h, r.type AS rel, endNode(r).name AS t
                LIMIT 60
                """,
                k=key,
            )
            facts.update(f"{r['h']} -[{r['rel']}]-> {r['t']}" for r in rows)
    return "\n".join(sorted(facts))


def vector_context(question: str, k: int = 3) -> str:
    with driver.session() as s:
        rows = s.run(
            "CALL db.index.vector.queryNodes('chunk_index', $k, $emb) YIELD node, score "
            "RETURN node.text AS text",
            k=k, emb=embed(question),
        )
        return "\n".join(r["text"] for r in rows)


# ---------------- Step 4: ANSWER ----------------
ANSWER_PROMPT = """Answer the question using ONLY the context below.
If the context is not enough, say "I don't know based on the documents."

Context:
{context}

Question: {q}
Answer:"""


def ask(question: str) -> str:
    r = route(question)
    print(f"\n[router] -> {r}")
    if r == "direct":
        return llm(question)
    context = graph_context(question) if r == "graph" else vector_context(question)
    if r == "graph" and not context:      # fallback: graph found nothing, try semantic search
        print("[router] graph empty -> falling back to vector")
        context = vector_context(question)
    print(f"[context]\n{context}\n")
    return llm(ANSWER_PROMPT.format(context=context, q=question))


# ---------------- CLI ----------------
if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "ingest":
        ingest(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == "ask":
        print(ask(" ".join(sys.argv[2:])))
    elif len(sys.argv) >= 2 and sys.argv[1] == "chat":
        while (q := input("\nYou: ").strip()) not in {"", "exit", "quit"}:
            print("Bot:", ask(q))
    else:
        print(__doc__)
    driver.close()
