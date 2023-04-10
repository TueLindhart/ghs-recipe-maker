from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate

from prompt_templates.en_weight_est_prompts import EN_WEIGHT_EST_PROMPT


def get_en_weight_est(verbose: bool = True):
    prompt = PromptTemplate(input_variables=["input", "table_info", "dialect"], template=EN_WEIGHT_EST_PROMPT)
    llm = ChatOpenAI(  # type: ignore
        temperature=0,
    )
    en_weight_est_chain = LLMChain(llm=llm, prompt=prompt, verbose=verbose)

    return en_weight_est_chain
