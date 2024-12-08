from enum import Enum

from langdetect import detect

from food_co2_estimator.output_parsers.recipe_extractor import Recipe


class Languages(Enum):
    English = "en"
    Danish = "da"
    Norwegian = "no"
    Swedish = "sv"


ALLOWED_LANGUAGE_MISTAKES = [Languages.Norwegian.value, Languages.Swedish.value]


def detect_language(recipe: Recipe) -> Languages | None:

    language = (
        detect(recipe.instructions)
        if recipe.instructions is not None
        else detect(", ".join(recipe.ingredients))
    )
    if language in ALLOWED_LANGUAGE_MISTAKES:  # Swedish and Norwegian is easy mistakes
        return Languages.Danish

    if language in [lang.value for lang in Languages]:
        return Languages(language)
