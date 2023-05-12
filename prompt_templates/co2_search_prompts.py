SEARCH_AGENT_PREFIX = """
Given an ingredient in Danish or English as input, find the kg CO2e per kg of the ingredient by using a search tool and extracting the kg CO2e per kg from the search results.

If you cannot find the kg CO2e per kg of the ingredient, then provide the answer 'CO2e per kg not found'.
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

You have access to the following tools:"""

SEARCH_AGENT_SUFFIX = """

You must search for '{input} kg CO2e per kg' and extract the kg CO2e per kg from the search results.
Before providing the final answer, explain how you arrived at the answer step by step.
Do not provide any ranges for the final answer. For example, do not provide '0.1-0.5 kg CO2e per kg' as the final answer.

Use the following template for the "Final Answer":
'ingredient': X 'kg CO2e per kg' OR 'CO2e per kg not found' (Explanation of how you found the answer)

Begin!

Question: {input}
{agent_scratchpad}"""
