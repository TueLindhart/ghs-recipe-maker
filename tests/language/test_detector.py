import pytest

from food_co2_estimator.language.detector import Languages, detect_language
from food_co2_estimator.pydantic_models.recipe_extractor import (
    EnrichedIngredient,
    EnrichedRecipe,
)

# Ingredient lists
SIMPLE_ENGLISH_INGREDIENTS = ["eggplant", "cucumber"]
SIMPLE_DANISH_INGREDIENTS = ["aubergine", "agurk"]
SIMPLE_SPANISH_INGREDIENTS = ["berenjena", "pepino"]
SALT_PEPPER_INGREDIENTS = ["salt", "pepper"]
DANISH_SINGLE_WORDS = ["agurk", "gulerod", "ærter"]

# Instructions
ENGLISH_INSTRUCTIONS = "Preheat the oven to 180 degrees. Add salt and pepper."
DANISH_INSTRUCTIONS = "Forvarm ovnen til 180 grader. Tilsæt salt og peber."
SPANISH_INSTRUCTIONS = "Precalienta el horno a 180 grados. Añade sal y pimienta."
NORWEGIAN_INSTRUCTIONS = "Forvarm ovnen til 180 grader. Dette er en norsk oppskrift."
SWEDISH_INSTRUCTIONS = "Förvärm ugnen till 180 grader. Detta är ett svenskt recept."

# Long ingredient lists
DANISH_RECIPE_INGREDIENTS = [
    "500 gram torskefilet",
    "2 stk æg",
    "1 stk gulerod, fintrevet",
    "0.5 tsk revet muskatnød",
    "2 spsk olie",
    "4 dl creme fraiche (18%)",
    "4 stk æggeblomme",
    "2 spsk frisk dild, hakket",
    "4 spsk frisk persille, hakket",
]

ENGLISH_RECIPE_INGREDIENTS = [
    "500 grams cod fillet",
    "2 eggs",
    "1 carrot, finely grated",
    "0.5 tsp grated nutmeg",
    "2 tbsp oil",
    "4 dl sour cream (18%)",
    "4 egg yolks",
    "2 tbsp fresh dill, chopped",
    "4 tbsp fresh parsley, chopped",
]

SPANISH_RECIPE_INGREDIENTS = [
    "500 gramos de filete de bacalao",
    "2 huevos",
    "1 zanahoria, finamente rallada",
    "0.5 cucharadita de nuez moscada rallada",
    "2 cucharadas de aceite",
    "4 dl de crema agria (18%)",
    "4 yemas de huevo",
    "2 cucharadas de eneldo fresco, picado",
    "4 cucharadas de perejil fresco, picado",
]


@pytest.mark.parametrize(
    "recipe,expected",
    [
        (
            EnrichedRecipe(
                url="http://example.com",
                ingredients=EnrichedIngredient.from_list(SIMPLE_ENGLISH_INGREDIENTS),
                instructions=ENGLISH_INSTRUCTIONS,
                persons=2,
            ),
            Languages.English.value,
        ),
        (
            EnrichedRecipe(
                url="http://example.com",
                ingredients=EnrichedIngredient.from_list(SIMPLE_DANISH_INGREDIENTS),
                instructions=DANISH_INSTRUCTIONS,
                persons=2,
            ),
            Languages.Danish.value,
        ),
        (
            EnrichedRecipe(
                url="http://example.com",
                ingredients=EnrichedIngredient.from_list(SIMPLE_SPANISH_INGREDIENTS),
                instructions=SPANISH_INSTRUCTIONS,
                persons=2,
            ),
            None,
        ),
    ],
    ids=["English", "Danish", "Spanish"],
)
def test_language_from_instructions(recipe, expected):
    assert detect_language(recipe) == expected


# def test_empty_recipe_raises_exception():
#     recipe = EnrichedRecipe(
#         url="http://example.com",
#         ingredients=[],
#         instructions=None,
#         persons=None,
#     )
#     with pytest.raises(Exception):
#         detect_language(recipe)


# @pytest.mark.parametrize(
#     "recipe,expected",
#     [
#         (
#             EnrichedRecipe(
#                 url="http://example.com",
#                 ingredients=EnrichedIngredient.from_list(SALT_PEPPER_INGREDIENTS),
#                 instructions=NORWEGIAN_INSTRUCTIONS,
#                 persons=2,
#             ),
#             Languages.Danish,
#         ),
#         (
#             EnrichedRecipe(
#                 url="http://example.com",
#                 ingredients=EnrichedIngredient.from_list(SALT_PEPPER_INGREDIENTS),
#                 instructions=SWEDISH_INSTRUCTIONS,
#                 persons=2,
#             ),
#             Languages.Danish,
#         ),
#     ],
# )
# def test_scandinavian_languages_as_danish(recipe, expected):
#     assert detect_language(recipe) == expected


# @pytest.mark.parametrize(
#     "recipe,expected",
#     [
#         (
#             EnrichedRecipe(
#                 url="http://example.com",
#                 ingredients=EnrichedIngredient.from_list(DANISH_RECIPE_INGREDIENTS),
#                 instructions=None,
#                 persons=2,
#             ),
#             Languages.Danish,
#         ),
#         (
#             EnrichedRecipe(
#                 url="http://example.com",
#                 ingredients=EnrichedIngredient.from_list(ENGLISH_RECIPE_INGREDIENTS),
#                 instructions=None,
#                 persons=2,
#             ),
#             Languages.English,
#         ),
#         (
#             EnrichedRecipe(
#                 url="http://example.com",
#                 ingredients=EnrichedIngredient.from_list(SPANISH_RECIPE_INGREDIENTS),
#                 instructions=None,
#                 persons=2,
#             ),
#             None,
#         ),
#     ],
# )
# def test_language_from_ingredients_no_instructions(recipe, expected):
#     assert detect_language(recipe) == expected


# def test_single_word_ingredients():
#     recipe = EnrichedRecipe(
#         url="http://example.com",
#         ingredients=EnrichedIngredient.from_list(DANISH_SINGLE_WORDS),
#         instructions=None,
#         persons=2,
#     )
#     assert detect_language(recipe) == Languages.Danish
