from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate

from prompt_templates.recipe_extractor_prompt import RECIPE_EXTRACTOR_PROMPT


def get_recipe_extractor_chain(verbose: bool = False):
    prompt = PromptTemplate(input_variables=["input"], template=RECIPE_EXTRACTOR_PROMPT)
    llm = ChatOpenAI(  # type: ignore
        temperature=0,
    )
    recipe_extractor_chain = LLMChain(llm=llm, prompt=prompt, verbose=verbose)
    return recipe_extractor_chain
