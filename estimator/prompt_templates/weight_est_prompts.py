from langchain import PromptTemplate

DK_NEGLIGEBLE = "negligerbar"
EN_NEGLIGEBLE = "negligible"

EN_WEIGHT_RECALCULATIONS = """
1 can = 400 g = 0.4 kg
1 bouillon cube = 4 g = 0.004 kg
1 large onion = 285 g = 0.285 kg
1 medium onion = 170 g = 0.170 kg
1 small onion = 115 g = 0.115 kg
1 bell pepper = 150 g = 0.150 kg
1 can tomato paste = 140 g = 0.140 kg
1 tablespoon/tbsp. = 15 g  = 0.015 kg
1 teaspoon/tsp. = 5 g = 0.005 kg
1 potato = 170 - 300 g = 0.170 - 0.300 kg
1 carrot = 100 g = 0.100 kg
1 lemon = 85 g = 0.085 kg
1 tortilla = 30 g = 0.030 kg
1 squash = 400 g = 0.400 kg

Examples of a bunch/bnch of an ingredient - use them as a guideline:
1 bunch/bnch parsley = 50 g = 0.050 kg
1 bunch/bnch asparagus = 500 g = 0.500 kg
1 bunch of carrots = 750 g = 0.750 kg
1 bunch/bnch tomatoes = 500 g = 0.500 kg
The weights of bunches are estimated as the highest possible weight.
"""

DK_WEIGHT_RECALCULATIONS = """
1 dåse = 400 g = 0.4 kg
1 terning bouillon = 4 g = 0.004 kg
1 stor løg = 285 g = 0.285 kg
1 mellem løg = 170 g = 0.170 kg
1 lille løg = 115 g = 0.115 kg
1 peberfrugt = 150 g = 0.150 kg
1 dåse tomatkoncentrat = 140 g = 0.140 kg
1 spiseskefuld/spsk. = 15 g  = 0.015 kg
1 teskefuld/tsk. = 5 g = 0.005 kg
1 kartoffel = 170 - 300 g = 0.170 - 0.300 kg
1 gulerod = 100 g = 0.100 kg
1 citron = 85 g = 0.085 kg
1 tortilla = 30 g = 0.030 kg
1 squash = 400 g = 0.400 kg

Examples of bdt/bundt af en ingrediens - use them as a guideline:
1 bundt/bdt persille = 50 g = 0.050 kg
1 bundt/bdt asparges = 500 g = 0.500 kg
1 bundt gulerødder = 750 g = 0.750 kg
1 bundt/bdt tomater = 500 g = 0.500 kg
The weights of bdt/bundt are estimated the highest possible weight.
"""

EN_INPUT_EXAMPLE = """
1 can chopped tomatoes
200 g pasta
500 ml water
250 grams minced meat
0.5 cauliflower
1 tsp. sugar
1 organic lemon
3 teaspoons salt
2 tbsp. spices
pepper
2 large potatoes
1 bunch asparagus
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
1 bdt asparges
"""

DK_ANSWER_EXAMPLE = """
1 dåse hakkede tomater: 1 dåse = 400 g = 0.4 kg
200 g pasta: 200 g = 0.2 kg
500 ml vand: 500 ml = 0.5 kg
250 gram hakket kød: 250 g = 0.25 kg
0.5 blomkål: 1 blomkål = 500 g (estimeret af LLM model) = 0.5 kg
1 tsk. sukker: 1 teskefuld = 5 g = 0.005 kg som er mindre end 0.050 kg, negligerbar
1 økologisk citron: 1 citron = 85 g = 0.085 kg
3 teskefulde salt: 1 tsk. = 5 g, 3 * 5 g = 15 g = 0.015 kg som er mindre end 0.050 kg, negligerbar
2 spsk. krydderi: 1 spsk. = 15 g, 2 * 15 g = 30 g = 0.030 kg som er mindre end 0.050 kg, negligerbar
peber: antal ikke angivet, negligerbar
2 store kartofler: 1 stor kartoffel = 300 g, 2 * 300 g = 600 g = 0.6 kg
1 bdt asparges: 1 bdt asparges = 500 g = 0.500 kg
"""

EN_ANSWER_EXAMPLE = """
1 can chopped tomatoes: 1 can = 400 g = 0.4 kg
200 g pasta: 200 g = 0.2 kg
500 ml water: 500 ml = 0.5 kg
250 grams minced meat: 250 g = 0.25 kg
0.5 cauliflower: 1 cauliflower = 500 g (estimated by LLM model) = 0.5 kg
1 tsp. sugar: 1 teaspoon = 5 g = 0.005 kg which is less than 0.050 kg, negligible
1 organic lemon: 1 lemon = 85 g = 0.085 kg
3 teaspoons salt: 1 tsp. = 5 g, 3 * 5 g = 15 g = 0.015 kg which is less than 0.050 kg, negligible
2 tbsp. spices: 1 tbsp. = 15 g, 2 * 15 g = 30 g = 0.030 kg which is less than 0.050 kg, negligible
pepper: quantity not specified, negligible
2 large potatoes: 1 large potato = 300 g, 2 * 300 g = 600 g = 0.6 kg
1 bunch asparagus: 1 bunch asparagus = 500 g = 0.500 kg
"""

WEIGHT_EST_PROMPT = """
Given a list of ingredients, estimate the weights in kilogram for each ingredient.
Explain your reasoning for the estimation of weights and why you estimate some ingredients to be {negligible}.

The following general weights can be used for estimation:
{recalculations}

Ingredients that weight less than 10 gram/g or 0.01 kilogram/kg should be called '{negligible}'.
If an ingredient is not found in the list of general weights, try to give your best estimate
of the weight in kilogram/kg of the ingredient and say (estimated by LLM model).

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
