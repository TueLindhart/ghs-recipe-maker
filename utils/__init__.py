import asyncio
import re

import requests
from bs4 import BeautifulSoup
from langchain.agents import AgentExecutor
from langchain.tools import tool


def get_url_text(url: str, text_length: int = 1000):  # Expand text length when it needs to estmate CO2 of cooking methods
    html = requests.get(url).text
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = " ".join(chunk for chunk in chunks if chunk)

    # Should make this more robust
    text = text.lower()
    # from_ingredients_idx_da = text.find("ingredienser")
    # if from_ingredients_idx_da != -1:
    #     to_idx = from_ingredients_idx_da + 2000
    #     return text[from_ingredients_idx_da:to_idx]

    # from_ingredients_idx_en = text.find("ingredients")
    # if from_ingredients_idx_en != -1:
    #     to_idx = from_ingredients_idx_en + 2000
    #     return text[from_ingredients_idx_en:to_idx]

    # return text[:text_length]

    results = re.findall(r"(ingredi.*\S)", text)
    return " ".join([result[:text_length] for result in results])


async def async_search_item(search_agent: AgentExecutor, input: str):
    return await search_agent.arun(input)


if __name__ == "__main__":
    # url = "https://www.valdemarsro.dk/blinis-med-stenbiderrogn/"
    url = "https://www.foodfanatic.dk/tacos-med-lynchili-og-salsa"
    print(get_url_text(url))
