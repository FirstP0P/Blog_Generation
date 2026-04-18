# Blog Generator with LangGraph & Groq

A FastAPI-based blog generation system powered by **LangGraph**, **Groq LLM**, and **LangChain**. The application can generate SEO-friendly blog posts from a given topic and optionally translate them into **Hindi** or **French**.

---

## Features

- **Topic-based Blog Generation**: Generates title and detailed content for any given topic.
- **Multilingual Support**: Translates the generated blog into Hindi or French.
- **LangGraph Workflow**: Uses stateful graph-based orchestration for clean and modular processing.
- **Structured Output Handling**: Uses Pydantic models for state management.
- **File Saving**: Automatically saves generated blogs as Markdown files with proper naming.
- **FastAPI Backend**: Simple and scalable REST API endpoint.
- **Environment Configuration**: Secure API key management using `.env`.

---

## Project Structure

```
blog-generator/
├── src/
│   ├──__init__.py
│   ├── states/
│   │   └──__init__.py
│   │   └── blogstate.py          # Pydantic + TypedDict state definitions
│   ├── nodes/
│   │   └──__init__.py
│   │   └── blog_node.py          # All LangGraph nodes (title, content, translation, routing)
│   ├── llms/
│   │   └──__init__.py
│   │   └── groqllm.py            # Groq LLM wrapper
│   ├── graphs/
│   │   └──__init__.py
│   │   └── graph_builder.py      # Builds topic and language-based graphs
│   ├── utils/
│   │   └──__init__.py
│   │   └── file_saver.py         # Saves blog to Markdown file
├── app.py                        # FastAPI application
├── .env                          # Environment variables (not committed)
├── requirements.txt              # Python dependencies
└── README.md
```

---

## Tech Stack

- **Python 3.10+**
- **FastAPI** – Web framework
- **LangGraph** – Graph-based workflow orchestration
- **LangChain** – LLM integration
- **Groq** – Fast LLM inference (Llama-3.1-8B-Instant)
- **Pydantic** – Data validation & settings
- **Uvicorn** – ASGI server

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/FirstP0P/Blog_Generation.git
cd blog-generator
```

### 2. Create Virtual Environment (Recommended)

```bash
uv init
```

### 3. Install Dependencies

Create a `requirements.txt` file with the following content:

```txt
langchain
langgraph
langchain_community
langchain_core
langchain_groq
fastapi
uvicorn
watchdog
langgraph-cli[inmem]
```

Then install:

```bash
uv add -r requirements.txt
```

Enable virtual environment:
```bash
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
```

### 4. Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
LANGCHAIN_API_KEY=your_langsmith_api_key_here
```

> Get your Groq API key from: [https://console.groq.com/keys](https://console.groq.com/keys)

---

## How to Run the Project

### Start the FastAPI Server

```bash
python app.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at: **http://127.0.0.1:8000**

---

## API Usage

### Endpoint: `POST /blogs`

#### 1. Generate Blog in English (Default)

```bash
curl -X POST http://127.0.0.1:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Benefits of Artificial Intelligence in Healthcare"
  }'
```

## OR

### Postman:

```bash
{
    "topic":"Agentic AI"
}
```

#### 2. Generate Blog + Translate to Hindi/French

```bash
curl -X POST http://127.0.0.1:8000/blogs \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Future of Electric Vehicles",
    "language": "hindi"
  }'
```

## OR

### Postman:

```bash
{
    "topic":"Agentic AI",
    "language":"french"
}
```

Supported languages for translation: `hindi`, `french`

---

## Langgraph

Use the command below in command prompt to open langgraph interface:

```bash
langgraph dev
```

---

## Output

- The generated blog is returned in the JSON response.
- A Markdown file is automatically saved in the `generated_blogs/` folder.
- Filename format: `topic_language.md` (e.g., `artificial_intelligence_hindi.md`)


---

## Future Improvements

- Add support for more languages
- Add image generation for blog cover
- Add blog summarization node
- Add streaming response support
- Add authentication & rate limiting
- Deploy on Render / Railway / AWS

---

## Troubleshooting

- **Groq API Key Error**: Ensure `GROQ_API_KEY` is correctly set in `.env`
- **ModuleNotFoundError**: Make sure you're running from the project root and virtual environment is activated
- **Empty Content**: Try with a more specific topic

---

## License

MIT License
