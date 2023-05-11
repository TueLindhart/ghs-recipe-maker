from typing import Literal

from langchain import GoogleSearchAPIWrapper, LLMChain, LLMMathChain  # , OpenAI
from langchain.agents import AgentExecutor, Tool, ZeroShotAgent
from langchain.chat_models import ChatOpenAI

from chains.co2_sql import get_en_co2_sql_chain
from chains.weight_est import get_en_weight_est
from prompt_templates.main_agent import (
    DK_AGENT_PREFIX,
    DK_AGENT_SUFFIX,
    EN_AGENT_PREFIX,
    EN_AGENT_SUFFIX,
)
