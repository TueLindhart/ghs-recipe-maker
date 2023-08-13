from typing import Optional

from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


# Not able to incorporate at the moment
class CO2SearchResult(BaseModel):
    ingredient: str = Field("The original input string with amounts etc. provided in 'Input:'")
    explanation: str = Field(description="Explanation of how the final search result is chosen in step-by-step logic")
    unit: Optional[str] = Field(description="Unit of search result.", default=None)
    result: Optional[float] = Field(
        description="Result in kg CO2e per kg. null/None if no useable result is found",
        default=None,
    )


search_output_parser = PydanticOutputParser(pydantic_object=CO2SearchResult)


SEARCH_AGENT_PROMPT_PREFIX = """
Given an ingredient in Danish or English as input, find the kg CO2e per kg of the ingredient by using a search tool and extracting the kg CO2e per kg from the search results.

If you find multiple values then choose the most likely result based on what type of ingredient it is.

Here is some information to help you choose the most likely result:
- Vegetables are usually between 0.1 and 0.5 kg CO2e per kg.
- Fruits are usually between 0.2-0.8 kg CO2e per kg.
- Beans and lentils are usually between 0.5-2.0 kg CO2e per kg.
- Poultry (e.g., chicken) is usually between 3.0-6.0 kg CO2e per kg.
- Pork is usually between 4.0-7.0 kg CO2e per kg.
- Beef is usually between 7.0-22.0 kg CO2e per kg.
- Lamb is usually between 9.0-20.0 kg CO2e per kg.
- Dairy products are usually between 0.5-12.0 kg CO2e per kg.

If you can't estimate what value that is most likely, then provide the value closest to the median of the values.
If you cannot find the kg CO2e per kg of the ingredient, then provide the final answer 'CO2e per kg not found'.

You have access to the following tools:
"""

# SEARCH_AGENT_FORMAT_INSTRUCTIONS = """
# Use the following format:

# Input: the ingredient you must search for
# Thought: you should always think about what to do
# Action: the action to take, should be one of [{tool_names}]
# Action Input: the input to the action
# Observation: the result of the action
# ... (this Thought/Action/Action Input/Observation can repeat 1 time)
# Thought: I now know the final answer
# Final Answer: the final answer to the original input question.
# """
SEARCH_AGENT_FORMAT_INSTRUCTIONS = """
Use the following format:

Input: the ingredient you must search for
Action: the action to take, can only be {tool_names}
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat 1 time)
Thought: I now know the final answer
Final Answer: the final answer to the original input question.
"""

SEARCH_AGENT_PROMPT_SUFFIX = """

Before searching for the ingredient, remove amounts and anything else that is not useful in getting kg CO2e per kg results.
You do NOT need to use a tool for removing amount etc.
Search on the language provided.

Removal example: 150 g red lentils --> red lentils.
Search example: red lentils kg CO2e per kg.

You must extract the kg CO2e per kg from the search results.
Do not provide any ranges for the final search result. For example, do not provide '0.1-0.5 kg CO2e per kg' as the final search result.
Remember the "ingredient" key must be the original input: '{input}'.

Begin!

Input: {input}
{agent_scratchpad}
"""
