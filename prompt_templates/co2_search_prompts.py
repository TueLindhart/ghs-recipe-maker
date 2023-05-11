DK_SEARCH_AGENT_PREFIX = """
Given an ingredient in Danish as input, find the kg CO2e per kg of the ingredient by using a search tool and extracting the kg CO2e per kg from the search results.

If you cannot find the kg CO2e per kg of the ingredient, then provide the answer 'CO2e per kg not found'.
If multiple results are found, then provide the highest kg CO2e per kg.

You have access to the following tools:"""

DK_SEARCH_AGENT_SUFFIX = """

Use the following template for the Final Answer:
'ingredient': X 'kg CO2e per kg' OR 'CO2e per kg not found'

Begin!

Question: {input}
{agent_scratchpad}"""

EN_SEARCH_AGENT_PREFIX = """
Given ingredient in English as input, find the kg CO2e per kg of the ingredient by using a search tool and extracting the kg CO2e per kg from the search results.

If you cannot find the kg CO2e per kg of the ingredient, then provide the answer 'CO2e per kg not found'.

You have access to the following tools:"""

EN_SEARCH_AGENT_SUFFIX = """
Use the following template for the Final Answer:
'ingredient': X 'kg CO2e per kg' OR 'CO2e per kg not found'

Begin!

Question: {input}
{agent_scratchpad}"""
