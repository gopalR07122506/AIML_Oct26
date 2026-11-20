"""
Streamlit front end for the Graph RAG project (Neo4j + Ollama + LLM router).

Run:   streamlit run app.py
Needs: graphrag.py and .env in the same folder (and optionally .streamlit/config.toml for the theme).
"""
import glob
import os

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Graph RAG Assistant", page_icon="🕸️", layout="wide")

# ------------------------------------------------------------------ Styling
CSS = """
<style>
/* Theme-neutral styling: works on dark AND light themes (no hard-coded white backgrounds). */
.block-container {padding-top: 1.6rem; max-width: 1100px;}
.hero {background: linear-gradient(135deg, #6C47FF 0%, #8E6BFF 45%, #00C2A8 100%);
       padding: 28px 32px; border-radius: 18px; margin-bottom: 20px;
       box-shadow: 0 10px 30px rgba(108,71,255,.30);}
.hero h1 {margin: 0; padding: 0; font-size: 2rem; color: #fff !important;}
.hero p {margin: 6px 0 0; font-size: 1.02rem; color: #fff !important; opacity: .93;}
.hero .chips span {display: inline-block; background: rgba(255,255,255,.2); color: #fff;
       border-radius: 999px; padding: 4px 13px; margin: 14px 8px 0 0; font-size: .82rem;}
.pill {display: inline-block; padding: 3px 13px; border-radius: 999px; font-size: .8rem;
       font-weight: 600; color: #fff; margin-right: 8px;}
.pill-graph {background: #6C47FF;} .pill-vector {background: #00A98F;} .pill-direct {background: #F59E0B;}
.pill-note {font-size: .85rem; opacity: .7;}
.card {background: rgba(128,128,128,.10); border: 1px solid rgba(128,128,128,.28);
       border-radius: 14px; padding: 16px 18px; height: 100%;}
.card .num {display: inline-block; width: 26px; height: 26px; line-height: 26px; text-align: center;
       border-radius: 50%; background: rgba(142,107,255,.25); color: #B7A3FF; font-weight: 700; margin-bottom: 8px;}
.card h4 {margin: 0 0 4px; font-size: 1rem;}
.card p {margin: 0; opacity: .75; font-size: .88rem;}
[data-testid="stMetric"] {background: rgba(108,71,255,.16); border-radius: 12px; padding: 8px 12px;}
[data-testid="stMetricValue"] {font-size: 1.4rem;}
[data-testid="stChatMessage"] {background: rgba(128,128,128,.08); border: 1px solid rgba(128,128,128,.25);
       border-radius: 14px; padding: 10px 14px; margin-bottom: 10px;}
.stButton > button {border-radius: 10px; font-weight: 600;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

try:
    import graphrag as g  # loads .env, creates the Neo4j driver and the Ollama client
except SystemExit as e:  # graphrag.py exits when NEO4J_PASSWORD is missing
    st.error(f"Configuration problem: {e}")
    st.stop()

# Hero banner: drawn immediately, before any database call, so the page is never blank.
st.markdown(
    f"""
<div class="hero">
  <h1>🕸️ Graph RAG Assistant</h1>
  <p>Ask questions across your knowledge graph. An LLM router picks the best search for every question.</p>
  <div class="chips"><span>🧠 {g.LLM_MODEL}</span><span>🧬 {g.EMBED_MODEL}</span><span>🗄️ Neo4j</span><span>🚦 LLM Router</span></div>
</div>
""",
    unsafe_allow_html=True,
)

ROUTE_LABELS = {"graph": "🕸️ Graph search", "vector": "🔍 Vector search", "direct": "💬 Direct answer"}
EXAMPLES = [
    "Who works on Project Atlas?",
    "What is Project Atlas about?",
    "What is the capital of France?",
]


def stretch(fn, *args, **kwargs):
    """Call a Streamlit widget so it fills the width on both old and new Streamlit versions."""
    try:
        return fn(*args, width="stretch", **kwargs)
    except Exception:  # noqa: BLE001
        return fn(*args, use_container_width=True, **kwargs)


# ------------------------------------------------------------------ Neo4j / Ollama helpers
@st.cache_resource
def _fast_driver():
    """Re-create the Neo4j driver with short timeouts so an unreachable database fails fast."""
    from neo4j import GraphDatabase

    try:
        g.driver.close()
    except Exception:  # noqa: BLE001
        pass
    g.driver = GraphDatabase.driver(
        g.NEO4J_URI,
        auth=(g.NEO4J_USER, g.NEO4J_PASSWORD),
        connection_timeout=8,
        connection_acquisition_timeout=10,
        max_transaction_retry_time=4,
    )
    return g.driver


_fast_driver()


@st.cache_data(ttl=5, show_spinner=False)
def db_stats() -> dict:
    try:
        with g.driver.session() as s:
            entities = s.run("MATCH (n:Entity) RETURN count(n) AS c").single()["c"]
            links = s.run("MATCH ()-[r:RELATED]->() RETURN count(r) AS c").single()["c"]
            chunks = s.run("MATCH (n:Chunk) RETURN count(n) AS c").single()["c"]
        return {"ok": True, "entities": entities, "links": links, "chunks": chunks}
    except Exception as ex:  # noqa: BLE001
        return {"ok": False, "error": str(ex)}


def _model_name(m):
    for key in ("model", "name"):
        v = getattr(m, key, None) or (m.get(key) if isinstance(m, dict) else None)
        if v:
            return v
    return ""


@st.cache_data(ttl=10, show_spinner=False)
def ollama_status() -> dict:
    """Check that Ollama is running and that the chat and embedding models are downloaded."""
    try:
        resp = g.client.list()
        items = resp["models"] if "models" in resp else []
        have = {_model_name(m) for m in items}

        def present(name):
            full = name if ":" in name else name + ":latest"
            return full in have or name in have

        missing = [n for n in (g.LLM_MODEL, g.EMBED_MODEL) if not present(n)]
        return {"ok": True, "missing": missing}
    except Exception as ex:  # noqa: BLE001
        return {"ok": False, "error": str(ex)}


def graph_facts(question: str):
    """Find entities in the question and return the facts within 2 hops."""
    entities = g.llm_json(g.ENTITY_PROMPT.format(q=question)).get("entities", [])
    facts = set()
    with g.driver.session() as s:
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
            facts.update((r["h"], r["rel"], r["t"]) for r in rows)
    return entities, sorted(facts)


def vector_chunks(question: str, k: int = 3):
    with g.driver.session() as s:
        rows = s.run(
            "CALL db.index.vector.queryNodes('chunk_index', $k, $emb) YIELD node, score "
            "RETURN node.text AS text, score",
            k=k, emb=g.embed(question),
        )
        return [(r["text"], r["score"]) for r in rows]


def fetch_graph(limit: int, search: str):
    with g.driver.session() as s:
        rows = s.run(
            """
            MATCH (a:Entity)-[r:RELATED]->(b:Entity)
            WHERE $s = '' OR a.key CONTAINS $s OR b.key CONTAINS $s
            RETURN a.name AS head, r.type AS relation, b.name AS tail
            LIMIT $limit
            """,
            s=search.lower().strip(), limit=limit,
        )
        return [(r["head"], r["relation"], r["tail"]) for r in rows]


def ingest_text(text: str, source: str, progress_cb):
    """Same logic as graphrag.ingest, but with progress and file-unique chunk ids."""
    g.setup_db()
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    for i, chunk in enumerate(chunks):
        triples = g.extract_triples(chunk)
        with g.driver.session() as s:
            s.run(
                "MERGE (c:Chunk {id:$id}) SET c.text=$text, c.embedding=$emb",
                id=f"{source}:{i}", text=chunk, emb=g.embed(chunk),
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
                    rel=t["relation"], id=f"{source}:{i}",
                )
        progress_cb((i + 1) / len(chunks), f"Chunk {i + 1}/{len(chunks)}: {len(triples)} facts found")


# ------------------------------------------------------------------ RAG logic
def plan_answer(question: str, mode: str, top_k: int) -> dict:
    """Route the question, retrieve context, and build the final prompt."""
    route = g.route(question) if mode.startswith("Auto") else mode
    plan = {"route": route, "entities": [], "facts": [], "chunks": [], "fallback": False}

    if route == "graph":
        plan["entities"], plan["facts"] = graph_facts(question)
        if not plan["facts"]:                       # graph empty -> fall back to vector search
            plan["fallback"] = True
            plan["route"] = route = "vector"
    if route == "vector":
        plan["chunks"] = vector_chunks(question, top_k)

    if route == "direct":
        plan["prompt"] = question
    else:
        if plan["facts"]:
            context = "\n".join(f"{h} -[{r}]-> {t}" for h, r, t in plan["facts"])
        else:
            context = "\n".join(text for text, _ in plan["chunks"])
        plan["prompt"] = g.ANSWER_PROMPT.format(context=context, q=question)
    return plan


def stream_llm(prompt: str):
    stream = g.client.chat(
        model=g.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
        stream=True,
    )
    for part in stream:
        yield part["message"]["content"]


# ------------------------------------------------------------------ UI helpers
def to_dot(facts, limit: int = 40) -> str:
    def esc(x):
        return str(x).replace('"', '\\"')

    lines = [
        "digraph G {",
        "rankdir=LR;",
        'bgcolor="transparent";',
        'node [shape=box, style="rounded,filled", fillcolor="#5B45E0", color="#8E6BFF", fontcolor="white", fontname="Helvetica"];',
        'edge [fontname="Helvetica", fontsize=10, color="#00C2A8", fontcolor="#9AA3B5"];',
    ]
    for h, rel, t in facts[:limit]:
        lines.append(f'"{esc(h)}" -> "{esc(t)}" [label="{esc(rel)}"];')
    lines.append("}")
    return "\n".join(lines)


def show_facts(facts):
    stretch(st.dataframe, pd.DataFrame(facts, columns=["head", "relation", "tail"]), hide_index=True)
    stretch(st.graphviz_chart, to_dot(facts))


def render_meta(meta: dict):
    route = meta["route"]
    note = "  graph was empty, so vector search was used" if meta.get("fallback") else ""
    st.markdown(
        f'<span class="pill pill-{route}">{ROUTE_LABELS.get(route, route)}</span>'
        f'<span class="pill-note">{note}</span>',
        unsafe_allow_html=True,
    )
    if meta.get("entities"):
        st.caption("Entities found in your question: " + ", ".join(map(str, meta["entities"])))
    if meta.get("facts"):
        with st.expander(f"🕸️ Graph facts used ({len(meta['facts'])})"):
            show_facts(meta["facts"])
    if meta.get("chunks"):
        with st.expander(f"📄 Text chunks used ({len(meta['chunks'])})"):
            for text, score in meta["chunks"]:
                st.markdown(f"**similarity {score:.3f}**  \n{text}")
                st.divider()


def how_it_works():
    steps = [
        ("1", "Route", "A small LLM reads your question and picks graph, vector or direct."),
        ("2", "Retrieve", "Graph search follows connections in Neo4j. Vector search finds similar text."),
        ("3", "Answer", "The LLM writes a reply using only the evidence found, and shows its sources."),
    ]
    for col, (n, title, text) in zip(st.columns(3), steps):
        col.markdown(
            f'<div class="card"><div class="num">{n}</div><h4>{title}</h4><p>{text}</p></div>',
            unsafe_allow_html=True,
        )
    st.write("")


# ------------------------------------------------------------------ Sidebar
with st.sidebar:
    st.markdown("### 🕸️ Graph RAG")
    page = st.radio("View", ["💬 Chat", "🔎 Explore graph"], label_visibility="collapsed")

    st.markdown("#### 🔌 Status")
    stats = db_stats()
    if stats["ok"]:
        st.success("Neo4j connected", icon="✅")
        c1, c2, c3 = st.columns(3)
        c1.metric("Entities", stats["entities"])
        c2.metric("Links", stats["links"])
        c3.metric("Chunks", stats["chunks"])
    else:
        st.error("Neo4j not reachable. Check NEO4J_URI, user and password in .env", icon="🚫")
        st.code(stats["error"][:300])

    ol = ollama_status()
    if not ol["ok"]:
        st.error("Ollama not reachable. Start it with: ollama serve", icon="🚫")
    elif ol["missing"]:
        st.warning("Missing models. Run: " + "  ".join(f"ollama pull {m}" for m in ol["missing"]), icon="⚠️")
    else:
        st.success("Ollama ready", icon="✅")

    st.markdown("#### ⚙️ Settings")
    mode = st.selectbox(
        "Router mode",
        ["Auto (router decides)", "graph", "vector", "direct"],
        help="Auto lets the LLM router choose. Pick a route to force it and compare answers.",
    )
    top_k = st.slider("Vector search: chunks to use", 1, 8, 3)

    st.markdown("#### 📥 Add data")
    uploaded = st.file_uploader("Upload a .txt file (paragraphs separated by a blank line)", type=["txt"])
    data_files = sorted(glob.glob("data/*.txt"))
    picked = st.selectbox("...or pick a file from data/", ["-"] + data_files)
    can_build = bool(uploaded) or picked != "-"
    if st.button("Build graph", disabled=not can_build, type="primary"):
        if uploaded:
            text, source = uploaded.getvalue().decode("utf-8", "ignore"), uploaded.name
        else:
            with open(picked, encoding="utf-8") as fh:
                text, source = fh.read(), os.path.basename(picked)
        bar = st.progress(0.0, text="Starting...")
        try:
            ingest_text(text, source, lambda p, m: bar.progress(p, text=m))
            db_stats.clear()
            st.toast("Graph updated", icon="✅")
            st.rerun()
        except Exception as ex:  # noqa: BLE001
            st.error(f"Ingest failed: {ex}")

    with st.expander("⚠️ Danger zone"):
        confirm = st.checkbox("Delete ALL nodes and relationships")
        if st.button("Clear graph", disabled=not confirm):
            with g.driver.session() as s:
                s.run("MATCH (n) DETACH DELETE n")
            db_stats.clear()
            st.rerun()

    if st.button("🧹 Clear chat"):
        st.session_state.messages = []
        st.rerun()


# ------------------------------------------------------------------ Pages
def chat_page():
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("pending", None)

    if not st.session_state.messages:
        how_it_works()
        st.markdown("**Try one of these:**")
        for col, ex in zip(st.columns(len(EXAMPLES)), EXAMPLES):
            if stretch(col.button, ex):
                st.session_state.pending = ex
                st.rerun()

    for m in st.session_state.messages:
        with st.chat_message(m["role"], avatar="🧑‍💻" if m["role"] == "user" else "🤖"):
            st.markdown(m["content"])
            if m.get("meta"):
                render_meta(m["meta"])

    prompt = st.chat_input("Ask a question about your documents...") or st.session_state.pending
    st.session_state.pending = None
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        meta = None
        try:
            with st.spinner("Routing and retrieving..."):
                meta = plan_answer(prompt, mode, top_k)
            render_meta(meta)
            reply = st.write_stream(stream_llm(meta["prompt"]))
        except Exception as ex:  # noqa: BLE001
            reply = f"⚠️ Something went wrong: {ex}"
            st.error(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply, "meta": meta})


def explore_page():
    c1, c2 = st.columns([1, 2])
    limit = c1.slider("Max relationships", 10, 300, 60)
    search = c2.text_input("Filter by entity name (optional)", placeholder="e.g. atlas")
    try:
        facts = fetch_graph(limit, search)
    except Exception as ex:  # noqa: BLE001
        st.error(f"Could not read the graph: {ex}")
        return
    if not facts:
        st.info("No relationships found. Add data from the sidebar with 'Build graph'.")
        return
    st.caption(f"Showing {len(facts)} relationships (the picture shows the first 40)")
    show_facts(facts)


if page.startswith("💬"):
    chat_page()
else:
    explore_page()
