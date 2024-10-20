from langchain.chains.llm import LLMChain
from langchain.prompts.prompt import PromptTemplate

from food_co2_estimator.prompt_templates.recipe_extractor import (
    RECIPE_EXTRACTOR_PROMPT,
    recipe_output_parser,
)
from food_co2_estimator.utils.openai_model import get_model


def get_recipe_extractor_chain(verbose: bool = False):
    prompt = PromptTemplate(
        template=RECIPE_EXTRACTOR_PROMPT,
        input_variables=["input"],
        partial_variables={
            "format_instructions": recipe_output_parser.get_format_instructions()
        },
        output_parser=recipe_output_parser,
    )

    recipe_extractor_chain = LLMChain(llm=get_model(), prompt=prompt, verbose=verbose)
    return recipe_extractor_chain
