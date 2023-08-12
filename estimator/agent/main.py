from typing import Literal

from langchain import LLMChain
from langchain.agents import AgentExecutor, Tool, ZeroShotAgent
from langchain.chat_models import ChatOpenAI
from langchain.utilities import PythonREPL

# from agent.search_agent import get_co2_google_search_agent
from estimator.agent.search_agent import get_co2_google_search_agent
from estimator.chains.co2_search import get_search_agent_tool
from estimator.chains.co2_sql import get_co2_sql_chain
from estimator.chains.weight_est import get_weight_est
from estimator.prompt_templates.main_agent import (
    AGENT_PREFIX,
    DK_AGENT_SUFFIX,
    EN_AGENT_SUFFIX,
)


def _handle_error(error) -> str:
    return f"Error: {str(error)}"[:50]


def get_co2_estimator_agent(language: Literal["da", "en"], verbose: bool = False, async_call: bool = False):
    python_repl = PythonREPL()
    sql_chain = get_co2_sql_chain(language=language, verbose=verbose)
    weight_est_chain = get_weight_est(language=language, verbose=verbose)
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
        # Tool(
        #     name="Math calculator",
        #     func=math_chain.run,
        #     description="""Useful for calculating the CO2 emission of each ingredients by kg * kg CO2e / kg.
        #                     You can for example ask: What is 0.1 * 1.26 + 0.2 * 0.5?
        #                     Do not ask it for ingredients with unknown weight or CO2e / kg.""",
        #     coroutine=math_chain.arun,
        # ),
        Tool(
            name="Python calculator",
            func=python_repl.run,
            description=""""A Python shell. Use this to execute python commands. Input should be a valid python command. 
                            If you want to see the output of a value, you should print it out with `print(...)`.
                            You can either as input parse print(x1*y1, x2*y2) or print(x1*y1 + x2*y2)""",
        ),
    ]

    prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=AGENT_PREFIX,
        suffix=EN_AGENT_SUFFIX if language == "en" else DK_AGENT_SUFFIX,
        input_variables=["input", "agent_scratchpad"],
    )

    llm_chain = LLMChain(
        llm=ChatOpenAI(temperature=0),  # type: ignore
        prompt=prompt,
    )

    tool_names = [tool.name for tool in tools]
    agent = ZeroShotAgent(
        llm_chain=llm_chain,
        allowed_tools=tool_names,
    )
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=verbose,
        # handle_parsing_errors=_handle_error,
    )

    return agent_executor
