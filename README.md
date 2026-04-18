# ✍️ AI Blog Generator — LangGraph + Groq + Streamlit

A full-stack AI blog generation app powered by **LangGraph**, **Groq LLM**, **FastAPI**, and **Streamlit**. Generate SEO-friendly blog posts on any topic, control tone and length, translate to Hindi or French, watch each LangGraph node light up live as your blog is built, and browse your full generation history — all from a single UI.

---

## 🖥️ Features

| Feature | Description |
|---|---|
| 🔀 Live graph animation | Nodes pulse blue while running, turn green with ✓ when done |
| 🎭 Tone control | Professional, Casual, Academic, Creative, Persuasive |
| 📏 Length control | Short (300–500w), Medium (600–900w), Long (1000–1500w) |
| 🌐 Translation | Hindi and French — Markdown formatting preserved |
| 🕘 Blog history | Every generated blog saved in session; click to reload any past blog |
| ⬇️ Export | Download generated blog as `.md` or `.txt` |
| 💾 Auto-save | Blogs saved automatically to `generated_blogs/` as Markdown files |

---

## 📁 Project Structure

```
Blog_Generation/
├── src/
│   ├── __init__.py
│   ├── states/
│   │   ├── __init__.py
│   │   └── blogstate.py          # BlogState (TypedDict) + Blog (Pydantic)
│   │                             # Fields: topic, blog, current_language, tone, length
│   ├── nodes/
│   │   ├── __init__.py
│   │   └── blog_node.py          # BlogNode class — all LangGraph node methods
│   │                             # title_creation, content_generation,
│   │                             # translation, route, route_decision
│   ├── llms/
│   │   ├── __init__.py
│   │   └── groqllm.py            # GroqLLM wrapper → get_llm()
│   ├── graphs/
│   │   ├── __init__.py
│   │   └── graph_builder.py      # GraphBuilder class
│   │                             # build_topic_graph(), build_language_graph()
│   │                             # setup_graph(usecase)
│   └── utils/
│       ├── __init__.py
│       └── file_saver.py         # save_blog_to_markdown(state)
├── generated_blogs/              # Auto-created; stores .md files of all blogs
├── app.py                        # FastAPI backend
│                                 # POST /blogs        — standard invoke
│                                 # POST /blogs/stream — SSE streaming for live UI
├── streamlit_app.py              # Streamlit UI with live graph + history
├── .env                          # API keys (never commit this)
├── requirements.txt
└── README.md
```

---

## 🔀 LangGraph Workflows

Two graphs are built depending on whether translation is requested.

### Topic Graph (no translation)

```
START
  │
  ▼
title_creation          ← BlogNode.title_creation()
  │                        Reads:   state["topic"], state["tone"]
  │                        Returns: {"blog": {"title": ...}}
  ▼
content_generation      ← BlogNode.content_generation()
  │                        Reads:   state["topic"], state["tone"], state["length"]
  │                        Returns: {"blog": {"title": ..., "content": ...}}
  ▼
END
```

### Language Graph (with translation)

```
START
  │
  ▼
title_creation
  │
  ▼
content_generation
  │
  ▼
route                   ← BlogNode.route() → route_decision()
  │                        Conditional edge on state["current_language"]
  │
  ├── "hindi"  ──►  hindi_translation  ──► END
  │                 BlogNode.translation()
  │
  └── "french" ──►  french_translation ──► END
                    BlogNode.translation()
```

**Source:** `src/graphs/graph_builder.py` → `GraphBuilder.build_topic_graph()` / `build_language_graph()`

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| LLM inference | Groq — `llama-3.1-8b-instant` |
| Workflow orchestration | LangGraph |
| LLM framework | LangChain |
| Backend API | FastAPI + Uvicorn |
| Streaming | Server-Sent Events (SSE) via `graph.stream()` |
| Frontend UI | Streamlit + `st.components.v1.html()` |
| Data validation | Pydantic |
| Environment | python-dotenv |

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/FirstP0P/Blog_Generation.git
cd Blog_Generation
```

### 2. Create virtual environment

```bash
# Using uv (recommended)
uv init
uv add -r requirements.txt

# OR using pip
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
LANGCHAIN_API_KEY=your_langsmith_api_key_here
```

- Groq API key → [https://console.groq.com/keys](https://console.groq.com/keys)
- LangSmith API key → [https://smith.langchain.com](https://smith.langchain.com) *(optional, for tracing)*

---

## ▶️ Running the App

You need **two terminals** running simultaneously.

### Terminal 1 — FastAPI backend

```bash
python app.py
```

API starts at: `http://localhost:8000`

### Terminal 2 — Streamlit UI

```bash
streamlit run streamlit_app.py
```

UI opens at: `http://localhost:8501`

---

## 🎛️ Streamlit UI Guide

### Sidebar

| Control | Description |
|---|---|
| **Topic** | Free-text input for the blog subject |
| **Tone** | Radio pills: Professional / Casual / Academic / Creative / Persuasive |
| **Length** | Slider: Short / Medium / Long |
| **Translation** | Dropdown: None / Hindi / French |
| **Generate Blog** | Triggers the LangGraph pipeline via SSE stream |
| **🕘 History** | List of all blogs generated this session (newest first) |
| **🗑️ Clear** | Wipes the entire history list |

### Main Area

**Settings bar** — live preview of current tone, length, language, and topic word count.

**LangGraph Execution Flow** *(left column)*
- Graph renders automatically for Topic or Language workflow based on sidebar selection
- Each node pulses blue with a spinner while it is running
- Each node turns green with ✓ when it completes
- Arrows between nodes turn green as execution flows through them
- For the Language graph, the untaken translation branch fades out once routing is decided

**Generated Blog** *(right column)*
- Shows a live node execution log while generation is in progress
- Displays the full formatted blog once complete, with metadata badges
- Blogs loaded from history show a `🕘 From history` badge

**Download row** (appears after generation)
- Download as `.md` or `.txt`
- Word and character count displayed

### Blog History

- Every successfully generated blog is automatically added to the history list in the sidebar
- Each entry shows the truncated title and metadata (tone · timestamp · language)
- Click any entry to instantly load that blog — the graph panel also restores to the completed state
- History is session-scoped (persists until the browser tab is closed or history is cleared)

---

## 🌐 API Reference

### `GET /`

Health check.

```json
{ "message": "Blog Generator API is running." }
```

---

### `POST /blogs`

Standard synchronous blog generation. Returns the complete blog in one response.

**Request body:**

```json
{
  "topic": "The Future of Quantum Computing",
  "tone": "professional",
  "length": "medium",
  "language": "hindi"
}
```

| Field | Type | Required | Default | Options |
|---|---|---|---|---|
| `topic` | string | ✅ | — | Any string |
| `tone` | string | ❌ | `professional` | `professional` `casual` `academic` `creative` `persuasive` |
| `length` | string | ❌ | `medium` | `short` `medium` `long` |
| `language` | string | ❌ | `""` | `hindi` `french` |

**Response:**

```json
{
  "data": {
    "topic": "The Future of Quantum Computing",
    "tone": "professional",
    "length": "medium",
    "blog": {
      "title": "Quantum Computing in 2030: A New Era Begins",
      "content": "## Introduction\n\n..."
    },
    "current_language": "hindi"
  },
  "message": "Blog saved to generated_blogs/the_future_of_quantum_computing_hindi.md"
}
```

---

### `POST /blogs/stream`

Streaming SSE endpoint used by the Streamlit UI for live node-by-node animation.

**Request body:** same as `/blogs`.

**Response:** `text/event-stream` — one event per node as it completes:

```
data: {"node": "title_creation",     "status": "done"}

data: {"node": "content_generation", "status": "done"}

data: {"node": "route",              "status": "done"}

data: {"node": "hindi_translation",  "status": "done"}

data: {"node": "__end__", "status": "done", "result": { ...full state... }}
```

**How it works internally:**
1. FastAPI calls `graph.stream(init_state)` — LangGraph yields `{node_name: output_dict}` for each node as it finishes
2. Each yield is serialised and sent as an SSE `data:` line
3. Node outputs are merged into `full_state` incrementally — no second graph invocation needed
4. The final `__end__` event carries the complete accumulated state including `blog.title` and `blog.content`

---

## 📂 File Output

- Blogs are saved to `generated_blogs/` automatically after every generation
- Format: Markdown (`.md`)
- Filename pattern: `topic_slug.md` or `topic_slug_language.md`
- Example: `future_of_quantum_computing_hindi.md`

---

## 🔧 Troubleshooting

| Error | Fix |
|---|---|
| `GROQ_API_KEY not found` | Ensure `.env` exists in project root with the correct key |
| `Cannot connect to FastAPI at localhost:8000` | Run `python app.py` before launching Streamlit |
| `ModuleNotFoundError` | Activate virtual environment; run commands from project root |
| `Node X already present` | Fixed — ensure you are using the latest `app.py` |
| Streamlit showing raw HTML tags | Fixed — ensure you are using the latest `streamlit_app.py` |
| History disappears on refresh | Expected — history is session-scoped; see Future Improvements |
| Empty blog content | Try a more specific topic; check Groq API quota |

---

## 🗺️ Future Improvements

- [ ] Persist blog history across sessions (SQLite or JSON file)
- [ ] Search and filter history by topic, tone, or date
- [ ] Support more languages (Spanish, German, Japanese)
- [ ] Add a blog cover image generation node (DALL-E / Stable Diffusion)
- [ ] Token-level streaming of blog content as it is written
- [ ] SEO meta description generation node
- [ ] User authentication and per-user history
- [ ] Deploy backend on Railway / Render, UI on Streamlit Cloud


