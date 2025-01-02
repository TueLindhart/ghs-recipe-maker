import asyncio

from langchain_community.utilities import GoogleSerperAPIWrapper

from food_co2_estimator.retrievers.emission_retriever import clean_ingredient_list


async def batch_co2_search_retriever(ingredients: list[str]):
    search_tool = GoogleSerperAPIWrapper(k=10, gl="dk")
    cleaned_ingredients = clean_ingredient_list(ingredients)
    search_queries = [
        f"{ingredient} emission kg CO2 per kg" for ingredient in cleaned_ingredients
    ]
    search_tasks = [search_tool.arun(query) for query in search_queries]
    search_results = await asyncio.gather(*search_tasks)
    return dict(zip(ingredients, search_results))
