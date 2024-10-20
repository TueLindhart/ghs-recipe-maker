import os

from langchain_openai import ChatOpenAI

DEFAULT_MODEL = "gpt-3.5-turbo-16k"


def get_model_name() -> str:
    return os.getenv("GPT_MODEL", DEFAULT_MODEL)


def get_model():
    return ChatOpenAI(model=get_model_name(), temperature=0)
