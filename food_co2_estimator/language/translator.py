import logging
import os
from copy import deepcopy
from enum import Enum
from typing import List, Protocol, TypedDict

from deep_translator import GoogleTranslator
from translate import Translator

from food_co2_estimator.language.detector import Languages
from food_co2_estimator.pydantic_models.recipe_extractor import EnrichedRecipe

# Global cache to keep track of the translator index
_translation_cache = {"index": 0}


class Translatable(Protocol):
    def translate(self, text: str) -> str: ...


class TranslationProviders(Enum):
    MyMemory = "mymemory"
    Microsft = "microsoft"
    DeepL = "deepl"
    Libre = "libre"


SPLIT_STRING = "; "
N_RETRIES = 2
INSTRUCTIONS_DELIMITER = " \\ "


class MyTranslator:
    def __init__(
        self,
        translators: List[Translatable],
    ):
        if not translators:
            raise ValueError("No translators provided")
        self.translators = translators
        self.current_translator = self.translators[0]  # Default to the first translator

    @classmethod
    def default(
        cls,
        from_lang: Languages = Languages.Danish,
        to_lang: Languages = Languages.English,
    ) -> "MyTranslator":
        return cls(
            translators=cls.create_translators(from_lang=from_lang, to_lang=to_lang)
        )

    @staticmethod
    def create_translators(
        from_lang: Languages = Languages.Danish,
        to_lang: Languages = Languages.English,
    ) -> List[Translatable]:
        return [
            GoogleTranslator(
                source=from_lang.value,
                target=to_lang.value,
            ),
            Translator(
                from_lang=from_lang.value,
                to_lang=to_lang.value,
                provider=TranslationProviders.MyMemory.value,
                email=os.getenv("MY_MAIL", None),
            ),
        ]

    def translate(self, text: str) -> str:
        return self.current_translator.translate(text)

    def switch_translator(self, index: int):
        self.current_translator = self.translators[index % len(self.translators)]


class TranslateDict(TypedDict):
    recipe: EnrichedRecipe
    language: str


def extract_translated_recipe(translation: str, recipe: EnrichedRecipe):

    if recipe.instructions is not None:
        ingredients_str, instructions = translation.split(INSTRUCTIONS_DELIMITER)
    else:
        ingredients_str = translation
        instructions = None

    ingredients = ingredients_str.split(SPLIT_STRING)
    recipe = deepcopy(recipe)
    recipe.update_with_translations(ingredients, instructions)
    return recipe


def _translate_if_not_english(recipe: EnrichedRecipe, language: str):
    if language == "en":
        recipe.update_with_translations(
            translated_ingredients=recipe.get_ingredients_orig_name_list(),
            instructions=recipe.instructions,
        )
        return recipe

    inputs_str = SPLIT_STRING.join(
        [ingredient.original_name for ingredient in recipe.ingredients]
    )
    if recipe.instructions is not None:
        inputs_str += INSTRUCTIONS_DELIMITER + recipe.instructions
    my_translator = MyTranslator.default()

    # Retrieve the current index from the global cache
    index = _translation_cache.get("index", 0)
    my_translator.switch_translator(index)

    for tries in range(N_RETRIES):
        translation = my_translator.translate(inputs_str)
        translated_recipe = extract_translated_recipe(translation, recipe)

        if len(recipe.ingredients) == len(translated_recipe.ingredients):
            return translated_recipe

        logging.warning(
            f"Translation failed. Trying other provider. Retry {tries + 1}/{N_RETRIES}"
        )
        # Update the index and switch the translator
        index = (index + 1) % len(my_translator.translators)
        _translation_cache["index"] = index
        my_translator.switch_translator(index)

    return translated_recipe


def translate_if_not_english(input: TranslateDict):
    return _translate_if_not_english(recipe=input["recipe"], language=input["language"])
