import asyncio
import re
from typing import Tuple

import validators
from langchain.schema.output_parser import OutputParserException

from food_co2_estimator.agent.search_agent import get_co2_google_search_agent
from food_co2_estimator.chains.rag_co2_estimator import rag_co2_emission_chain
from food_co2_estimator.chains.recipe_extractor import get_recipe_extractor_chain
from food_co2_estimator.chains.translator import get_translation_chain
from food_co2_estimator.chains.weight_estimator import get_weight_estimator_chain
from food_co2_estimator.language.detector import Languages, detect_language
from food_co2_estimator.output_parsers.co2_estimator import CO2Emissions
from food_co2_estimator.output_parsers.recipe_extractor import Recipe
from food_co2_estimator.output_parsers.retry_parser import get_retry_parser
from food_co2_estimator.output_parsers.search_co2_estimator import (
    search_co2_output_parser,
)
from food_co2_estimator.output_parsers.weight_estimator import (
    WeightEstimates,
    weight_output_parser,
)
from food_co2_estimator.utils import generate_output, get_url_text

NUMBER_PERSONS_REGEX = r".*\?antal=(\d+)"


async def get_co2_emissions(
    verbose: bool,
    negligeble_threshold: float,
    language: Languages,
    parsed_weight_output: WeightEstimates,
) -> CO2Emissions:
    emission_chain = rag_co2_emission_chain(verbose)
    translation_chain = get_translation_chain()
    ingredients_input = [
        item.ingredient
        for item in parsed_weight_output.weight_estimates
        if item.weight_in_kg is not None and item.weight_in_kg >= negligeble_threshold
    ]
    # Translation specific to emission chain is temporary
    emission_chain_with_translation = translation_chain | emission_chain
    parsed_rag_emissions: CO2Emissions = await emission_chain_with_translation.ainvoke(
        input={"inputs": ingredients_input, "language": language.value}
    )
    # Temporary translation needed here until all runs on english only
    for translated_emission, orig_ingredient in zip(
        parsed_rag_emissions.emissions, ingredients_input
    ):
        translated_emission.ingredient = orig_ingredient
    return parsed_rag_emissions


async def extract_recipe(text: str, url: str, is_url: bool, verbose: bool) -> Recipe:
    recipe_extractor_chain = get_recipe_extractor_chain(verbose=verbose)
    recipe: Recipe = await recipe_extractor_chain.ainvoke({"input": text})

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
    verbose: bool, recipe: Recipe, language: Languages
) -> WeightEstimates:
    weight_estimator_chain = get_weight_estimator_chain(
        language=language, verbose=verbose
    )
    output = await weight_estimator_chain.ainvoke({"input": recipe.ingredients})
    weight_output = output["text"]
    try:
        parsed_weight_output: WeightEstimates = weight_output_parser.parse(
            weight_output
        )
    except OutputParserException:
        retry_parser = get_retry_parser(weight_output_parser)
        parsed_weight_output: WeightEstimates = retry_parser.parse(weight_output)
    return parsed_weight_output


async def get_co2_search_emissions(verbose: bool, parsed_rag_emissions: CO2Emissions):
    co2_search_input_items = [
        item.ingredient
        for item in parsed_rag_emissions.emissions
        if item.co2_per_kg is None
    ]
    search_agent = get_co2_google_search_agent(verbose=verbose)
    tasks = [search_agent.ainvoke({"input": q}) for q in co2_search_input_items]
    search_results = await asyncio.gather(*tasks)
    parsed_search_results = []

    for result in search_results:
        try:
            parsed_search_results.append(
                search_co2_output_parser.parse(result["output"])
            )
        except OutputParserException:
            retry_parser = get_retry_parser(search_co2_output_parser)
            parsed_search_results.append(retry_parser.parse(result["output"]))
    return parsed_search_results


# TO-DO: Implement Runnable Interface instead and set prompttemplaces outside of model calls
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
    language = detect_language(recipe)
    if language is None:
        return (
            f"Language is not recognized as {', '.join([l.value for l in Languages])}"
        )
    try:
        # Estimate weights using weight estimator
        parsed_weight_output = await get_weight_estimates(verbose, recipe, language)
    except Exception as e:
        print(str(e))
        return "Something went wrong in estimating weights of ingredients."

    try:
        # Estimate the kg CO2e per kg for each weight ingredien
        parsed_rag_emissions = await get_co2_emissions(
            verbose,
            negligeble_threshold,
            language,
            parsed_weight_output,
        )

    except Exception as e:
        print(str(e))
        return "Something went wrong in estimating kg CO2e per kg for the ingredients"

    # Check if any ingredients needs CO2 search
    try:
        parsed_search_results = await get_co2_search_emissions(
            verbose, parsed_rag_emissions
        )
    except Exception as e:
        print(str(e))
        print("Something went wrong when searching for kg CO2e per kg")
        parsed_search_results = []

    return generate_output(
        weight_estimates=parsed_weight_output,
        co2_emissions=parsed_rag_emissions,
        search_results=parsed_search_results,
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
    url = "https://www.valdemarsro.dk/spaghetti-bolognese/"
    # url = "https://www.valdemarsro.dk/hjemmelavede-burgere/"
    # url = "https://www.valdemarsro.dk/red-thai-curry/"
    # url = """1 stk tomat
    #          1 glas oliven
    #          200 g løg
    #       """

    start_time = time()
    print(asyncio.run(async_estimator(url=url, verbose=True)))
    # estimator(url=url, verbose=True)
    end_time = time()
    print(f"Async time elapsed: {end_time - start_time}s")
