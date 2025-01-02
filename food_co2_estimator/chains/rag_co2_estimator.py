from langchain_core.runnables import RunnablePassthrough, RunnableSerializable

from food_co2_estimator.prompt_templates.rag_co2_estimator import (
    RAG_CO2_EMISSION_PROMPT,
)
from food_co2_estimator.pydantic_models.co2_estimator import CO2Emissions
from food_co2_estimator.retrievers.emission_retriever import batch_emission_retriever
from food_co2_estimator.utils.openai_model import get_model


def rag_co2_emission_chain(verbose: bool) -> RunnableSerializable:
    llm = get_model(
        pydantic_model=CO2Emissions,
        verbose=verbose,
    )

    return (
        {"context": batch_emission_retriever, "ingredients": RunnablePassthrough()}
        | RAG_CO2_EMISSION_PROMPT
        | llm
    )
