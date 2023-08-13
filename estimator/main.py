import asyncio

import validators
from langdetect import detect

from estimator.agent.search_agent import get_co2_google_search_agent
from estimator.chains.co2_sql import get_co2_sql_chain
from estimator.chains.recipe_extractor import get_recipe_extractor_chain
from estimator.chains.weight_est import get_weight_estimator_chain
from estimator.prompt_templates.co2_search_prompts import search_output_parser
from estimator.prompt_templates.co2_sql_prompts import co2_output_parser
from estimator.prompt_templates.recipe_extractor_prompt import recipe_output_parser
from estimator.prompt_templates.weight_est_prompts import weight_output_parser
from estimator.utils import generate_output, get_url_text


# TO-DO: Implement better coding practices (No Exception etc.)
def estimator(
    url: str,
    verbose: bool = False,
    negligeble_threshold: float = 0.01,
):
    if validators.url(url):
        # Get URL text
        text = get_url_text(url)
    else:
        text = url

    # Extract ingredients from text
    recipe_extractor_chain = get_recipe_extractor_chain()
    ingredients = recipe_extractor_chain.run(text)
    parsed_ingredients = recipe_output_parser.parse(ingredients)
    if not parsed_ingredients:
        return "I can't find a recipe in the provided URL / text"

    # Detect language in ingredients
    language = detect(ingredients)
    if language != "en" and language != "da":
        return "Language is not recognized as Danish or English"

    try:
        # Estimate weights using weight estimator
        weight_estimator_chain = get_weight_estimator_chain(language=language, verbose=verbose)
        weight_output = weight_estimator_chain.run(ingredients)
        parsed_weight_output = weight_output_parser.parse(weight_output)
    except Exception:
        return "Something went wrong in estimating weights of ingredients."

    try:
        # Estimate the kg CO2e per kg for each weight ingredien
        co2_sql_chain = get_co2_sql_chain(language=language, verbose=verbose)
        co2_query_input = [item.ingredient for item in parsed_weight_output.weight_estimates if item.weight_in_kg is not None and item.weight_in_kg > negligeble_threshold]
        co2_query_input_str = str(co2_query_input)
        sql_output = co2_sql_chain.run(co2_query_input_str)
        parsed_sql_output = co2_output_parser.parse(sql_output)
    except Exception:
        return "Something went wrong in estimating kg CO2e per kg for the ingredients"

    # Check if any ingredients needs CO2 search
    try:
        co2_search_input_items = [item.ingredient for item in parsed_sql_output.emissions if item.co2_per_kg is None]
        search_agent = get_co2_google_search_agent(verbose=verbose)
        search_results = [search_agent.run(item) for item in co2_search_input_items]
        parsed_search_results = [search_output_parser.parse(result) for result in search_results]
    except Exception:
        print("Something went wrong when searching for kg CO2e per kg")
        parsed_search_results = []

    return generate_output(
        weight_estimates=parsed_weight_output,
        co2_emissions=parsed_sql_output,
        search_results=parsed_search_results,
        negligeble_threshold=negligeble_threshold,
    )


# TO-DO: Implement better coding practices (No Exception etc.)
async def async_estimator(
    url: str,
    verbose: bool = False,
    negligeble_threshold: float = 0.01,
):
    if validators.url(url):
        # Get URL text
        is_url = True
        text = get_url_text(url)
    else:
        text = url
        is_url = False

    # Extract ingredients from text
    recipe_extractor_chain = get_recipe_extractor_chain()
    ingredients: str = await recipe_extractor_chain.arun(text)
    if "no ingredients" in ingredients.lower():
        if is_url:
            return "I can't find a recipe in the provided URL. Try manually inserting ingredients list"
        return "Cannot find any ingredients"

    # Detect language in ingredients
    language = detect(ingredients)
    if language == "no":  # Easy mistake that should have any consequence
        language = "da"
    if language != "en" and language != "da":
        return "Language is not recognized as Danish, Norwegian or English"

    try:
        # Estimate weights using weight estimator
        weight_estimator_chain = get_weight_estimator_chain(language=language, verbose=verbose)
        weight_output = await weight_estimator_chain.arun(ingredients)
        parsed_weight_output = weight_output_parser.parse(weight_output)
    except Exception:
        return "Something went wrong in estimating weights of ingredients."

    try:
        # Estimate the kg CO2e per kg for each weight ingredien
        co2_sql_chain = get_co2_sql_chain(language=language, verbose=verbose)
        co2_query_input = [item.ingredient for item in parsed_weight_output.weight_estimates if item.weight_in_kg is not None and item.weight_in_kg > negligeble_threshold]
        co2_query_input_str = str(co2_query_input)
        sql_output = co2_sql_chain.run(
            co2_query_input_str,
        )
        parsed_sql_output = co2_output_parser.parse(sql_output)
    except Exception:
        return "Something went wrong in estimating kg CO2e per kg for the ingredients"

    # Check if any ingredients needs CO2 search
    try:
        co2_search_input_items = [item.ingredient for item in parsed_sql_output.emissions if item.co2_per_kg is None]
        search_agent = get_co2_google_search_agent(verbose=verbose)
        tasks = [search_agent.arun(q) for q in co2_search_input_items]
        search_results = await asyncio.gather(*tasks)
        parsed_search_results = [search_output_parser.parse(result) for result in search_results]
    except Exception:
        print("Something went wrong when searching for kg CO2e per kg")
        parsed_search_results = []

    return generate_output(
        weight_estimates=parsed_weight_output,
        co2_emissions=parsed_sql_output,
        search_results=parsed_search_results,
        negligeble_threshold=negligeble_threshold,
    )


if __name__ == "__main__":
    # import asyncio

    from time import time

    start_time = time()
    # url = "https://www.foodfanatic.dk/tacos-med-lynchili-og-salsa"
    url = "https://madogkaerlighed.dk/cremet-pasta-med-asparges/"
    print(estimator(url, verbose=False))
    end_time = time()
    print(f"Time elapsed: {end_time - start_time}s")

    start_time = time()
    print(asyncio.run(async_estimator(url=url, verbose=False)))
    end_time = time()
    print(f"Async time elapsed: {end_time - start_time}s")
