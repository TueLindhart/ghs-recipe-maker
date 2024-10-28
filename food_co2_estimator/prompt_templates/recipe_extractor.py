from langchain_core.prompts import PromptTemplate

from food_co2_estimator.output_parsers.recipe_extractor import recipe_output_parser

WEBSITE_RESPONSE = """
{
    "ingredients": [
        "500 g torskefilet",
        "1 tsk havsalt",
        "2 æg",
        "1 gulerod, fintrevet",
        "0.5 dl fløde (13%)",
        "0.5 tsk revet muskatnød",
        "1 tsk peber",
        "2 spsk olie",
        "4 dl creme fraiche (18%)",
        "4 æggeblommer",
        "2 spsk frisk dild, hakket",
        "4 spsk frisk persille, hakket"
    ],
    "persons": 4,
    "instructions": "Forbered fiskefarsen ved at skære torskefileten i mindre stykker og blend den sammen med havsalt i en foodprocessor til en fin konsistens. 
    Tilsæt de to hele æg, fintrevet gulerod, fløde, muskatnød og peber. Blend igen, indtil ingredienserne er godt blandet og konsistensen er jævn. 
    Smag til med salt og peber efter behov. Forvarm ovnen til 180 grader. Smør en lille brødform eller ildfast fad med lidt olie og hæld fiskefarsen i formen. 
    Glat overfladen ud. Bag terrinen i ovnen i cirka 25-30 minutter, eller indtil den er fast og let gylden på toppen. 
    I en lille skål piskes creme fraiche sammen med æggeblommerne, hakket dild og persille. Smag til med salt og peber. 
    Opvarm forsigtigt saucen i en lille gryde over lav varme, indtil den er varm, men undgå at koge den for at undgå at æggeblommerne skiller. 
    Tag fisketerrinen ud af ovnen og lad den køle af i formen i et par minutter. Skær terrinen i skiver og anret på tallerkener. 
    Hæld den cremede sauce over eller server den ved siden af."
}
"""

RAW_TEXT_RESPONSE = """
{
    "ingredients": [
        "1 tomat",
        "2 løg",
        "200 g laks",
        "0.5 l mælk",
        "200 g kartofler"
    ],
    "persons": 2,
    "instructions": null
}
"""

NO_RECIPE_RESPONSE = """
{
    "ingredients": [],
    "persons": null,
    "instructions": null
}
"""

RECIPE_EXTRACTOR_PROMPT_TEMPLATE = """
Act as an expert in extracting recipes from text that understand danish and english.
Given an unstructured raw text containing a recipe, extract the amount of each ingredient, the number of persons and the instructions.

Sometimes, there is no recipe to be found and then you return and empty ingredients list and null in persons and instructions fields.

Sometimes the ingredients list is already provided. In that case just output the input in the format described below
and give an estimate of number of persons and provide an null as instruction response.

Example of ingredients already provided in Danish: oksemørbrad (250 g), 2 gulerødder
Example of ingredients already provided in English:
250 g cream
400 g beef tenderloin

{format_instructions}

The input/text is delimited by ####.

It is very important that you extract the number of persons (antal personer) from the text. If not able, then
instead estimate number of persons from ingredient list based on the amounts in the ingredients.

Begin!

####
dansk hovedret 12 tilberedningstid 45 minutter arbejdstid 25 minutter print bedøm denne opskrift rated 4
/ 5 based on 1 customer reviews hov! du skal være logget ind. log ind bliv medlem ingredienser (12) 1 2 3 4 5 6 7 8
antal personer: 500 gram torskefilet 1 tsk havsalt 2 stk æg 1 stk gulerod 0.5 deciliter fløde 13% 0.5 tsk revet
muskatnød 1 tsk peber 2 spsk olie 4 deciliter creme fraiche 18% 4 stk æggeblomme 2 spsk frisk dild 4 spsk frisk persille
Forbered fiskefarsen ved at skære torskefileten i mindre stykker og blend den sammen med havsalt i en foodprocessor til en fin konsistens. Tilsæt de to hele æg, fintrevet gulerod, fløde, muskatnød og peber. Blend igen, indtil ingredienserne er godt blandet og konsistensen er jævn. Smag til med salt og peber efter behov
Forvarm ovnen til 180 grader. Smør en lille brødform eller ildfast fad med lidt olie og hæld fiskefarsen i formen. Glat overfladen ud. Bag terrinen i ovnen i cirka 25-30 minutter, eller indtil den er fast og let gylden på toppen
I en lille skål piskes creme fraiche sammen med æggeblommerne, hakket dild og persille. Smag til med salt og peber. Opvarm forsigtigt saucen i en lille gryde over lav varme, indtil den er varm, men undgå at koge den for at undgå at æggeblommerne skiller
Tag fisketerrinen ud af ovnen og lad den køle af i formen i et par minutter. Skær terrinen i skiver og anret på tallerkener. Hæld den cremede sauce over eller server den ved siden af
####
{website_response}
####
1 tomat2 løg200 g laks0.5 l mælk200 g kartofler
####
{raw_text_response}
####
Det er dejligt vejr i dag. Jeg tror jeg vil gå en tur.
####
{no_recipe_response}
####
{input}
####
"""

RECIPE_EXTRACTOR_PROMPT = PromptTemplate(
    template=RECIPE_EXTRACTOR_PROMPT_TEMPLATE,
    input_variables=["input"],
    partial_variables={
        "format_instructions": recipe_output_parser.get_format_instructions(),
        "website_response": WEBSITE_RESPONSE,
        "raw_text_response": RAW_TEXT_RESPONSE,
        "no_recipe_response": NO_RECIPE_RESPONSE,
    },
)
