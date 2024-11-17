from typing import Any, List, TypedDict

from translate import Translator


class MyTranslator:

    def __init__(self, translator: Any | None = None):
        if translator is None:
            translator = Translator(to_lang="en", from_lang="da")

        self.translator = translator

    def translate(self, text: str) -> str:
        return self.translator.translate(text)


class TranslateDict(TypedDict):
    inputs: List[str]
    language: str


def _translate_if_danish(inputs: List[str], language: str):
    translator = MyTranslator()
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
