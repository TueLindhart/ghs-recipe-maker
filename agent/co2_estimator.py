from langchain import GoogleSearchAPIWrapper, LLMChain, LLMMathChain, OpenAI
from langchain.agents import AgentExecutor, Tool, ZeroShotAgent
from langchain.chat_models import ChatOpenAI

from chains.co2_sql import get_en_co2_sql_chain
from chains.weight_est import get_en_weight_est
from prompt_templates.en_co2_estimator_agent import EN_AGENT_PREFIX, EN_AGENT_SUFFIX


def get_en_co2_estimator_agent():
    search_chain = GoogleSearchAPIWrapper(k=10, search_engine="google")
    math_chain = LLMMathChain(llm=ChatOpenAI(temperature=0))  # type: ignore
    sql_chain = get_en_co2_sql_chain()
    weight_est_chain = get_en_weight_est()

    tools = [
        Tool(
            name="Weight estimator",
            func=weight_est_chain.run,
            description="Useful for estimating the weight of each item by passing all ingredients at once as input.",
        ),
        Tool(
            name="CO2 emission estimator",
            func=sql_chain.run,
            description="""Useful for finding out the CO2 emission of each item by passing
                           all ingredients at once as input.""",
        ),
        Tool(
            name="Google search",
            func=search_chain.run,
            description="""Useful for finding out the kg CO2e / kg if the ingredient is not in the database.
                            Should only use if the ingredient weights more than 100 g.""",
        ),
        Tool(
            name="Math calculator",
            func=math_chain.run,
            description="""Useful for calculating the CO2 emission of each ingredients by kg * kg CO2e / kg.
                            You can for example ask: What is 0.1 * 1.26 + 0.2 * 0.5?""",
        ),
    ]

    en_prompt = ZeroShotAgent.create_prompt(
        tools, prefix=EN_AGENT_PREFIX, suffix=EN_AGENT_SUFFIX, input_variables=["input", "agent_scratchpad"]
    )

    llm_chain = LLMChain(
        llm=ChatOpenAI(temperature=0),  # type: ignore
        prompt=en_prompt,
    )

    tool_names = [tool.name for tool in tools]
    agent = ZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names)
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)

    return agent_executor
