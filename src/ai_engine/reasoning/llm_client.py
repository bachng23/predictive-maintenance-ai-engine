import os

from langchain_openrouter import ChatOpenRouter


def build_openrouter_chat_model() -> ChatOpenRouter | None:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None

    return ChatOpenRouter(
        api_key=api_key,
        model=os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash"),
        temperature=0,
    )
