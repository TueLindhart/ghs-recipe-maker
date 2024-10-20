import asyncio
from typing import Any, Dict

import validators
from langchain.schema.output_parser import OutputParserException
from langdetect import detect

from food_co2_estimator.agent.search_agent import get_co2_google_search_agent
from food_co2_estimator.chains.recipe_extractor import get_recipe_extractor_chain
from food_co2_estimator.chains.sql_co2_estimator import get_co2_sql_chain
from food_co2_estimator.chains.weight_estimator import get_weight_estimator_chain
from food_co2_estimator.output_parsers.retry_parser import get_retry_parser
from food_co2_estimator.output_parsers.search_co2_estimator import (
    search_co2_output_parser,
)
from food_co2_estimator.output_parsers.sql_co2_estimator import sql_co2_output_parser
from food_co2_estimator.output_parsers.weight_estimator import weight_output_parser
from food_co2_estimator.utils import generate_output, get_url_text


# TO-DO: Implement Runnable Interface instead and set prompttemplaces outside of model calls
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
    output: Dict[str, Any] = await recipe_extractor_chain.ainvoke({"input": text})
    ingredients = output["text"]
    if "no ingredients" in ingredients.lower():
        if is_url:
            return "I can't find a recipe in the provided URL. Try manually inserting ingredients list"
        return "Cannot find any ingredients"

    # Detect language in ingredients
    language = detect(ingredients)
    if language in ["no", "sv"]:  # Swedish and Norwegian is easy mistakes
        language = "da"
    if language != "en" and language != "da":
        return "Language is not recognized as Danish, Norwegian, Swedish or English"

    try:
        # Estimate weights using weight estimator
        weight_estimator_chain = get_weight_estimator_chain(
            language=language, verbose=verbose
        )
        output = await weight_estimator_chain.ainvoke({"input": ingredients})
        weight_output = output["text"]
        try:
            parsed_weight_output = weight_output_parser.parse(weight_output)
        except OutputParserException:
            retry_parser = get_retry_parser(weight_output_parser)
            parsed_weight_output = retry_parser.parse(weight_output)
    except Exception as e:
        print(str(e))
        return "Something went wrong in estimating weights of ingredients."

    try:
        # Estimate the kg CO2e per kg for each weight ingredien
        co2_sql_chain = get_co2_sql_chain(language=language, verbose=verbose)
        co2_query_input = [
            item.ingredient
            for item in parsed_weight_output.weight_estimates
            if item.weight_in_kg is not None
            and item.weight_in_kg >= negligeble_threshold
            and item.ignore is False
        ]
        co2_query_input_str = str(co2_query_input)
        output = await co2_sql_chain.ainvoke(
            {"query": co2_query_input_str},
        )
        sql_result = output["result"]
        try:
            parsed_sql_output = sql_co2_output_parser.parse(sql_result)
        except OutputParserException:
            retry_parser = get_retry_parser(sql_co2_output_parser)
            parsed_sql_output = retry_parser.parse(sql_result)
    except Exception as e:
        print(str(e))
        return "Something went wrong in estimating kg CO2e per kg for the ingredients"

    # Check if any ingredients needs CO2 search
    try:
        co2_search_input_items = [
            item.ingredient
            for item in parsed_sql_output.emissions
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
    except Exception as e:
        print(str(e))
        print("Something went wrong when searching for kg CO2e per kg")
        parsed_search_results = []

    return generate_output(
        weight_estimates=parsed_weight_output,
        co2_emissions=parsed_sql_output,
        search_results=parsed_search_results,
        negligeble_threshold=negligeble_threshold,
        language=language,
    )


if __name__ == "__main__":
    # import asyncio

    from time import time

    start_time = time()
    # url = "https://www.foodfanatic.dk/tacos-med-lynchili-og-salsa"
    # url = "https://madogkaerlighed.dk/cremet-pasta-med-asparges/"
    url = "https://www.valdemarsro.dk/spaghetti-bolognese/"
    # url = """1 stk tomat
    #          1 glas oliven
    #          200 g løg
    #       """
    # print(estimator(url, verbose=False))
    # end_time = time()
    # print(f"Time elapsed: {end_time - start_time}s")

    start_time = time()
    print(asyncio.run(async_estimator(url=url, verbose=True)))
    # estimator(url=url, verbose=True)
    end_time = time()
    print(f"Async time elapsed: {end_time - start_time}s")
