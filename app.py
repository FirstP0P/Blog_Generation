import uvicorn
import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from src.graphs.graph_builder import GraphBuilder
from src.llms.groqllm import GroqLLM
from src.utils.file_saver import save_blog_to_markdown

import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")  # type: ignore


@app.get("/")
def root():
    return {"message": "Blog Generator API is running."}


# ── Standard (non-streaming) endpoint — kept for compatibility ─────────────────
@app.post("/blogs")
async def create_blogs(request: Request):
    data     = await request.json()
    topic    = data.get("topic", "")
    language = data.get("language", "").strip().lower()
    tone     = data.get("tone", "professional").strip().lower()
    length   = data.get("length", "medium").strip().lower()

    llm           = GroqLLM().get_llm()
    graph_builder = GraphBuilder(llm)
    base_state    = {"topic": topic, "tone": tone, "length": length}
    state         = {}

    if topic and language:
        graph = graph_builder.setup_graph(usecase="language")
        state = graph.invoke({**base_state, "current_language": language})
    elif topic:
        graph = graph_builder.setup_graph(usecase="topic")
        state = graph.invoke(base_state)

    saved_filepath = save_blog_to_markdown(state) if state else None
    return {
        "data":    state,
        "message": f"Blog saved to {saved_filepath}" if saved_filepath else "No blog generated",
    }


# ── Streaming SSE endpoint ─────────────────────────────────────────────────────
@app.post("/blogs/stream")
async def stream_blogs(request: Request):
    data     = await request.json()
    topic    = data.get("topic", "")
    language = data.get("language", "").strip().lower()
    tone     = data.get("tone", "professional").strip().lower()
    length   = data.get("length", "medium").strip().lower()

    async def event_generator():
        try:
            llm           = GroqLLM().get_llm()
            graph_builder = GraphBuilder(llm)
            base_state    = {"topic": topic, "tone": tone, "length": length}

            if topic and language:
                graph      = graph_builder.setup_graph(usecase="language")
                init_state = {**base_state, "current_language": language}
            else:
                graph      = graph_builder.setup_graph(usecase="topic")
                init_state = base_state

            # Accumulate full state by merging each node's output.
            # graph.stream() yields {node_name: {keys_that_node_returned}}
            # We merge all of these to reconstruct complete final state.
            full_state = dict(init_state)

            for chunk in graph.stream(init_state):
                for node_name, node_output in chunk.items():
                    # Merge node output into accumulated state
                    if isinstance(node_output, dict):
                        full_state.update(node_output)
                    # Send node-complete event to UI
                    event = json.dumps({"node": node_name, "status": "done"})
                    yield f"data: {event}\n\n"
                    await asyncio.sleep(0.05)

            save_blog_to_markdown(full_state)

            done_event = json.dumps({"node": "__end__", "status": "done", "result": full_state})
            yield f"data: {done_event}\n\n"

        except Exception as e:
            err = json.dumps({"node": "__error__", "error": str(e)})
            yield f"data: {err}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
