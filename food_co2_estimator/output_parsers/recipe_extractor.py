from typing import List

from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class Recipe(BaseModel):
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


recipe_output_parser = PydanticOutputParser(pydantic_object=Recipe)
