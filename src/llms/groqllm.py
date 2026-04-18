from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

class GroqLLM:
    # def __init__(self):
    #     load_dotenv()

    # def get_llm(self):
    #     try:
    #         os.environ["GROQ_API_KEY"]=self.groq_api_key=os.getenv("GROQ_API_KEY") # type: ignore
    #         llm=ChatGroq(api_key=self.groq_api_key,model="llama-3.1-8b-instant") # type: ignore
    #         return llm
    #     except Exception as e:
    #         raise ValueError("Error occurred with exception: {e}")

    def get_llm(self):
        load_dotenv()

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found")

        return ChatGroq(
            api_key=api_key,
            model="llama-3.1-8b-instant",
            temperature=0
        )
