from operator import itemgetter

from langchain_core.runnables import Runnable, RunnableLambda

from food_co2_estimator.language.translator import translate_if_danish


def get_translation_chain() -> Runnable:
    return {
        "inputs": itemgetter("inputs"),
        "language": itemgetter("language"),
    } | RunnableLambda(translate_if_danish)
