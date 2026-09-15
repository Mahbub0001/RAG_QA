import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    llm_model: str
    groq_api_key: str

def get_settings()-> Settings:
    groq_api_key = os.environ.get("GROQ_API_KEY", "")
    llm_model = os.environ.get("LLM_MODEL", "gpt-4o")

    return Settings(
        llm_model=llm_model,
        groq_api_key=groq_api_key
        
    )
