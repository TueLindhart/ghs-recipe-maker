from typing import Any

from langchain.schema.runnable import RunnableSerializable

from food_co2_estimator.prompt_templates.weight_estimator import WEIGHT_EST_PROMPT
from food_co2_estimator.pydantic_models.weight_estimator import WeightEstimates
from food_co2_estimator.utils.openai_model import get_model


def get_weight_estimator_chain(
    verbose: bool = False,
) -> RunnableSerializable[Any, Any]:
    llm = get_model(pydantic_model=WeightEstimates, verbose=verbose)
    chain = WEIGHT_EST_PROMPT | llm
    return chain
