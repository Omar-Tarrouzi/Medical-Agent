import os
from dotenv import load_dotenv 
from langchain_openai import ChatOpenAI
load_dotenv()

def get_llm(temperature: float =0.3):
    """ Retourne une instace du modele LLM configure"""

    return ChatOpenAI(
    model= os.getenv ("MODEL_NAME","gpt-4o-mini"),
    temperature =temperature,
    api_key=os.getenv("OPENAI_API_KEY"),
    )

    llm = get_llm()