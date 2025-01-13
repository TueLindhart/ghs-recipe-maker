from typing import List, Optional

from pydantic import BaseModel, Field


class CO2perKg(BaseModel):
    explanation: str = Field(
        description="Comment about result. For instance what closest result is."
    )
    ingredient: str = Field(description="Name of ingredient")
    unit: str = Field(description="The unit which is kg CO2e per kg")
    co2_per_kg: Optional[float] = Field(
        description="kg CO2 per kg for ingredient", default=None
    )


class CO2Emissions(BaseModel):
    emissions: List[CO2perKg]
