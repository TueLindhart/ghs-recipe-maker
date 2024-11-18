import re
from typing import List

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from food_co2_estimator.data.vector_store import get_vector_store

INGREDIENT_UNITS = [
    # Weight Units
    "gram",
    "grams",
    "g",
    "kilogram",
    "kilograms",
    "kg",
    "milligram",
    "milligrams",
    "mg",
    "ounce",
    "ounces",
    "oz",
    "pound",
    "pounds",
    "lb",
    "lbs",
    # Volume Units
    "milliliter",
    "milliliters",
    "ml",
    "liter",
    "liters",
    "l",
    "ltr",
    "ltrs",
    "deciliter",
    "deciliters",
    "dl",
    "teaspoon",
    "teaspoons",
    "tsp",
    "t",
    "tablespoon",
    "tablespoons",
    "tbsp",
    "tbsp.",
    "T",
    "cup",
    "cups",
    "c",
    "pint",
    "pints",
    "pt",
    "quart",
    "quarts",
    "qt",
    "gallon",
    "gallons",
    "gal",
    "drop",
    "drops",
    # Miscellaneous Units
    "pinch",
    "pinches",
    "dash",
    "dashes",
    "bunch",
    "bunches",
    "clove",
    "cloves",
    "slice",
    "slices",
    "can",
    "cans",
    "package",
    "packages",
    "pkg",
    "pkgs",
    "bottle",
    "bottles",
    "jar",
    "jars",
    "handful",
    "handfuls",
    "dozen",
    "dozens",
    "piece",
    "pieces",
    "stick",
    "sticks",
    "centimeter",
    "centimeters",
    "cm",
]


def get_clean_regex():
    """
    Removes quantities and units from the beginning of an ingredient string.

    Args:
        ingredient (str): The ingredient string to clean.

    Returns:
        str: The cleaned ingredient name.
    """

    # Escape any units that might have regex special characters
    escaped_units = [re.escape(unit) for unit in INGREDIENT_UNITS]

    # Join the units with '|' to create the units part of the regex
    units_pattern = r"\b(?:" + "|".join(escaped_units) + r")\b\.?"

    # Define the regex pattern
    pattern = r"""
        ^\s*                                      # Leading whitespace
        (?:                                       # Non-capturing group to match one or more quantities with optional units
            (?:                                   # Non-capturing group for quantity with optional unit
                (?:
                    \d+(?:[\/\-]\d+)?             # Numbers with optional fraction or range
                    | \d*\.\d+                    # Decimal numbers
                    | \b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b  # Number words
                )
                \s*?                              # Optional whitespace (or none)
                (?:{units})?                      # Optional units, possibly attached directly
                \s*                               # Optional whitespace
            )
        )+                                        # One or more quantities with optional units
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


def get_emission_retriever_chain(k: int = 10, **kwargs):
    retriever = get_emission_retriever(k=k, **kwargs)
    return retriever | parse_retriever_output


def batch_emission_retriever(inputs: List[str]):
    retriever_chain = get_emission_retriever_chain()
    cleaned_inputs = remove_quantities_from_inputs(inputs)
    return dict(zip(inputs, retriever_chain.batch(cleaned_inputs)))


def remove_quantities_from_inputs(inputs: List[str]) -> List[str]:
    cleaned_inputs = []
    clean_pattern = get_clean_regex()
    for input_ in inputs:
        cleaned_input = clean_pattern.sub("", input_).strip()
        cleaned_inputs.append(cleaned_input)
    return cleaned_inputs
