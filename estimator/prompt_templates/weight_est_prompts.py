from langchain import PromptTemplate

DK_NEGLIGEBLE = "negligerbar"
EN_NEGLIGEBLE = "negligible"

DK_WEIGHT_EST_PROMPT = """
Given a list of ingredients in Danish, estimate the weights in kilogram for each ingredient.
Explain your reasoning for the estimation of weights and why you estimate some ingredients to be negligible.

The following recalculations can be used to estimate the weight of each ingredient:
1 dåse = 400 g
1 terning bouillon = 4 g
1 stor løg = 285 g
1 mellem løg = 170 g
1 lille løg = 115 g
1 peberfrugt = 150 g
1 dåse tomatkoncentrat = 140 g
1 spiseskefuld/spsk. = 15 g
1 teskefuld/tsk. = 5 g
1 kartoffel = 170 - 300 g
1 gulerod = 100 g
1 citron = 85 g
1 tortilla = 30 g

Ingredients that weight less than 50 gram/g or 0.050 kilogram/kg should be called 'negligerbar'.

Use the following format:
Ingredients: "Ingredients here"
Answer: "Final answer here"

Begin!

Ingredients:
1 dåse hakkede tomater
200 g pasta
500 ml vand
250 gram hakket kød
0.5 blomkål
1 tsk. sukker
1 økologisk citron
3 teskefulde salt
2 spsk. krydderi
peber
2 store kartofler

Answer:
1 dåse hakkede tomater: 1 dåse = 400 g = 0.4 kg
200 g pasta: 200 g = 0.2 kg
500 ml vand: 500 ml = 0.5 kg
250 gram hakket kød: 250 g = 0.25 kg
0.5 blomkål: 1 blomkål = 500 g (estimeret af LLM model) = 0.5 kg
1 tsk. sukker: 1 teskefuld = 5 g som er mindre end 50 g, negligerbar
1 økologisk citron: 1 citron = 85 g = 0.085 kg
3 teskefulde salt: 1 tsk. = 5 g, 3 * 5 g = 15 g = 0.015 kg som er mindre end 0.050 kg, negligerbar
2 spsk. krydderi: 1 spsk. = 15 g, 2 * 15 g = 30 g = 0.030 kg som er mindre end 0.050 kg, negligerbar
peber: antal ikke angivet, negligerbar
2 store kartofler: 1 stor kartoffel = 300 g, 2 * 300 g = 600 g = 0.6 kg

Ingredients:
{input}
"""

EN_WEIGHT_RECALCULATIONS = """
1 can = 400 g
1 cube of bouillon/stock = 4 g
1 large onion = 285 g
1 medium onion = 170 g
1 small onion = 115 g
1 pepper = 150 g
1 tin of tomato concentrate = 140 g
1 tablespoon/tbsp. = 15 g
1 teaspoon/tsp. = 5 g
1 potato = 170 - 300 g
1 carrot = 100 g
1 lemon = 60 g
"""

DK_WEIGHT_RECALCULATIONS = """
1 dåse = 400 g
1 terning bouillon = 4 g
1 stor løg = 285 g
1 mellem løg = 170 g
1 lille løg = 115 g
1 peberfrugt = 150 g
1 dåse tomatkoncentrat = 140 g
1 spiseskefuld/spsk. = 15 g
1 teskefuld/tsk. = 5 g
1 kartoffel = 170 - 300 g
1 gulerod = 100 g
1 citron = 85 g
1 tortilla = 30 g
"""

EN_INPUT_EXAMPLE = """
1 can of chopped tomatoes
2 large potatoes
1 teaspoon of sugar
200 g of pasta
500 ml of water
250 gram of minced meat
0.5 cauliflower
1 teaspoon/tsp. sugar
1 organic lemon
3 teaspoons of salt
pepper
"""

DK_INPUT_EXAMPLE = """
1 dåse hakkede tomater
200 g pasta
500 ml vand
250 gram hakket kød
0.5 blomkål
1 tsk. sukker
1 økologisk citron
3 teskefulde salt
2 spsk. krydderi
peber
2 store kartofler
"""

DK_ANSWER_EXAMPLE = """
1 dåse hakkede tomater: 1 dåse = 400 g = 0.4 kg
200 g pasta: 200 g = 0.2 kg
500 ml vand: 500 ml = 0.5 kg
250 gram hakket kød: 250 g = 0.25 kg
0.5 blomkål: 1 blomkål = 500 g (estimeret af LLM model) = 0.5 kg
1 tsk. sukker: 1 teskefuld = 5 g som er mindre end 50 g, negligerbar
1 økologisk citron: 1 citron = 85 g = 0.085 kg
3 teskefulde salt: 1 tsk. = 5 g, 3 * 5 g = 15 g = 0.015 kg som er mindre end 0.050 kg, negligerbar
2 spsk. krydderi: 1 spsk. = 15 g, 2 * 15 g = 30 g = 0.030 kg som er mindre end 0.050 kg, negligerbar
peber: antal ikke angivet, negligerbar
2 store kartofler: 1 stor kartoffel = 300 g, 2 * 300 g = 600 g = 0.6 kg
"""

EN_ANSWER_EXAMPLE = """
1 can of chopped tomatoes: 1 can = 400 g = 0.4 kg
2 large potatoes: 1 large potato = 300 g, 2 * 0.3 kg = 0.6 kg
200 g of pasta: 200 g = 0.2 kg
500 ml of water: 500 ml = 0.5 kg
250 gram of minced meat: 250 g = 0.25 kg
0.5 cauliflower: 1 cauliflower = 500 g (estimated by LLM model) = 0.5 kg
3 teaspoons of sugar: 1 tsp. = 5 g, 3 * 5 g = 15 g = 0.015 kg which is below 0.05 kg, negligible
1 organic lemon: 1 lemon = 60 g = 0.06 kg
salt: 1 tsp. = 5 g, 3 * 5 g = 15 g = 0.015 kg which is below 0.05 kg, negligible
pepper: negligible
"""

WEIGHT_EST_PROMPT = """
Given a list of ingredients, estimate the weights in kilogram for each ingredient.
Explain your reasoning for the estimation of weights and why you estimate some ingredients to be {negligible}.

The following recalculations can be used to estimate the weight of each ingredient:
{recalculations}

Ingredients that weight less than 10 gram/g or 0.01 kilogram/kg should be called '{negligible}'.

Use the following format:
Ingredients: "Ingredients here"
Answer: "Final answer here"

Begin!

Ingredients:
{input_example}


Answer:
{answer_example}

Ingredients:
{input}
"""

DK_WEIGHT_EST_PROMPT = PromptTemplate(
    template=WEIGHT_EST_PROMPT,
    input_variables=["input"],
    partial_variables={
        "negligible": DK_NEGLIGEBLE,
        "recalculations": DK_WEIGHT_RECALCULATIONS,
        "input_example": DK_INPUT_EXAMPLE,
        "answer_example": DK_ANSWER_EXAMPLE,
    },
)

EN_WEIGHT_EST_PROMPT = PromptTemplate(
    template=WEIGHT_EST_PROMPT,
    input_variables=["input"],
    partial_variables={
        "negligible": EN_NEGLIGEBLE,
        "recalculations": EN_WEIGHT_RECALCULATIONS,
        "input_example": EN_INPUT_EXAMPLE,
        "answer_example": EN_ANSWER_EXAMPLE,
    },
)
