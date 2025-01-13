from typing import List

from pydantic import BaseModel, Field

from food_co2_estimator.pydantic_models.co2_estimator import CO2Emissions, CO2perKg
from food_co2_estimator.pydantic_models.search_co2_estimator import (
    CO2SearchResult,
    CO2SearchResults,
)
from food_co2_estimator.pydantic_models.weight_estimator import (
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

    @classmethod
    def from_list(cls, ingredients: list[str]) -> List["EnrichedIngredient"]:
        return [cls(original_name=ingredient) for ingredient in ingredients]

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
    url: str
    ingredients: list[EnrichedIngredient]

    def get_ingredients_en_name_list(self) -> list[str | None]:
        return [ingredient.en_name for ingredient in self.ingredients]

    def get_ingredients_orig_name_list(self) -> list[str]:
        return [ingredient.original_name for ingredient in self.ingredients]

    @classmethod
    def from_extracted_recipe(
        cls,
        url,
        extracted_recipe: ExtractedRecipe,
    ) -> "EnrichedRecipe":
        return cls(
            url=url,
            ingredients=EnrichedIngredient.from_list(extracted_recipe.ingredients),
            persons=extracted_recipe.persons,
            instructions=extracted_recipe.instructions,
        )

    def get_match_objects(
        self, obj: WeightEstimate | CO2perKg | CO2SearchResult
    ) -> list[EnrichedIngredient]:
        matched_ingredients = []
        for ingredient in self.ingredients:
            if ingredient.en_name == obj.ingredient:
                matched_ingredients.append(ingredient)
        return matched_ingredients

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
            ingredients = self.get_match_objects(weight_estimate)
            for ingredient in ingredients:
                ingredient.set_weight_estimate(weight_estimate)

    def update_with_co2_per_kg_db(self, co2_emissions: CO2Emissions):
        for co2_per_kg in co2_emissions.emissions:
            ingredients = self.get_match_objects(co2_per_kg)
            for ingredient in ingredients:
                ingredient.set_co2_per_kg_db(co2_per_kg)

    def update_with_co2_per_kg_search(self, co2_emissions: CO2SearchResults):
        for co2_per_kg in co2_emissions.search_results:
            ingredients = self.get_match_objects(co2_per_kg)
            for ingredient in ingredients:
                ingredient.set_co2_per_kg_search(co2_per_kg)
