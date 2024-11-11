from langchain_core.runnables import Runnable

from food_co2_estimator.output_parsers.recipe_extractor import Recipe
from food_co2_estimator.prompt_templates.recipe_extractor import RECIPE_EXTRACTOR_PROMPT
from food_co2_estimator.utils.openai_model import get_model


def get_recipe_extractor_chain(verbose: bool = False) -> Runnable:

    llm = get_model(pydantic_model=Recipe, model_name="gpt-4o-mini", verbose=verbose)

    chain = RECIPE_EXTRACTOR_PROMPT | llm
    return chain
