import re

import requests
from bs4 import BeautifulSoup


def get_url_text(
    url: str, text_length: int = 1000
):  # Expand text length when it needs to estmate CO2 of cooking methods
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    html = requests.get(url, headers=headers).text
    # html = requests.get(url).text
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

    results = re.findall(r"(ingredi.*\S)", text)
    return " ".join([result[:text_length] for result in results])
