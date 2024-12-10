from typing import List

from pydantic import BaseModel, Field

from food_co2_estimator.output_parsers.co2_estimator import CO2Emissions, CO2perKg
from food_co2_estimator.output_parsers.search_co2_estimator import CO2SearchResult
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


class EnrichedIngredient(BaseModel):
    original_name: str
    en_name: str | None = None
    weight_estimate: WeightEstimate | None = None
    co2_per_kg_db: CO2perKg | None = None
    co2_per_kg_search: CO2SearchResult | None = None

    def is_name_match(self, name: str) -> bool:
        return self.en_name == name

    def set_english_name(self, english_name: str):
        self.en_name = english_name

    def set_weight_estimate(self, weight_estimate: WeightEstimate):
        if self.en_name == weight_estimate.ingredient:
            self.weight_estimate = weight_estimate

    def set_co2_per_kg_db(self, co2_per_kg: CO2perKg):
        if self.en_name == co2_per_kg.ingredient:
            self.co2_per_kg_db = co2_per_kg

    def set_co2_per_kg_search(self, co2_per_kg_search: CO2SearchResult):
        if self.en_name == co2_per_kg_search.ingredient:
            self.co2_per_kg_search = co2_per_kg_search


class EnrichedRecipe(ExtractedRecipe):
    ingredients: list[EnrichedIngredient]

    def get_ingredients_en_name_list(self) -> list[str | None]:
        return [ingredient.en_name for ingredient in self.ingredients]

    def get_ingredients_orig_name_list(self) -> list[str]:
        return [ingredient.original_name for ingredient in self.ingredients]

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

    def get_match_object(self, obj: WeightEstimate | CO2perKg | CO2SearchResult):
        for ingredient in self.ingredients:
            if ingredient.en_name == obj.ingredient:
                return ingredient

    def update_with_translations(
        self, translated_ingredients: list[str], instructions: str | None
    ):

        self.instructions = instructions

        if len(translated_ingredients) != len(self.ingredients):
            translated_ingredients = [
                ingredient.original_name for ingredient in self.ingredients
            ]

        for ingredient, translation in zip(self.ingredients, translated_ingredients):
            ingredient.set_english_name(translation)

    def update_with_weight_estimates(self, weight_estimates: WeightEstimates):
        for weight_estimate in weight_estimates.weight_estimates:
            ingredient = self.get_match_object(weight_estimate)
            if ingredient is not None:
                ingredient.set_weight_estimate(weight_estimate)

    def update_with_co2_per_kg_db(self, co2_emissions: CO2Emissions):
        for co2_per_kg in co2_emissions.emissions:
            ingredient = self.get_match_object(co2_per_kg)
            if ingredient is not None:
                ingredient.set_co2_per_kg_db(co2_per_kg)

    def update_with_co2_per_kg_search(self, co2_emissions: list[CO2SearchResult]):
        for co2_per_kg in co2_emissions:
            ingredient = self.get_match_object(co2_per_kg)
            if ingredient is not None:
                ingredient.set_co2_per_kg_search(co2_per_kg)
