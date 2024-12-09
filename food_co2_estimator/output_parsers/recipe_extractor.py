from dis import Instruction
from enum import Enum
from typing import List

from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from food_co2_estimator.output_parsers.co2_estimator import CO2Emissions, CO2perKg
from food_co2_estimator.output_parsers.weight_estimator import (
    WeightEstimate,
    WeightEstimates,
)


class ExtractedRecipe(BaseModel):
    """Class containing recipe information"""

    ingredients: List[str] = Field(
        description="This field should contain a list of ingredients in the recipe"
    )
    persons: int | None = Field(
        description="This field should contain number of persons recipe if for."
    )
    instructions: str | None = Field(
        description="This field should contain instructions for recipe."
    )


class CO2Source(Enum):
    DB = "DB"
    Search = "Search"


class EnrichedIngredient(BaseModel):
    original_name: str
    name: str | None = None
    weight_in_kg: float | None = None
    co2_per_kg: float | None = None
    co2_source: CO2Source | None = None

    def is_name_match(self, name: str) -> bool:
        return self.name == name

    def set_english_name(self, english_name: str):
        self.english_name = english_name

    def set_weight(self, weight_estimate: WeightEstimate):
        if self.name == weight_estimate.ingredient:
            self.weight_in_kg = weight_estimate.weight_in_kg

    def set_co2(self, co2_emission: CO2perKg, source: CO2Source):
        if self.name == co2_emission:
            self.co2_per_kg = co2_emission.co2_per_kg
            self.co2_source = source


class EnrichedRecipe(ExtractedRecipe):
    ingredients: list[EnrichedIngredient]

    @classmethod
    def from_extracted_recipe(
        cls,
        extracted_recipe: ExtractedRecipe,
    ) -> "EnrichedRecipe":
        return cls(
            ingredients=[
                EnrichedIngredient(original_name=ingredient)
                for ingredient in extracted_recipe.ingredients
            ],
            persons=extracted_recipe.persons,
            instructions=extracted_recipe.instructions,
        )

    def get_matched_ingredient(self, name: str):
        for ingredient in self.ingredients:
            if ingredient.name == name:
                return ingredient

    def update_with_translations(
        self, translated_ingredients: list[str], instructions: str | None
    ):

        if len(translated_ingredients) != len(self.ingredients):
            translated_ingredients = [
                ingredient.original_name for ingredient in self.ingredients
            ]

        for ingredient, translation in zip(self.ingredients, translated_ingredients):
            ingredient.set_english_name(translation)

    def update_with_weight_estimates(self, weight_estimates: WeightEstimates):
        for weight_estimate in weight_estimates.weight_estimates:
            ingredient = self.get_matched_ingredient(weight_estimate.ingredient)
            ingredient.set_weight(weight_estimate)

    # def enrich_with_weight_estimates(self,weight_estimates: WeightEstimates)
