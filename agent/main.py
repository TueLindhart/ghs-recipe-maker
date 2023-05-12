from types import coroutine
from typing import Literal

from langchain import (
    GoogleSearchAPIWrapper,
    GoogleSerperAPIWrapper,
    LLMChain,
    LLMMathChain,
)
from langchain.agents import AgentExecutor, Tool, ZeroShotAgent
from langchain.chat_models import ChatOpenAI

# from agent.search_agent import get_co2_google_search_agent
from agent.search_agent import get_co2_google_search_agent
from chains.co2_search import get_async_search_agent_tool, get_search_agent_tool
from chains.co2_sql import get_en_co2_sql_chain
from chains.weight_est import get_en_weight_est
from prompt_templates.main_agent import (
    DK_AGENT_PREFIX,
    DK_AGENT_SUFFIX,
    EN_AGENT_PREFIX,
    EN_AGENT_SUFFIX,
)


def get_co2_estimator_agent(language: Literal["da", "en"], verbose: bool = False, async_call: bool = False):
    math_chain = LLMMathChain.from_llm(llm=ChatOpenAI(temperature=0))  # type: ignore
    sql_chain = get_en_co2_sql_chain(language=language, verbose=verbose)
    weight_est_chain = get_en_weight_est(language=language, verbose=verbose)
    # search_chain = GoogleSerperAPIWrapper(k=10, gl="dk")

    search_tool = get_search_agent_tool(search_agent=get_co2_google_search_agent(verbose=verbose))

    tools = [
        Tool(
            name="Weight estimator",
            func=weight_est_chain.run,
            description="Useful for estimating the weight of each item by passing all ingredients at once as input.",
            coroutine=weight_est_chain.arun,
        ),
        Tool(
            name="CO2 emission estimator",
            func=sql_chain.run,
            description="""Useful for finding out the CO2 emission of each item by passing
                           all ingredients at once as input.""",
            coroutine=sql_chain.arun,
        ),
        # Tool(
        #     name="Search tool",
        #     func=search_agent.run,
        # ),
        # Tool(
        #     name="Search tool",
        #     func=search_chain.run,
        #     description="""Useful for finding out the kg CO2e / kg for an ingredient is not in the database.
        #                     Should only use if the ingredient weights more than 0.1 kg.
        #                     The search item should only be used for one ingredient at a time.""",
        #     coroutine=search_chain.arun,
        # ),
        search_tool,
        Tool(
            name="Math calculator",
            func=math_chain.run,
            description="""Useful for calculating the CO2 emission of each ingredients by kg * kg CO2e / kg.
                            You can for example ask: What is 0.1 * 1.26 + 0.2 * 0.5? 
                            Do not ask it for ingredients with unknown weight or CO2e / kg.""",
            coroutine=math_chain.arun,
        ),
    ]

    en_prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=EN_AGENT_PREFIX if language == "en" else DK_AGENT_PREFIX,
        suffix=EN_AGENT_SUFFIX if language == "en" else DK_AGENT_SUFFIX,
        input_variables=["input", "agent_scratchpad"],
    )

    llm_chain = LLMChain(
        llm=ChatOpenAI(temperature=0),  # type: ignore
        prompt=en_prompt,
    )

    tool_names = [tool.name for tool in tools]
    agent = ZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names)
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=verbose)

    return agent_executor
