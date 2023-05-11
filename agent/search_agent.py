from typing import Literal

from langchain import GoogleSearchAPIWrapper, LLMChain
from langchain.agents import AgentExecutor, Tool, ZeroShotAgent
from langchain.chat_models import ChatOpenAI

from prompt_templates.co2_search_prompts import (
    DK_SEARCH_AGENT_PREFIX,
    DK_SEARCH_AGENT_SUFFIX,
    EN_SEARCH_AGENT_PREFIX,
    EN_SEARCH_AGENT_SUFFIX,
)


def get_co2_google_search_agent(language: Literal["da", "en"], verbose: bool = False):
    search_chain = GoogleSearchAPIWrapper(k=10, search_engine="google")

    tools = [
        Tool(
            name="Search tool",
            func=search_chain.run,
            description="""Useful for finding out the kg CO2e / kg for an ingredient.""",
        ),
    ]

    en_prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=EN_SEARCH_AGENT_PREFIX if language == "en" else DK_SEARCH_AGENT_PREFIX,
        suffix=EN_SEARCH_AGENT_SUFFIX if language == "en" else DK_SEARCH_AGENT_SUFFIX,
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
