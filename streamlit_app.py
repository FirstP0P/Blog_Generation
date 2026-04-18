import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import time
from datetime import datetime

st.set_page_config(
    page_title="AI Blog Generator",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d2e 0%, #161925 100%);
        border-right: 1px solid #2e3250;
    }
    .blog-card {
        background: #1a1d2e; border: 1px solid #2e3250;
        border-radius: 12px; padding: 2rem 2.5rem;
        line-height: 1.85; font-size: 1.05rem; color: #e0e4f0;
    }
    .blog-title { font-size: 1.7rem; font-weight: 700; color: #a0aaff; margin-bottom: 0.5rem; }
    .blog-divider { border: none; border-top: 1px solid #2e3250; margin: 1rem 0 1.5rem 0; }
    .badge {
        display: inline-block; background: #2e3250; color: #a0aaff;
        border-radius: 20px; padding: 3px 12px; font-size: 0.8rem; margin-right: 6px;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #5c6bc0, #7986cb);
        color: white; border: none; border-radius: 8px;
        padding: 0.65rem 1.5rem; font-size: 1rem; font-weight: 600;
        width: 100%; transition: opacity 0.2s;
    }
    div.stButton > button:hover { opacity: 0.85; }
    .stat-box {
        background: #1e2236; border: 1px solid #2e3250;
        border-radius: 10px; padding: 0.9rem; text-align: center;
    }
    .stat-number { font-size: 1.5rem; font-weight: 700; color: #7c8ff5; }
    .stat-label  { font-size: 0.75rem; color: #6e7a9f; margin-top: 2px; }
    .placeholder-box {
        border: 2px dashed #2e3250; border-radius: 12px;
        padding: 4rem 2rem; text-align: center; color: #4a5580;
    }
    /* History card */
    .hist-card {
        background: #1a1d2e; border: 1px solid #2e3250; border-radius: 8px;
        padding: 10px 14px; margin-bottom: 8px; cursor: pointer;
        transition: border-color 0.2s;
    }
    .hist-card:hover { border-color: #5c6bc0; }
    .hist-title { color: #a0aaff; font-size: 0.85rem; font-weight: 600;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .hist-meta  { color: #4a5580; font-size: 0.72rem; margin-top: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [
    ("blog_title", None), ("blog_content", None), ("blog_meta", {}),
    ("node_states", {}), ("generation_done", False), ("active_node", None),
    ("blog_history", []),   # ← NEW: list of past blog dicts
    ("viewing_history", False),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✍️ Blog Generator")
    st.markdown("*Powered by LangGraph + Groq*")
    st.divider()

    st.markdown("#### 📝 Topic")
    topic = st.text_area("topic_input", label_visibility="collapsed",
        placeholder="e.g. The Future of Quantum Computing", height=100)

    st.markdown("#### 🎭 Tone")
    tone = st.radio("tone_radio", label_visibility="collapsed",
        options=["Professional", "Casual", "Academic", "Creative", "Persuasive"],
        index=0, horizontal=True)

    st.markdown("#### 📏 Blog Length")
    length_map = {
        "Short  (300–500 words)": "short",
        "Medium (600–900 words)": "medium",
        "Long (1000–1500 words)": "long",
    }
    length_label = st.select_slider("length_slider", label_visibility="collapsed",
        options=list(length_map.keys()), value="Medium (600–900 words)")
    length = length_map[length_label]

    st.markdown("#### 🌐 Translation (optional)")
    language = st.selectbox("language_select", label_visibility="collapsed",
        options=["None", "Hindi", "French"])

    st.divider()
    generate_btn = st.button("🚀 Generate Blog", use_container_width=True)

    # ── History section ────────────────────────────────────────────────────────
    st.divider()
    history = st.session_state.blog_history

    col_h, col_c = st.columns([3, 1])
    with col_h:
        st.markdown(f"#### 🕘 History ({len(history)})")
    with col_c:
        if history and st.button("🗑️", help="Clear all history", use_container_width=True):
            st.session_state.blog_history = []
            st.rerun()

    if not history:
        st.markdown("<div style='color:#3a4060;font-size:0.8rem;padding:8px 0'>"
                    "No blogs generated yet.</div>", unsafe_allow_html=True)
    else:
        for i, entry in enumerate(reversed(history)):
            idx = len(history) - 1 - i   # real index in list
            label = entry["title"][:38] + "…" if len(entry["title"]) > 38 else entry["title"]
            meta_str = f"{entry['meta'].get('tone','').title()} · {entry['timestamp']}"
            if entry['meta'].get('language') not in (None, 'None', ''):
                meta_str += f" · {entry['meta']['language']}"

            # Button to load this entry
            if st.button(f"📄 {label}", key=f"hist_{idx}", use_container_width=True,
                         help=meta_str):
                st.session_state.blog_title      = entry["title"]
                st.session_state.blog_content    = entry["content"]
                st.session_state.blog_meta       = entry["meta"]
                st.session_state.node_states     = entry.get("node_states", {})
                st.session_state.generation_done = True
                st.session_state.viewing_history = True
                st.rerun()

    st.markdown("<small style='color:#4a5068'>Backend: FastAPI · localhost:8000</small>",
        unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("## 📰 AI Blog Generator")
st.markdown("Watch each LangGraph node light up live as your blog is generated.")

c1, c2, c3, c4 = st.columns(4)
topic_words = len(topic.split()) if topic.strip() else 0
for col, icon, label in [
    (c1, "🎭", f"Tone: {tone}"),
    (c2, "📏", length_label.split("(")[0].strip()),
    (c3, "🌐", f"Lang: {language}"),
    (c4, "📝", f"{topic_words} word{'s' if topic_words != 1 else ''}"),
]:
    with col:
        st.markdown(
            f'<div class="stat-box"><div class="stat-number">{icon}</div>'
            f'<div class="stat-label">{label}</div></div>',
            unsafe_allow_html=True)

st.markdown("---")

# ── Graph HTML builder ─────────────────────────────────────────────────────────
GRAPH_CSS = """
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #0f1117; font-family: 'Segoe UI', sans-serif; padding: 16px; }
.graph-wrap {
    background: #13162a; border: 1px solid #2e3250; border-radius: 14px;
    padding: 24px 16px; display: flex; flex-direction: column;
    align-items: center; gap: 0;
}
.pill {
    border-radius: 20px; padding: 6px 32px; font-size: 13px; font-weight: 600;
    border: 1.5px solid; text-align: center; min-width: 90px; transition: all 0.4s;
}
.pill-idle { background: #1e2236; border-color: #3a4060; color: #4a5580; }
.pill-done { background: #0d2520; border-color: #1d9e75; color: #5DCAA5; }
.node-box {
    border-radius: 10px; padding: 12px 24px; min-width: 230px; text-align: center;
    border: 2px solid; transition: all 0.4s ease;
}
.node-label { font-size: 14px; font-weight: 600; }
.node-sub   { font-size: 11px; margin-top: 4px; opacity: 0.75; }
.state-idle   .node-box { background: #1e2236; border-color: #3a4060; color: #6a7a9a; }
.state-active .node-box {
    background: #252a4a; border-color: #7c8ff5; color: #d0d8ff;
    box-shadow: 0 0 18px rgba(124,143,245,0.45);
    animation: pulse 1s ease-in-out infinite;
}
.state-done .node-box { background: #0d2520; border-color: #1d9e75; color: #5DCAA5; }
.route-box {
    border-radius: 6px; padding: 10px 24px; min-width: 180px; text-align: center;
    border: 2px solid; transition: all 0.4s;
}
.route-idle   .route-box { background: #1e1a0a; border-color: #5a4a10; color: #7a6a30; }
.route-active .route-box {
    background: #2a2010; border-color: #FAC775; color: #FAC775;
    box-shadow: 0 0 18px rgba(250,199,117,0.4);
    animation: pulse-gold 1s ease-in-out infinite;
}
.route-done .route-box { background: #1e1a0a; border-color: #FAC775; color: #FAC775; }
.arrow-wrap { display: flex; flex-direction: column; align-items: center; }
.arrow-line { width: 2px; background: #2e3250; transition: background 0.4s; }
.arrow-line.done   { background: #1d9e75; }
.arrow-line.active { background: #7c8ff5; }
.arrow-head {
    width: 0; height: 0;
    border-left: 5px solid transparent; border-right: 5px solid transparent;
    border-top: 7px solid #2e3250; transition: border-top-color 0.4s;
}
.arrow-head.done   { border-top-color: #1d9e75; }
.arrow-head.active { border-top-color: #7c8ff5; }
.cond-label {
    font-size: 11px; color: #FAC775; background: #1e1a0a;
    border: 1px solid #FAC775; border-radius: 10px;
    padding: 2px 8px; margin-bottom: 6px; white-space: nowrap;
}
.branch-row { display: flex; gap: 40px; justify-content: center; align-items: flex-start; }
.branch     { display: flex; flex-direction: column; align-items: center; }
.hindi-done  .node-box { background: #1a0e08; border-color: #F0997B; color: #F0997B; }
.french-done .node-box { background: #080e1a; border-color: #85B7EB; color: #85B7EB; }
.hindi-idle  .node-box,
.french-idle .node-box { background: #1e2236; border-color: #3a4060; color: #6a7a9a; opacity: 0.4; }
.hindi-active .node-box { background: #2a1a0e; border-color: #F0997B; color: #F0997B;
    box-shadow: 0 0 18px rgba(240,153,123,0.4); animation: pulse 1s infinite; }
.french-active .node-box { background: #0e1428; border-color: #85B7EB; color: #85B7EB;
    box-shadow: 0 0 18px rgba(133,183,235,0.4); animation: pulse 1s infinite; }
.spinner {
    display: inline-block; width: 12px; height: 12px;
    border: 2px solid rgba(255,255,255,0.2); border-top-color: currentColor;
    border-radius: 50%; animation: spin 0.7s linear infinite;
    vertical-align: middle; margin-right: 5px;
}
@keyframes pulse      { 0%,100%{opacity:1} 50%{opacity:0.7} }
@keyframes pulse-gold { 0%,100%{box-shadow:0 0 14px rgba(250,199,117,0.3)} 50%{box-shadow:0 0 28px rgba(250,199,117,0.6)} }
@keyframes spin       { to { transform: rotate(360deg); } }
</style>
"""

def _icon(state):
    if state == "active": return '<span class="spinner"></span>'
    if state == "done":   return '<span>&#10003;&nbsp;</span>'
    return ""

def build_graph_html(node_states, use_lang, lang_lower):
    def ns(name):
        return node_states.get(name, "idle")

    def arrow(prev_node, height=32):
        s = ns(prev_node)
        ac = "done" if s == "done" else ("active" if s == "active" else "")
        return (f'<div class="arrow-wrap">'
                f'<div class="arrow-line {ac}" style="height:{height}px"></div>'
                f'<div class="arrow-head {ac}"></div></div>')

    start_done = any(v == "done" for v in node_states.values())
    start_cls  = "pill-done" if start_done else "pill-idle"
    tc = ns("title_creation")
    cg = ns("content_generation")

    topic_nodes = f"""
    <div class="pill {start_cls}">START</div>
    {arrow("__start__" if start_done else "__none__", 28) if start_done else
     '<div class="arrow-wrap"><div class="arrow-line" style="height:28px"></div><div class="arrow-head"></div></div>'}
    <div class="state-{tc}">
      <div class="node-box">
        {_icon(tc)}<span class="node-label">title_creation</span>
        <div class="node-sub">BlogNode.title_creation()</div>
      </div>
    </div>
    {arrow("title_creation", 28)}
    <div class="state-{cg}">
      <div class="node-box">
        {_icon(cg)}<span class="node-label">content_generation</span>
        <div class="node-sub">BlogNode.content_generation()</div>
      </div>
    </div>
    """

    if not use_lang:
        end_done = cg == "done"
        body = topic_nodes + f"""
    {arrow("content_generation", 28)}
    <div class="pill {'pill-done' if end_done else 'pill-idle'}">END</div>"""
    else:
        rt = ns("route")
        hi = ns("hindi_translation")
        fr = ns("french_translation")
        hi_box_extra = 'style="opacity:0.3"' if (rt == "done" and lang_lower != "hindi" and hi == "idle") else ""
        fr_box_extra = 'style="opacity:0.3"' if (rt == "done" and lang_lower != "french" and fr == "idle") else ""

        body = topic_nodes + f"""
    {arrow("content_generation", 28)}
    <div class="route-{rt}">
      <div class="route-box">
        {_icon(rt)}<span class="node-label">route</span>
        <div class="node-sub">route_decision()</div>
      </div>
    </div>
    <div class="arrow-wrap">
      <div class="arrow-line {'done' if rt=='done' else ''}" style="height:16px"></div>
    </div>
    <div class="branch-row">
      <div class="branch" {hi_box_extra}>
        <div class="cond-label">"hindi"</div>
        <div class="hindi-{hi}">
          <div class="node-box" style="min-width:160px">
            {_icon(hi)}<span class="node-label">hindi_translation</span>
            <div class="node-sub">translation()</div>
          </div>
        </div>
        <div class="arrow-wrap">
          <div class="arrow-line {'done' if hi=='done' else ''}" style="height:20px"></div>
          <div class="arrow-head {'done' if hi=='done' else ''}"></div>
        </div>
        <div class="pill {'pill-done' if hi=='done' else 'pill-idle'}">END</div>
      </div>
      <div class="branch" {fr_box_extra}>
        <div class="cond-label">"french"</div>
        <div class="french-{fr}">
          <div class="node-box" style="min-width:160px">
            {_icon(fr)}<span class="node-label">french_translation</span>
            <div class="node-sub">translation()</div>
          </div>
        </div>
        <div class="arrow-wrap">
          <div class="arrow-line {'done' if fr=='done' else ''}" style="height:20px"></div>
          <div class="arrow-head {'done' if fr=='done' else ''}"></div>
        </div>
        <div class="pill {'pill-done' if fr=='done' else 'pill-idle'}">END</div>
      </div>
    </div>"""

    return f"<!DOCTYPE html><html><head>{GRAPH_CSS}</head><body><div class='graph-wrap'>{body}</div></body></html>"


def graph_height(use_lang):
    return 560 if use_lang else 380


# ── Layout ─────────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1.6], gap="large")

with left_col:
    st.markdown("#### 🔀 LangGraph Execution Flow")
    graph_slot = st.empty()

with right_col:
    st.markdown("#### 📄 Generated Blog")
    blog_slot = st.empty()


def render_graph():
    use_lang   = st.session_state.blog_meta.get("language", language) not in (None, "None", "")
    lang_lower = st.session_state.blog_meta.get("language", language).lower()
    html = build_graph_html(st.session_state.node_states, use_lang, lang_lower)
    with graph_slot:
        components.html(html, height=graph_height(use_lang), scrolling=False)


def render_blog():
    if st.session_state.blog_title and st.session_state.blog_content:
        meta = st.session_state.blog_meta
        badge = (
            f'<span class="badge">🎭 {meta.get("tone","").title()}</span>'
            f'<span class="badge">📏 {meta.get("length","").split("(")[0].strip()}</span>'
        )
        if meta.get("language") not in (None, "None", ""):
            badge += f'<span class="badge">🌐 {meta["language"]}</span>'
        if st.session_state.viewing_history:
            badge += '<span class="badge">🕘 From history</span>'
        content_html = st.session_state.blog_content.replace("\n", "<br>")
        blog_slot.markdown(f"""
{badge}<br><br>
<div class="blog-card">
  <div class="blog-title">{st.session_state.blog_title}</div>
  <hr class="blog-divider">{content_html}
</div>""", unsafe_allow_html=True)
    else:
        done  = [n for n, s in st.session_state.node_states.items() if s == "done"]
        active = st.session_state.active_node
        if done or active:
            rows = "".join(
                f"<div style='color:#5DCAA5;margin:5px 0'>&#10003; <b>{n}</b> — completed</div>"
                for n in done)
            if active:
                rows += f"<div style='color:#a0aaff;margin:5px 0'>&#9679; <b>{active}</b> — running…</div>"
            blog_slot.markdown(
                f"<div style='background:#13162a;border:1px solid #2e3250;"
                f"border-radius:10px;padding:1.5rem'>"
                f"<div style='color:#6a7a9a;font-size:13px;margin-bottom:10px'>Node execution log</div>"
                f"{rows}</div>", unsafe_allow_html=True)
        else:
            blog_slot.markdown("""
<div class="placeholder-box">
  <div style="font-size:3rem;margin-bottom:1rem">✍️</div>
  <div style="font-size:1.1rem;font-weight:600;color:#6070a0">Your generated blog will appear here</div>
  <div style="margin-top:0.5rem;font-size:0.9rem">Fill in topic and settings, then click <b>Generate Blog</b></div>
</div>""", unsafe_allow_html=True)


# Initial render
render_graph()
render_blog()

# ── Generate ───────────────────────────────────────────────────────────────────
if generate_btn:
    if not topic.strip():
        st.warning("⚠️ Please enter a topic before generating.")
    else:
        st.session_state.node_states     = {}
        st.session_state.blog_title      = None
        st.session_state.blog_content    = None
        st.session_state.blog_meta       = {}
        st.session_state.generation_done = False
        st.session_state.active_node     = None
        st.session_state.viewing_history = False
        render_graph()
        render_blog()

        payload = {"topic": topic.strip(), "tone": tone.lower(), "length": length}
        if language != "None":
            payload["language"] = language.lower()

        try:
            with requests.post(
                "http://localhost:8000/blogs/stream",
                json=payload, stream=True, timeout=180,
            ) as resp:
                resp.raise_for_status()

                for raw_line in resp.iter_lines():
                    if not raw_line:
                        continue
                    line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
                    if not line.startswith("data:"):
                        continue

                    event = json.loads(line[5:].strip())
                    node  = event.get("node", "")

                    if node == "__error__":
                        st.error(f"❌ {event.get('error', 'Unknown error')}")
                        break

                    if node == "__end__":
                        result  = event.get("result", {})
                        blog    = result.get("blog", {})
                        title   = blog.get("title", topic) if isinstance(blog, dict) else str(blog)
                        content = blog.get("content", "")  if isinstance(blog, dict) else ""
                        meta    = {"tone": tone, "length": length_label,
                                   "language": language, "topic": topic}

                        st.session_state.blog_title      = title
                        st.session_state.blog_content    = content
                        st.session_state.blog_meta       = meta
                        st.session_state.active_node     = None
                        st.session_state.generation_done = True

                        for n in st.session_state.node_states:
                            st.session_state.node_states[n] = "done"

                        # ── Save to history ────────────────────────────────
                        st.session_state.blog_history.append({
                            "title":       title,
                            "content":     content,
                            "meta":        meta,
                            "node_states": dict(st.session_state.node_states),
                            "timestamp":   datetime.now().strftime("%d %b %H:%M"),
                            "word_count":  len(content.split()),
                        })

                        render_graph()
                        render_blog()
                        break

                    else:
                        prev = st.session_state.active_node
                        if prev:
                            st.session_state.node_states[prev] = "done"
                        st.session_state.node_states[node] = "active"
                        st.session_state.active_node = node
                        render_graph()
                        render_blog()
                        time.sleep(0.05)

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to FastAPI at `localhost:8000`. Run `python app.py` first.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ── Download buttons ───────────────────────────────────────────────────────────
if st.session_state.blog_title and st.session_state.blog_content:
    st.markdown("---")
    full_md = f"# {st.session_state.blog_title}\n\n{st.session_state.blog_content}"
    meta = st.session_state.blog_meta
    d1, d2, d3 = st.columns([1, 1, 2])
    with d1:
        st.download_button("⬇️ Download .md", data=full_md,
            file_name=f"{meta.get('topic','blog')[:30].replace(' ','_').lower()}.md",
            mime="text/markdown", use_container_width=True)
    with d2:
        st.download_button("⬇️ Download .txt", data=full_md,
            file_name=f"{meta.get('topic','blog')[:30].replace(' ','_').lower()}.txt",
            mime="text/plain", use_container_width=True)
    with d3:
        wc = len(st.session_state.blog_content.split())
        st.info(f"📊 **{wc}** words · **{len(st.session_state.blog_content)}** characters")
