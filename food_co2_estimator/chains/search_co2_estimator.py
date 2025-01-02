from langchain_core.runnables import RunnablePassthrough

from food_co2_estimator.prompt_templates.search_co2_estimator import (
    SEARCH_CO2_EMISSION_PROMPT,
)
from food_co2_estimator.pydantic_models.search_co2_estimator import CO2SearchResults
from food_co2_estimator.retrievers.search_retriever import batch_co2_search_retriever
from food_co2_estimator.utils.openai_model import get_model


def get_search_co2_emission_chain(verbose: bool):
    llm = get_model(
        pydantic_model=CO2SearchResults,
        verbose=verbose,
    )

    return (
        {
            "search_results": batch_co2_search_retriever,
            "ingredients": RunnablePassthrough(),
        }
        | SEARCH_CO2_EMISSION_PROMPT
        | llm
    )
