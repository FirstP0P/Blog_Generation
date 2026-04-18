import uvicorn
from fastapi import FastAPI, Request
from src.graphs.graph_builder import GraphBuilder
from src.llms.groqllm import GroqLLM
from src.utils.file_saver import save_blog_to_markdown # <-- Add this impor

import os
from dotenv import load_dotenv
load_dotenv()

app=FastAPI()

print(os.getenv("LANGCHAIN_API_KEY"))
os.environ["LANGSMITH_API_KEY"]=os.getenv("LANGCHAIN_API_KEY") # type: ignore

@app.post("/blogs")
async def create_blogs(request:Request):

    data=await request.json()
    topic= data.get("topic","")
    language = data.get("language", '')
    print(language)

    groqllm=GroqLLM()
    llm=groqllm.get_llm()

    graph_builder=GraphBuilder(llm)

    # Initialize state variable
    state = {}

    if topic and language:
        graph=graph_builder.setup_graph(usecase="language")
        state=graph.invoke({"topic":topic,"current_language":language.lower()}) # type: ignore

    elif topic:
        graph=graph_builder.setup_graph(usecase="topic")
        state=graph.invoke({"topic":topic}) # type: ignore

    # <-- Add the file saving logic here -->
    saved_filepath = None
    if state: # Ensure state is not empty before saving
        saved_filepath = save_blog_to_markdown(state)

    # Return the state and the path where the file was saved
    return {
        "data": state,
        "message": f"Blog successfully saved to {saved_filepath}" if saved_filepath else "No blog generated"
    }

if __name__=="__main__":
    uvicorn.run("app:app",host="0.0.0.0",port=8000,reload=True)
