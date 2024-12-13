from enum import Enum

from langdetect import detect

from food_co2_estimator.pydantic_models.recipe_extractor import EnrichedRecipe


class Languages(Enum):
    English = "en"
    Danish = "da"
    Norwegian = "no"
    Swedish = "sv"


ALLOWED_LANGUAGE_MISTAKES = [Languages.Norwegian.value, Languages.Swedish.value]


def detect_language(recipe: EnrichedRecipe) -> Languages | None:

    language = (
        detect(recipe.instructions)
        if recipe.instructions is not None
        else detect(", ".join(recipe.get_ingredients_orig_name_list()))
    )
    if language in ALLOWED_LANGUAGE_MISTAKES:  # Swedish and Norwegian is easy mistakes
        return Languages.Danish

    if language in [lang.value for lang in Languages]:
        return Languages(language)
