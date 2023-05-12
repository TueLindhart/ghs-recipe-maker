import asyncio

from langchain.agents import AgentExecutor
from langchain.tools import tool


async def async_search_item(search_agent: AgentExecutor, input: str):
    return await search_agent.arun(input)


def search_item(search_agent: AgentExecutor, input: str):
    return search_agent.run(input)


def get_async_search_agent_tool(search_agent: AgentExecutor):
    @tool("CO2 search tool", return_direct=False)
    async def search_multiple_items(inputs: str):
        """Useful for finding out the kg CO2e / kg for ingredients. Each ingredient must be comma separated in the input."""

        tasks = [async_search_item(search_agent=search_agent, input=input) for input in inputs.split(",")]
        return await asyncio.gather(*tasks)

    return search_multiple_items


def get_search_agent_tool(search_agent: AgentExecutor):
    @tool("CO2 search tool", return_direct=False)
    def search_multiple_items(inputs: str):
        """Useful for finding out the kg CO2e / kg for ingredients. Each ingredient must be comma separated in the input."""

        results = [search_item(search_agent=search_agent, input=input) for input in inputs.split(",")]
        return results

    return search_multiple_items
