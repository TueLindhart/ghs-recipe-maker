import asyncio
import re
from typing import Tuple

import validators

from food_co2_estimator.chains.rag_co2_estimator import rag_co2_emission_chain
from food_co2_estimator.chains.recipe_extractor import get_recipe_extractor_chain
from food_co2_estimator.chains.search_co2_estimator import get_search_co2_emission_chain
from food_co2_estimator.chains.translator import get_translation_chain
from food_co2_estimator.chains.weight_estimator import get_weight_estimator_chain
from food_co2_estimator.language.detector import Languages, detect_language
from food_co2_estimator.pydantic_models.co2_estimator import CO2Emissions
from food_co2_estimator.pydantic_models.recipe_extractor import (
    EnrichedIngredient,
    EnrichedRecipe,
    ExtractedRecipe,
)
from food_co2_estimator.pydantic_models.search_co2_estimator import CO2SearchResults
from food_co2_estimator.pydantic_models.weight_estimator import WeightEstimates
from food_co2_estimator.utils import generate_output, get_url_text

NUMBER_PERSONS_REGEX = r".*\?antal=(\d+)"


async def get_co2_emissions(
    verbose: bool,
    negligeble_threshold: float,
    recipe: EnrichedRecipe,
) -> CO2Emissions:
    emission_chain = rag_co2_emission_chain(verbose)

    ingredients_input = [
        item.en_name
        for item in recipe.ingredients
        if weight_above_negligeble_threshold(item, negligeble_threshold)
    ]

    parsed_rag_emissions: CO2Emissions = await emission_chain.ainvoke(ingredients_input)

    return parsed_rag_emissions


def weight_above_negligeble_threshold(
    item: EnrichedIngredient, negligeble_threshold: float
) -> bool:
    return (
        item.weight_estimate is not None
        and item.weight_estimate.weight_in_kg is not None
        and item.weight_estimate.weight_in_kg >= negligeble_threshold
    )


async def extract_recipe(
    text: str, url: str, is_url: bool, verbose: bool
) -> ExtractedRecipe:
    recipe_extractor_chain = get_recipe_extractor_chain(verbose=verbose)
    recipe: ExtractedRecipe = await recipe_extractor_chain.ainvoke({"input": text})

    # If number is provided in url, then use that instead of llm estimate
    if is_url:
        persons = extract_person_from_url(url)
        recipe.persons = persons if isinstance(persons, int) else recipe.persons

    return recipe


def extract_person_from_url(url) -> int | None:
    match = re.match(NUMBER_PERSONS_REGEX, url)
    if match:
        return int(match.group(1))


def get_text_from_input(url: str) -> Tuple[bool, str]:
    if validators.url(url):
        text = get_url_text(url)
        return True, text
    return False, url


async def get_weight_estimates(
    verbose: bool, recipe: EnrichedRecipe
) -> WeightEstimates:
    weight_estimator_chain = get_weight_estimator_chain(verbose=verbose)
    weight_output: WeightEstimates = await weight_estimator_chain.ainvoke(
        {"input": recipe.get_ingredients_en_name_list()}
    )  # type: ignore

    return weight_output


async def get_co2_search_emissions(
    verbose: bool,
    recipe: EnrichedRecipe,
    negligeble_threshold: float,
) -> CO2SearchResults:
    co2_search_input_items = [
        item.en_name
        for item in recipe.ingredients
        if co2_per_kg_not_found(item)
        and weight_above_negligeble_threshold(item, negligeble_threshold)
        and item.en_name is not None
    ]
    if not co2_search_input_items:
        return CO2SearchResults(search_results=[])
    search_chain = get_search_co2_emission_chain(verbose=verbose)
    search_results: CO2SearchResults = await search_chain.ainvoke(
        co2_search_input_items
    )  # type: ignore
    return search_results


def co2_per_kg_not_found(item: EnrichedIngredient):
    return item.co2_per_kg_db is None or item.co2_per_kg_db.co2_per_kg is None


async def async_estimator(
    url: str,
    verbose: bool = False,
    negligeble_threshold: float = 0.01,
):
    is_url, text = get_text_from_input(url)

    # Extract ingredients from text
    recipe = await extract_recipe(text=text, url=url, is_url=is_url, verbose=verbose)
    if len(recipe.ingredients) == 0:
        if is_url:
            return "I can't find a recipe in the provided URL. Try manually inserting ingredients list"
        return "Cannot find any ingredients"

    # Detect language in ingredients
    enriched_recipe = EnrichedRecipe.from_extracted_recipe(recipe)
    language = detect_language(enriched_recipe)
    if language is None:
        return (
            f"Language is not recognized as {', '.join([l.value for l in Languages])}"
        )

    translator = get_translation_chain()
    try:
        enriched_recipe: EnrichedRecipe = await translator.ainvoke(
            {"recipe": enriched_recipe, "language": language}
        )
    except Exception as e:
        print(str(e))
        return "Something went wrong in translating recipies."

    try:
        # Estimate weights using weight estimator
        parsed_weight_output = await get_weight_estimates(
            verbose,
            enriched_recipe,
        )
        enriched_recipe.update_with_weight_estimates(parsed_weight_output)
    except Exception as e:
        print(str(e))
        return "Something went wrong in estimating weights of ingredients."

    try:
        # Estimate the kg CO2e per kg for each weight ingredien
        parsed_rag_emissions = await get_co2_emissions(
            verbose,
            negligeble_threshold,
            enriched_recipe,
        )
        enriched_recipe.update_with_co2_per_kg_db(parsed_rag_emissions)

    except Exception as e:
        print(str(e))
        return "Something went wrong in estimating kg CO2e per kg for the ingredients"

    # Check if any ingredients needs CO2 search
    try:
        parsed_search_results = await get_co2_search_emissions(
            verbose, enriched_recipe, negligeble_threshold
        )
        enriched_recipe.update_with_co2_per_kg_search(parsed_search_results)
    except Exception as e:
        print(str(e))
        print("Something went wrong when searching for kg CO2e per kg")

    return generate_output(
        enriched_recipe=enriched_recipe,
        negligeble_threshold=negligeble_threshold,
        number_of_persons=recipe.persons,
        language=language,
    )


if __name__ == "__main__":
    # import asyncio

    from time import time

    start_time = time()
    # url = "https://www.foodfanatic.dk/tacos-med-lynchili-og-salsa"
    # url = "https://madogkaerlighed.dk/cremet-pasta-med-asparges/"
    # url = "https://www.valdemarsro.dk/spaghetti-bolognese/"
    url = "https://www.valdemarsro.dk/hjemmelavede-burgere/"
    # url = "https://www.valdemarsro.dk/red-thai-curry/"
    # url = "https://www.bbcgoodfood.com/recipes/best-spaghetti-bolognese-recipe"
    # url = "https://www.allrecipes.com/recipe/267703/dutch-oven-southwestern-chicken-pot-pie/"
    # url = "https://gourministeriet.dk/vores-favorit-bolognese/"
    # url = """1 stk tomat
    #          1 glas oliven
    #          200 g løg
    #       """

    start_time = time()
    print(asyncio.run(async_estimator(url=url, verbose=True)))
    # estimator(url=url, verbose=True)
    end_time = time()
    print(f"Async time elapsed: {end_time - start_time}s")
