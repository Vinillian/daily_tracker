from typing import List, Optional
from pydantic import Field
from .base import SerializableModel


class StateCategory(SerializableModel):
    """State category model"""
    name: str = Field(..., description="Category name")
    type: str = Field("percent", description="Input type: percent, scale_1_10, text, yes_no")
    emoji: str = Field("⚪", description="Category emoji")
    color: str = Field("#808080", description="Color in HEX")
    description: str = Field("", description="Category description")
    order: int = Field(0, description="Display order")


class StateValue(SerializableModel):
    """State value for specific category"""
    category: str = Field(..., description="Category name")
    value: str = Field("", description="Value")
    value_type: str = Field("text", description="Value type")


class DayState(SerializableModel):
    """Day state model"""
    values: List[StateValue] = Field(default_factory=list, alias="значения")

    def get_value(self, category_name: str) -> Optional[str]:
        """Get value by category name"""
        for state_value in self.values:
            if state_value.category == category_name:
                return state_value.value
        return None

    def set_value(self, category_name: str, value: str, value_type: str):
        """Set value for category"""
        for state_value in self.values:
            if state_value.category == category_name:
                state_value.value = value
                state_value.value_type = value_type
                return

        # If category doesn't exist, add new one
        self.values.append(StateValue(
            category=category_name,
            value=value,
            value_type=value_type
        ))