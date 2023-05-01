from typing import Literal

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate

from prompt_templates.weight_est_prompts import (
    DK_WEIGHT_EST_PROMPT,
    EN_WEIGHT_EST_PROMPT,
)


def get_en_weight_est(language: Literal["da", "en"], verbose: bool = False):
    prompt = PromptTemplate(
        input_variables=["input"],
        template=EN_WEIGHT_EST_PROMPT if language == "en" else DK_WEIGHT_EST_PROMPT,
    )
    llm = ChatOpenAI(  # type: ignore
        temperature=0,
    )
    en_weight_est_chain = LLMChain(llm=llm, prompt=prompt, verbose=verbose)

    return en_weight_est_chain
