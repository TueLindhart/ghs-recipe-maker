from typing import List, TypedDict

from translate import Translator


class TranslateDict(TypedDict):
    inputs: List[str]
    language: str


def _translate_if_danish(inputs: List[str], language: str):
    translator = Translator(to_lang="en", from_lang="da")
    if language == "en":
        return inputs

    inputs_str = "; ".join(inputs)
    translations = translator.translate(inputs_str)
    translation_list = translations.split("; ")
    if len(inputs) != len(translation_list):
        raise ValueError("Input and translations length are not equal")
    return translation_list


def translate_if_danish(input: TranslateDict):
    return _translate_if_danish(inputs=input["inputs"], language=input["language"])
