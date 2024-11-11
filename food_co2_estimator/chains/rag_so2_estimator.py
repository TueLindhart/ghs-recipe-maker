from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI

from food_co2_estimator.output_parsers.sql_co2_estimator import CO2Emissions
from food_co2_estimator.prompt_templates.rag_co2_estimator import (
    RAG_SO2_EMISSION_PROMPT,
)
from food_co2_estimator.retrievers.emission_retriever import (
    get_emission_retriever_chain,
)
from food_co2_estimator.utils.openai_model import get_model


def batch_emission_retriever(inputs: List[str]):
    retriever_chain = get_emission_retriever_chain()
    return dict(zip(inputs, retriever_chain.batch(inputs)))


def rag_co2_emission_chain() -> Runnable:

    llm = get_model(pydantic_model=CO2Emissions, model_name="gpt-4o-mini")

    return (
        {"context": batch_emission_retriever, "ingredients": RunnablePassthrough()}
        | RAG_SO2_EMISSION_PROMPT
        | llm
    )
