from food_co2_estimator.output_parsers.weight_estimator import WeightEstimates
from food_co2_estimator.prompt_templates.weight_estimator import WEIGHT_EST_PROMPT
from food_co2_estimator.utils.openai_model import get_model


def get_weight_estimator_chain(verbose: bool = False):

    llm = get_model(
        model_name="gpt-4o-mini", pydantic_model=WeightEstimates, verbose=verbose
    )

    return WEIGHT_EST_PROMPT | llm
