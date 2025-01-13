from copy import copy

import pytest

from food_co2_estimator.pydantic_models.co2_estimator import CO2Emissions, CO2perKg
from food_co2_estimator.pydantic_models.recipe_extractor import (
    EnrichedIngredient,
    EnrichedRecipe,
    ExtractedRecipe,
)
from food_co2_estimator.pydantic_models.search_co2_estimator import (
    CO2SearchResult,
    CO2SearchResults,
)
from food_co2_estimator.pydantic_models.weight_estimator import (
    WeightEstimate,
    WeightEstimates,
)


@pytest.fixture
def recipe_before_translation():
    return EnrichedRecipe(
        url="http://example.com",
        ingredients=[
            EnrichedIngredient(
                original_name="1 dåse tomater",
            ),
            EnrichedIngredient(
                original_name="2 agurker",
            ),
            EnrichedIngredient(
                original_name="1 dåse tomater",
            ),
        ],
        persons=2,
        instructions="Bland ingredienserne",
    )


@pytest.fixture
def recipe():
    return EnrichedRecipe(
        url="http://example.com",
        ingredients=[
            EnrichedIngredient(
                original_name="1 dåse tomater", en_name="1 can of tomatoes"
            ),
            EnrichedIngredient(original_name="2 agurker", en_name="2 cucumbers"),
            EnrichedIngredient(
                original_name="1 dåse tomater", en_name="1 can of tomatoes"
            ),
        ],
        persons=2,
        instructions="Mix ingredients",
    )


def test_update_with_translations(recipe_before_translation: EnrichedRecipe):
    translated_ingredients = ["1 can of tomatoes", "2 agurker", "1 can of tomatoes"]
    instructions = "Mix ingredients"

    recipe_after_translation = copy(recipe_before_translation)
    recipe_after_translation.update_with_translations(
        translated_ingredients, instructions
    )

    assert recipe_after_translation.instructions == instructions
    for idx, translated_ingredient in enumerate(translated_ingredients):
        assert (
            recipe_after_translation.ingredients[idx].en_name == translated_ingredient
        )


def test_update_with_weight_estimates(recipe: EnrichedRecipe):
    weight_estimates = WeightEstimates(
        weight_estimates=[
            WeightEstimate(
                ingredient="1 can of tomatoes",
                weight_calculation="1 dåse tomater = 200g",
                weight_in_kg=0.2,
            ),
        ]
    )

    recipe.update_with_weight_estimates(weight_estimates)
    for ingredient, weight in zip(recipe.ingredients, [0.2, None, 0.2]):
        if weight:
            assert (
                ingredient.weight_estimate is not None
                and ingredient.weight_estimate.weight_in_kg == weight
            )
        else:
            assert ingredient.weight_estimate is None


def test_update_with_co2_per_kg_db(recipe: EnrichedRecipe):
    co2_emissions = CO2Emissions(
        emissions=[
            CO2perKg(
                explanation="Matches 'tomatoes, canned' best.",
                ingredient="1 can of tomatoes",
                co2_per_kg=2.5,
                unit="kg",
            )
        ]
    )

    recipe.update_with_co2_per_kg_db(co2_emissions)

    for ingredient, co2 in zip(recipe.ingredients, [2.5, None, 2.5]):
        if co2:
            assert (
                ingredient.co2_per_kg_db is not None
                and ingredient.co2_per_kg_db.co2_per_kg == co2
            )
        else:
            assert ingredient.co2_per_kg_db is None


def test_update_with_co2_per_kg_search(recipe: EnrichedRecipe):
    search_results = CO2SearchResults(
        search_results=[
            CO2SearchResult(
                explanation="This was the best match.",
                ingredient="1 can of tomatoes",
                result=2.0,
            )
        ]
    )

    recipe.update_with_co2_per_kg_search(search_results)

    for ingredient, co2 in zip(recipe.ingredients, [2.0, None, 2.0]):
        if co2:
            assert (
                ingredient.co2_per_kg_search is not None
                and ingredient.co2_per_kg_search.result == co2
            )
        else:
            assert ingredient.co2_per_kg_search is None


def test_get_ingredients_lists(recipe: EnrichedRecipe):
    en_names = recipe.get_ingredients_en_name_list()
    orig_names = recipe.get_ingredients_orig_name_list()

    assert en_names == ["1 can of tomatoes", "2 cucumbers", "1 can of tomatoes"]
    assert orig_names == ["1 dåse tomater", "2 agurker", "1 dåse tomater"]


def test_from_extracted_recipe():
    ingredients = ["1 dåse tomater", "2 agurker", "1 dåse tomater"]
    extracted = ExtractedRecipe(
        ingredients=ingredients,
        persons=2,
        instructions="Mix ingredients",
    )

    enriched = EnrichedRecipe.from_extracted_recipe(
        url="http://example.com", extracted_recipe=extracted
    )

    assert enriched.url == "http://example.com"
    assert len(enriched.ingredients) == 3
    assert enriched.persons == 2
    assert enriched.instructions == "Mix ingredients"
    for idx, expected in enumerate(ingredients):
        assert enriched.ingredients[idx].original_name == expected
