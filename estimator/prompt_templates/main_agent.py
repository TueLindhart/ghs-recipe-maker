from estimator.prompt_templates.weight_est_prompts import DK_NEGLIGEBLE, EN_NEGLIGEBLE

DK_FINAL_ANSWER_FORMAT = """
'''
----------------------------------------
Total CO2e udledning: Z Total kg CO2e
----------------------------------------
Udregningsmetoden per ingrediens er: X kg CO2e / kg * Y kg = Z kg CO2e
'ingrediens 1: X1 * Y1 = Z1' OR 'negligerbar' if ingredient is negligerbar OR 'CO2e per kg ikke fundet' if CO2e per kg is not found for ingredient
'ingrediens 2: X2 * Y2 = Z2' OR 'negligerbar' if ingredient is negligerbar OR 'CO2e per kg ikke fundet' if CO2e per kg is not found for ingredient
etc.
----------------------------------------
'''
where 'ingrediens N' is the name of the ingredient, 'X' is the CO2e per kg of the ingredient, 'Y' is the weight of the ingredient and 'Z' is the CO2 emission of the ingredient.
Formatting of the final answer is not an Action but the output in the 'Final Answer'.
"""

EN_FINAL_ANSWER_FORMAT = """
----------------------------------------
Total CO2 emission: Z Total kg CO2e
----------------------------------------
The calculation method per ingredient is: X kg CO2e / kg * Y kg = Z kg CO2e
'ingredient 1: X1 * Y1 = Z1' OR 'negligeble' if ingredient is negligeble OR 'CO2e per kg ikke fundet' if CO2e per kg is not found for ingredient
'ingredient 2: X2 * Y2 = Z2' OR 'negligeble' if ingredient is negligeble OR 'CO2e per kg ikke fundet' if CO2e per kg is not found for ingredient
etc.
----------------------------------------
'''
where 'ingredient N' is the name of the ingredient, 'X' is the CO2e per kg of the ingredient, 'Y' is the weight of the ingredient and 'Z' is the CO2 emission of the ingredient.
Formatting of the final answer is not an Action but the output in the 'Final Answer'.
"""

AGENT_PREFIX = """Act as a CO2 emission calculator that understands danish and english.

Given a list of ingredients to a recipe, your job is to estimate the CO2 emission for each ingredient in kg CO2e and the recipe in total.
A question is framed as a list of ingredients where you answer the question by providing the CO2 emission of each ingredient and the total CO2 emission of the recipe.
You can not do any calculations on your own so you must use the tools provided. Therefore, you can not estimate any kg CO2e per kg of an ingredient on your own.

You have access to the following tools:"""

AGENT_SUFFIX = """

You can use all tools as many times as you want.

You solve this task by:
Step 1. Estimating the weights of the ingredients in the recipe using the weight estimation tool. This steps also defines what ingredients are {negligeble}.
Step 2. Finding the CO2 emission of each ingredient in kg CO2e per kg using the CO2 emission estimator tool. Remember querying all ingredients that are not {negligeble}.
Step 3. Step 3 is optional. Only use Search tool to get the kg CO2e per kg of a ingredient if the kg CO2e per kg is unknown/not returned in step 2 for an ingredient AND the ingredient is not {negligeble} in step 1.
        Each ingredient needs to be comma separated when given as input to the search tool.
Step 4. Calculate the CO2 emission in kg per ingredient by parsing 'print(x1 * y1, x2 * y2, ...)' to the python calculator tool
        which will give you the outputs 'z1 z2 z3 ...'. x = kg CO2e per kg and y = weight and z = emission in kg CO2.
        Only provide input to python calculator tool where both weight is not {negligeble} and CO2e per kg is known.
Step 5. Given the output from step 4, you then calculate the total CO2 emission of the recipe by parsing 'print(x1*y1 + x2*y2 + ...)' to the python calculator tool.
Step 6. Provide the final answer when you show the kg CO2 emission for each ingredient and the total CO2 emission of the recipe.

You can only use the search tool (step 3) for an ingredient if both conditions are satisfied:
- Condition 1: ingredient is NOT {negligeble} in step 1
- Condition 2: CO2e per kg is not found in step 2 for the ingredient.
Before using search tool, you need to think (in Thought section) about if the two conditions are satisfied by any ingredient.
You can use the search tool for the ingredients that satisfy both conditions.
If no ingredients meet both conditions, you are not able to use the search tool.

In the Question section, the ingredients are provided.

In step 6, when you know the CO2e emission per kilo of each ingredient and the total CO2e emission in kg,
use this template for the Final Answer;

{final_answer_format}

Begin!

Question: {{input}}
Thought: {{agent_scratchpad}}"""

DK_AGENT_SUFFIX = AGENT_SUFFIX.format(negligeble=DK_NEGLIGEBLE, final_answer_format=DK_FINAL_ANSWER_FORMAT)
EN_AGENT_SUFFIX = AGENT_SUFFIX.format(negligeble=EN_NEGLIGEBLE, final_answer_format=EN_FINAL_ANSWER_FORMAT)
