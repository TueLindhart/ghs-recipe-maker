import os
from typing import Any

from langchain_openai import ChatOpenAI

DEFAULT_MODEL = "gpt-3.5-turbo-16k"


def get_model_name_from_env() -> str:
    return os.getenv("GPT_MODEL", DEFAULT_MODEL)


def get_model(
    pydantic_model: Any | None = None,
    model_name: str | None = None,
    verbose: bool = False,
):

    llm = ChatOpenAI(
        model=get_model_name_from_env() if model_name is None else model_name,
        temperature=0,
        verbose=verbose,
    )
    if pydantic_model is None:
        return llm
    llm = llm.with_structured_output(pydantic_model)
    return llm
