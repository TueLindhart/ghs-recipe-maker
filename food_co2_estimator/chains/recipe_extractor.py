from langchain.chains.llm import LLMChain

from food_co2_estimator.prompt_templates.recipe_extractor import (
    RECIPE_EXTRACTOR_PROMPT,
    recipe_output_parser,
)
from food_co2_estimator.utils.openai_model import get_model


def get_recipe_extractor_chain(verbose: bool = False):

    recipe_extractor_chain = LLMChain(
        llm=get_model(),
        prompt=RECIPE_EXTRACTOR_PROMPT,
        verbose=verbose,
        output_parser=recipe_output_parser,
    )
    return recipe_extractor_chain
