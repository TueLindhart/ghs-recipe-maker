from langdetect import detect

from agent import get_co2_estimator_agent
from chains.recipe_extractor import get_recipe_extractor_chain
from utils import get_url_text


def estimator(url: str, verbose: bool = False):
    # Get URL text
    text = get_url_text(url)

    # Detect language in text
    language = detect(text)
    if language not in ["da", "en"]:
        return "Language in link is not recognized as Danish or English"

    # Extract ingredients from text
    recipe_extractor_chain = get_recipe_extractor_chain()
    ingredients = recipe_extractor_chain.run(text)
    if "I can't find a recipe" in ingredients:
        return "I can't find a recipe in the provided URL"

    # Get agent and use it to estimate CO2 emission
    agent_executor = get_co2_estimator_agent(language=language, verbose=verbose)
    co2_estimate = agent_executor.run(ingredients)

    return co2_estimate


async def async_estimator(url: str, verbose: bool = False):
    # Get URL text
    text = get_url_text(url)

    # Detect language in text
    language = detect(text)
    if language not in ["da", "en"]:
        return "Language in link is not recognized as Danish or English"

    # Extract ingredients from text
    recipe_extractor_chain = get_recipe_extractor_chain()
    ingredients = await recipe_extractor_chain.arun(text)
    if "I can't find a recipe" in ingredients:
        return "I can't find a recipe in the provided URL"

    # Get agent and use it to estimate CO2 emission
    agent_executor = get_co2_estimator_agent(language=language, verbose=verbose)
    co2_estimate = await agent_executor.arun(ingredients)

    return co2_estimate


if __name__ == "__main__":
    # import asyncio

    from time import time

    start_time = time()
    url = "https://www.foodfanatic.dk/tacos-med-lynchili-og-salsa"
    print(estimator(url, verbose=False))
    end_time = time()

    print(f"Time elapsed: {end_time - start_time}s")
