import pytest

from food_co2_estimator.language.detector import Languages, detect_language
from food_co2_estimator.pydantic_models.recipe_extractor import (
    EnrichedIngredient,
    EnrichedRecipe,
)


def _create_enriched_recipe(
    ingredients: list[str], instructions: str | None, persons: int | None = 2
) -> EnrichedRecipe:
    return EnrichedRecipe(
        url="http://example.com",
        ingredients=[EnrichedIngredient(original_name=ing) for ing in ingredients],
        instructions=instructions,
        persons=persons,
    )


@pytest.mark.parametrize(
    "ingredients,instructions,expected",
    [
        (
            ["eggplant", "cucumber"],
            "Preheat the oven to 180 degrees. Add salt and pepper.",
            Languages.English,
        ),
        (
            ["aubergine", "agurk"],
            "Forvarm ovnen til 180 grader. Tilsæt salt og peber.",
            Languages.Danish,
        ),
        (
            ["berenjena", "pepino"],
            "Precalienta el horno a 180 grados. Añade sal y pimienta.",
            None,
        ),
    ],
)
def test_language_from_instructions(ingredients, instructions, expected):
    recipe = _create_enriched_recipe(
        ingredients=ingredients,
        instructions=instructions,
    )
    assert detect_language(recipe) == expected


@pytest.mark.parametrize(
    "instructions,expected",
    [
        (
            "Forvarm ovnen til 180 grader. Dette er en norsk oppskrift.",
            Languages.Danish,
        ),
        (
            "Förvärm ugnen till 180 grader. Detta är ett svenskt recept.",
            Languages.Danish,
        ),
    ],
)
def test_scandinavian_languages_as_danish(instructions, expected):
    recipe = _create_enriched_recipe(
        ingredients=["salt", "pepper"],
        instructions=instructions,
    )
    assert detect_language(recipe) == expected


@pytest.mark.parametrize(
    "ingredients,expected",
    [
        (
            [
                "500 gram torskefilet",
                "2 stk æg",
                "1 stk gulerod, fintrevet",
                "0.5 tsk revet muskatnød",
                "2 spsk olie",
                "4 dl creme fraiche (18%)",
                "4 stk æggeblomme",
                "2 spsk frisk dild, hakket",
                "4 spsk frisk persille, hakket",
            ],
            Languages.Danish,
        ),
        (
            [
                "500 grams cod fillet",
                "2 eggs",
                "1 carrot, finely grated",
                "0.5 tsp grated nutmeg",
                "2 tbsp oil",
                "4 dl sour cream (18%)",
                "4 egg yolks",
                "2 tbsp fresh dill, chopped",
                "4 tbsp fresh parsley, chopped",
            ],
            Languages.English,
        ),
        (
            [
                "500 gramos de filete de bacalao",
                "2 huevos",
                "1 zanahoria, finamente rallada",
                "0.5 cucharadita de nuez moscada rallada",
                "2 cucharadas de aceite",
                "4 dl de crema agria (18%)",
                "4 yemas de huevo",
                "2 cucharadas de eneldo fresco, picado",
                "4 cucharadas de perejil fresco, picado",
            ],
            None,
        ),
    ],
)
def test_language_from_ingredients_no_instructions(ingredients, expected):
    recipe = _create_enriched_recipe(
        ingredients=ingredients,
        instructions=None,
    )
    assert detect_language(recipe) == expected


def test_empty_recipe_raises_exception():
    recipe = _create_enriched_recipe(
        ingredients=[],
        instructions=None,
        persons=None,
    )
    with pytest.raises(Exception):
        detect_language(recipe)


def test_single_word_ingredients():
    recipe = _create_enriched_recipe(
        ingredients=["agurk", "gulerod", "ærter"],
        instructions=None,
    )
    assert detect_language(recipe) == Languages.Danish
