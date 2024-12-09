from langchain.prompts import (
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from food_co2_estimator.output_parsers.weight_estimator import (
    WeightEstimate,
    WeightEstimates,
)

# The general weight lookup table
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
1 clove garlic = 0.004 kg
1 dl / deciliter = 0.1 kg
Handful of herbs (basil, oregano etc.) = 0.025 kg

Examples of a bunch/bnch of an ingredient - use them as a guideline:
1 bunch/bnch parsley = 50 g = 0.050 kg
1 bunch/bnch asparagus = 500 g = 0.500 kg
1 bunch of carrots = 750 g = 0.750 kg
1 bunch/bnch tomatoes = 500 g = 0.500 kg
The weights of bunches are estimated as the highest possible weight.
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
1 duck, ca. 2 kg
"""

# Constructing the example using Pydantic models
ANSWER_EXAMPLE_OBJ = WeightEstimates(
    weight_estimates=[
        WeightEstimate(
            ingredient="1 can chopped tomatoes",
            weight_calculation="1 can = 400 g = 0.4 kg",
            weight_in_kg=0.4,
        ),
        WeightEstimate(
            ingredient="200 g pasta",
            weight_calculation="200 g = 0.2 kg",
            weight_in_kg=0.2,
        ),
        WeightEstimate(
            ingredient="500 ml water",
            weight_calculation="500 ml = 0.5 kg",
            weight_in_kg=0.5,
        ),
        WeightEstimate(
            ingredient="250 grams minced meat",
            weight_calculation="250 g = 0.25 kg",
            weight_in_kg=0.25,
        ),
        WeightEstimate(
            ingredient="0.5 cauliflower",
            weight_calculation="1 cauliflower = 500 g (estimated by LLM model) = 0.5 kg",
            weight_in_kg=0.5,
        ),
        WeightEstimate(
            ingredient="1 tsp. sugar",
            weight_calculation="1 teaspoon = 5 g = 0.005 kg",
            weight_in_kg=0.005,
        ),
        WeightEstimate(
            ingredient="1 organic lemon",
            weight_calculation="1 lemon = 85 g = 0.085 kg",
            weight_in_kg=0.085,
        ),
        WeightEstimate(
            ingredient="3 teaspoons salt",
            weight_calculation="1 tsp. = 5 g, 3 * 5 g = 15 g = 0.015 kg",
            weight_in_kg=0.015,
        ),
        WeightEstimate(
            ingredient="2 tbsp. spices",
            weight_calculation="1 tbsp. = 15 g, 2 * 15 g = 30 g = 0.030 kg",
            weight_in_kg=0.03,
        ),
        WeightEstimate(
            ingredient="pepper",
            weight_calculation="amount of pepper not specified",
            weight_in_kg=None,
        ),
        WeightEstimate(
            ingredient="2 large potatoes",
            weight_calculation="1 large potato = 300 g, 2 * 300 g = 600 g = 0.6 kg",
            weight_in_kg=0.6,
        ),
        WeightEstimate(
            ingredient="1 bunch asparagus",
            weight_calculation="1 bunch asparagus = 500 g = 0.500 kg",
            weight_in_kg=0.5,
        ),
        WeightEstimate(
            ingredient="1 duck, ca. 2 kg",
            weight_calculation="1 duck, ca. 2 kg = 2.0 kg",
            weight_in_kg=2.0,
        ),
    ]
)

ANSWER_EXAMPLE = ANSWER_EXAMPLE_OBJ.model_dump_json(indent=2)

WEIGHT_EST_SYSTEM_PROMPT = """
Given a list of ingredients, estimate the weights in kilogram for each ingredient.
Explain your reasoning for the estimation of weights.

The following general weights can be used for estimation:
{recalculations}

If an ingredient is not found in the list of general weights, try to give your best estimate
of the weight in kilogram/kg of the ingredient and say (estimated by LLM model).
Your estimate must always be a python float. Therefore, you must not provide any intervals.

Input is given after "Ingredients:"
"""

WEIGHT_EST_EXAMPLE_HUMAN_PROMPT = """Ingredients:
{input_example}

Answer:"""

WEIGHT_EST_EXAMPLE_AI_PROMPT = """{answer_example}"""

# Final prompt combining system, human, and AI messages.
WEIGHT_EST_PROMPT = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(WEIGHT_EST_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(WEIGHT_EST_EXAMPLE_HUMAN_PROMPT),
        AIMessagePromptTemplate.from_template(WEIGHT_EST_EXAMPLE_AI_PROMPT),
        HumanMessagePromptTemplate.from_template("Ingredients:\n{input}"),
    ],
    input_variables=["input"],
    partial_variables={
        "recalculations": EN_WEIGHT_RECALCULATIONS,
        "input_example": EN_INPUT_EXAMPLE,
        "answer_example": ANSWER_EXAMPLE,
    },
)
