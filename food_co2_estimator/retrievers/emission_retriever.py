import re
from typing import List

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from food_co2_estimator.data.vector_store import get_vector_store

# List of number words to recognize spelled-out quantities
NUMBER_WORDS = [
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
]

# List of units, sorted by length in decreasing order to match longer units first
INGREDIENT_UNITS = sorted(
    [
        # Weight Units
        "kilograms",
        "milligrams",
        "kilogram",
        "milligram",
        "pounds",
        "ounces",
        "grams",
        "pound",
        "ounce",
        "gram",
        "kg",
        "mg",
        "g",
        "oz",
        "lb",
        "lbs",
        # Volume Units
        "milliliters",
        "deciliters",
        "tablespoons",
        "teaspoons",
        "milliliter",
        "deciliter",
        "tablespoon",
        "teaspoon",
        "pints",
        "quarts",
        "gallons",
        "liters",
        "litre",
        "liter",
        "cups",
        "pint",
        "quart",
        "gallon",
        "cup",
        "ml",
        "l",
        "dl",
        "tbsps",
        "tbsp",
        "tsp",
        "ltr",
        "ltrs",
        # Miscellaneous Units
        "packages",
        "bunches",
        "pinches",
        "cloves",
        "slices",
        "bottles",
        "pieces",
        "sticks",
        "bunch",
        "pinch",
        "clove",
        "slice",
        "bottle",
        "piece",
        "stick",
        "package",
        "pkg",
        "pkgs",
        "dozen",
        "jar",
        "can",
        "cm",
        "drop",
        "drops",
        # Short Units
        "t",
        "c",
    ],
    key=len,
    reverse=True,
)  # Sort units by length in decreasing order


def get_clean_regex():
    """
    Removes quantities, units, and the word 'of' from the beginning of an ingredient string.

    Returns:
        Pattern object: Compiled regular expression pattern.
    """

    # Escape any units that might have regex special characters
    escaped_units = [re.escape(unit) for unit in INGREDIENT_UNITS]

    # Join the units with '|' to create the units part of the regex
    units_pattern = r"(?:" + "|".join(escaped_units) + r")\.?"

    # Define the regex pattern
    pattern = r"""
        ^\s*                                      # Leading whitespace
        (?:                                       # Non-capturing group to match quantities and units
            (?:                                   # Non-capturing group for quantity with optional unit
                (?:
                    \d+(?:[\/\-]\d+)?             # Numbers with optional fraction or range
                    | \d*\.\d+                    # Decimal numbers
                    | \b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b  # Number words
                )
                \s*                               # Optional whitespace
                (?:{units})?                      # Optional units
                \s*                               # Optional whitespace
            )
        )+                                        # One or more quantities with optional units
        (?:of\b\s*)?                              # Optional 'of' followed by optional whitespace
    """.format(
        units=units_pattern
    )

    # Compile the regex pattern with verbose and ignore case flags
    regex = re.compile(pattern, re.IGNORECASE | re.VERBOSE)

    return regex


def get_emission_retriever(k: int = 5, **kwargs) -> VectorStoreRetriever:
    vector_store = get_vector_store()
    return vector_store.as_retriever(k=k, **kwargs)


def parse_retriever_output(documents: List[Document]):
    results = {}
    for document in documents:
        if "Total kg CO2e/kg" in document.metadata.keys():
            emission = document.metadata["Total kg CO2e/kg"]
            emission_rounded = round(float(emission), 1)
            results[document.page_content] = f"{emission_rounded} kg CO2e / kg"
    return results


def get_emission_retriever_chain(k: int = 5, **kwargs):
    retriever = get_emission_retriever(k=k, **kwargs)
    return retriever | parse_retriever_output


def batch_emission_retriever(inputs: List[str]):
    retriever_chain = get_emission_retriever_chain()
    cleaned_inputs = clean_ingredient_list(inputs)
    return dict(zip(inputs, retriever_chain.batch(cleaned_inputs)))


def remove_quantities(ingredient: str) -> str:
    """
    Removes quantities (numbers, fractions, decimals, number words) from the beginning of an ingredient string.

    Args:
        ingredient (str): The ingredient string to process.

    Returns:
        str: The ingredient string without leading quantities.
    """
    # Create a regex pattern to match quantities
    quantity_pattern = re.compile(
        r"^\s*"  # Start of string and optional whitespace
        r"(?:"  # Non-capturing group for quantities
        r"\d+(?:[\/\-]\d+)?"  # Whole number with optional fraction or range (e.g., 1, 1/2, 3-4)
        r"|\d*\.\d+"  # Decimal number (e.g., 0.5, .75)
        r"|\b(?:" + "|".join(NUMBER_WORDS) + r")\b"  # Number words (e.g., one, two)
        r")\s*",  # Optional whitespace after quantity
        re.IGNORECASE,
    )
    # Remove the quantity from the ingredient string
    return quantity_pattern.sub("", ingredient, count=1).strip()


def remove_units(ingredient: str) -> str:
    """
    Removes units from the beginning of an ingredient string.

    Args:
        ingredient (str): The ingredient string to process.

    Returns:
        str: The ingredient string without leading units.
    """
    # Escape units for regex and join them into a pattern
    escaped_units = [re.escape(unit) for unit in INGREDIENT_UNITS]
    units_pattern_str = (
        r"\b(?:" + "|".join(escaped_units) + r")\b\.?"
    )  # Units as whole words, optional period

    # Create a regex pattern to match units with optional 'of' following them
    units_pattern = re.compile(
        r"^\s*"  # Start of string and optional whitespace
        r"(?:" + units_pattern_str + r")"  # Units
        r"(?:\s+of)?"  # Optional 'of' after units
        r"\s*",  # Optional whitespace after units
        re.IGNORECASE,
    )
    # Remove the units from the ingredient string
    return units_pattern.sub("", ingredient, count=1).strip()


def clean_ingredient_list(ingredients: List[str]) -> List[str]:
    """
    Removes quantities and units from the beginning of each ingredient string in the list.

    Args:
        ingredients (List[str]): The list of ingredient strings to process.

    Returns:
        List[str]: A new list with cleaned ingredient strings.
    """
    cleaned_ingredients = []
    for ingredient in ingredients:
        # Remove quantities
        no_quantity = remove_quantities(ingredient)
        # Remove units
        no_unit = remove_units(no_quantity)
        cleaned_ingredients.append(no_unit)
    return cleaned_ingredients
