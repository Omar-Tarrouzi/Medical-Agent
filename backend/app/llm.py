import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def get_llm(temperature: float = 0.3):
    """Retourne une instance du modèle LLM configuré (Groq)."""
    return ChatGroq(
        model=os.getenv("MODEL_NAME", "llama-3.3-70b-versatile"),
        temperature=temperature,
        api_key=os.getenv("GROQ_API_KEY"),
    )


# Instance globale partagée par tous les agents
llm = get_llm()