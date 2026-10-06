from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings

MODEL_NAME = "gemini-2.5-flash"


def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0,
        api_key=settings.google_api_key,
        timeout=60,
        max_retries=2,
        thinking_budget=0
    )
