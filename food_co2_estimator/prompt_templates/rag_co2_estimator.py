from langchain_core.prompts import ChatPromptTemplate

RAG_CO2_EMISSION_PROMPT_SYSTEM = """
You are a bot that is expert in matching a list of ingredients to the best 
emission options and returning the emissions in kg / Co2e kg provided.

You expertly follow these rules to find the best match and extrapolate logically from these rules.
1. Base best match on most generic emission option
    IF 1) the exact or nearly exact match is not available
    2) and the ingredient categorizes as a sub-category.
    Example: Lasagna sheets are form of flat pasta, so pasta is a valid choice if it is best option available.
2. Do not use final meals as best matches as we match on ingredient level. 
3. If there is multiple viable options, choose the one closest wrt.
to the amount of processing performed.
4. If there is multiple viable options with similar processes then choose the highest emission.

These are the ingredient emission options:
{context}
"""


RAG_CO2_EMISSION_PROMPT_INPUT_TEMPLATE = """
Give me emissions for this list of ingredients:
{ingredients}

Begin!
"""

RAG_CO2_EMISSION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", RAG_CO2_EMISSION_PROMPT_SYSTEM),
        ("human", RAG_CO2_EMISSION_PROMPT_INPUT_TEMPLATE),
    ]
)
