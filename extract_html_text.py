# from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup

# url = "https://www.valdemarsro.dk/spaghetti-bolognese/"
# url = "https://www.arla.dk/opskrifter/kartoffelsuppe-med-porrer/"
# url = "https://www.louisesmadblog.dk/kartoffel-porresuppe/"
url = "https://www.valdemarsro.dk/cheesecake/"
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
text = "\n".join(chunk for chunk in chunks if chunk)

# from_ingredients_idx = text.lower().rfind(r"(ingredi.\S*)")
text = text.lower()
from_ingredients_idx = text.lower().find("ingredienser")
if from_ingredients_idx == -1:
    print(text)
else:
    to_ingredients_idx = from_ingredients_idx + 2000
    ingredients = text[from_ingredients_idx:to_ingredients_idx]
    print(ingredients)
