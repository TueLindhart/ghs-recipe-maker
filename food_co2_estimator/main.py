import asyncio
import functools
import inspect
import logging
import re

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
from food_co2_estimator.url.url2markdown import get_markdown_from_url
from food_co2_estimator.utils import generate_output

NUMBER_PERSONS_REGEX = r".*\?antal=(\d+)"

logger = logging.getLogger(__name__)


def log_with_url(func):
    """
    Decorator that tries to find 'url' in the call.
      1) If kwargs['url'] is present, use that.
      2) Else if kwargs['recipe'] is an EnrichedRecipe with a .url field, use that.
      3) Else use "NO_URL_FOUND".
    Logs 'Calling function...' before and 'Finished function...' after.
    """

    def _get_url(args, kwargs: dict[str, str]):
        extracted_url = kwargs.get("url", None)
        if extracted_url is not None:
            return extracted_url

        all_args = [arg for arg in args] + [value for value in kwargs.values()]
        for arg in all_args:
            if isinstance(arg, EnrichedRecipe):
                return arg.url

        return "NO_URL_FOUND"

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        # Try to get url from kwargs['url']
        extracted_url = _get_url(args, kwargs)

        logger.info("URL=%s: Calling function: %s", extracted_url, func.__name__)
        result = func(*args, **kwargs)
        logger.info("URL=%s: Finished function: %s", extracted_url, func.__name__)
        return result

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        extracted_url = _get_url(args, kwargs)
        logger.info("URL=%s: Calling function: %s", extracted_url, func.__name__)
        result = await func(*args, **kwargs)
        logger.info("URL=%s: Finished function: %s", extracted_url, func.__name__)
        return result

    # Return the async or sync wrapper depending on the original function
    if inspect.iscoroutinefunction(func):
        return async_wrapper

    return sync_wrapper


@log_with_url
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


@log_with_url
async def extract_recipe(text: str, url: str, verbose: bool) -> ExtractedRecipe:
    recipe_extractor_chain = get_recipe_extractor_chain(verbose=verbose)
    recipe: ExtractedRecipe = await recipe_extractor_chain.ainvoke({"input": text})

    # If number is provided in url, then use that instead of llm estimate
    persons = extract_person_from_url(url)
    recipe.persons = persons if isinstance(persons, int) else recipe.persons

    return recipe


def extract_person_from_url(url) -> int | None:
    match = re.match(NUMBER_PERSONS_REGEX, url)
    if match:
        return int(match.group(1))


@log_with_url
async def get_weight_estimates(
    verbose: bool, recipe: EnrichedRecipe
) -> WeightEstimates:
    weight_estimator_chain = get_weight_estimator_chain(verbose=verbose)
    weight_output: WeightEstimates = await weight_estimator_chain.ainvoke(
        {"input": recipe.get_ingredients_en_name_list()}
    )  # type: ignore

    return weight_output


@log_with_url
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


def log_expeption_message(url: str, message: str):
    logging.exception(f"URL={url}: {message}")


async def async_estimator(
    url: str,
    verbose: bool = False,
    negligeble_threshold: float = 0.01,
):
    text = get_markdown_from_url(url)
    if text is None:
        return "Unable to extraxt text from provided URL"

    # Extract ingredients from text
    recipe = await extract_recipe(text=text, url=url, verbose=verbose)
    if len(recipe.ingredients) == 0:

        no_recipe_message = "I can't find a recipe in the provided URL."
        log_expeption_message(url, no_recipe_message)
        return no_recipe_message

    # Detect language in ingredients
    enriched_recipe = EnrichedRecipe.from_extracted_recipe(url, recipe)
    language = detect_language(enriched_recipe)
    if language is None:
        language_expection = f"Language is not recognized as {', '.join([lang.value for lang in Languages])}"
        log_expeption_message(url, language_expection)
        return language_expection

    translator = get_translation_chain()
    try:

        enriched_recipe: EnrichedRecipe = await translator.ainvoke(
            {"recipe": enriched_recipe, "language": language}
        )
    except Exception as e:
        translation_expection = "Something went wrong in translating recipies."
        log_expeption_message(url, str(e))
        log_expeption_message(url, translation_expection)
        return translation_expection

    try:
        # Estimate weights using weight estimator
        parsed_weight_output = await get_weight_estimates(
            verbose,
            enriched_recipe,
        )
        enriched_recipe.update_with_weight_estimates(parsed_weight_output)
    except Exception as e:
        weight_est_exception = (
            "Something went wrong in estimating weights of ingredients."
        )
        log_expeption_message(url, str(e))
        log_expeption_message(url, weight_est_exception)
        return weight_est_exception

    try:
        # Estimate the kg CO2e per kg for each weight ingredien
        parsed_rag_emissions = await get_co2_emissions(
            verbose,
            negligeble_threshold,
            enriched_recipe,
        )
        enriched_recipe.update_with_co2_per_kg_db(parsed_rag_emissions)

    except Exception as e:
        rag_emissions_exception = (
            "Something went wrong in estimating kg CO2e per kg for the ingredients"
        )
        log_expeption_message(url, str(e))
        log_expeption_message(url, rag_emissions_exception)
        return rag_emissions_exception

    # Check if any ingredients needs CO2 search
    try:
        parsed_search_results = await get_co2_search_emissions(
            verbose, enriched_recipe, negligeble_threshold
        )
        enriched_recipe.update_with_co2_per_kg_search(parsed_search_results)
    except Exception as e:
        search_emissions_expection = (
            "Something went wrong when searching for kg CO2e per kg"
        )
        log_expeption_message(url, str(e))
        log_expeption_message(url, search_emissions_expection)

    return generate_output(
        enriched_recipe=enriched_recipe,
        negligeble_threshold=negligeble_threshold,
        number_of_persons=enriched_recipe.persons,
        language=language,
    )


if __name__ == "__main__":
    # import asyncio

    from time import time

    logging.basicConfig(level=logging.INFO)
    start_time = time()
    # url = "https://www.foodfanatic.dk/tacos-med-lynchili-og-salsa"
    # url = "https://madogkaerlighed.dk/cremet-pasta-med-asparges/"
    # url = "https://www.valdemarsro.dk/spaghetti-bolognese/"
    # url = "https://www.valdemarsro.dk/hjemmelavede-burgere/"
    # url = "https://www.valdemarsro.dk/greasy-portobello-burger-med-boenneboef/"
    # url = "https://www.valdemarsro.dk/red-thai-curry/"
    # url = "https://www.bbcgoodfood.com/recipes/best-spaghetti-bolognese-recipe"
    # url = "https://www.allrecipes.com/recipe/267703/dutch-oven-southwestern-chicken-pot-pie/"
    # url = "https://gourministeriet.dk/vores-favorit-bolognese/"
    # url = "https://hot-thai-kitchen.com/green-curry-new-2/"
    url = "https://www.arla.dk/opskrifter/nytarstorsk-bagt-torsk-med-sennepssauce/"

    start_time = time()
    print(asyncio.run(async_estimator(url=url, verbose=True)))
    # estimator(url=url, verbose=True)
    end_time = time()
    print(f"Async time elapsed: {end_time - start_time}s")
