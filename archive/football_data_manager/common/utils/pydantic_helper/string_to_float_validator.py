"""
String to float field validator for Pydantic models.

Provides a reusable field validator that can convert string values to float,
handling common edge cases and validation scenarios for API responses.
"""

from typing import Any
from pydantic import field_validator


def string_to_float_validator(*field_names: str):
    """
    Create a field validator that converts string values to float.
    
    This validator handles cases where APIs return numeric values as strings,
    which would normally fail validation in strict mode. It safely converts
    strings to floats while preserving actual float values and handling edge cases.
    
    :param field_names: Names of fields to apply the validator to
    :returns: Field validator function that can be used as a decorator
    
    Usage:
        class MyModel(BaseModel):
            value1: float = 0.0
            value2: float = 0.0
            
            # Apply to specific fields
            _convert_to_float = string_to_float_validator("value1", "value2")
            
        # OR for single field:
        class MyModel(BaseModel):
            value: float = 0.0
            
            @field_validator("value", mode="before")
            @classmethod
            def convert_value_to_float(cls, v):
                return convert_string_to_float(v)
    """
    def validator_func(cls, v: Any) -> float:
        """Convert string or numeric value to float."""
        return convert_string_to_float(v)
    
    return field_validator(*field_names, mode="before")(validator_func)


def convert_string_to_float(value: Any) -> float:
    """
    Convert a value to float, handling string inputs gracefully.
    
    Safely converts string representations of numbers to float values,
    while preserving existing float/int values and handling edge cases.
    
    :param value: Value to convert to float
    :returns: Float representation of the value
    :raises ValueError: If the value cannot be converted to float
    
    Supported conversions:
    - String numbers: "123.45" -> 123.45
    - Integer values: 123 -> 123.0
    - Float values: 123.45 -> 123.45 (unchanged)
    - Empty/whitespace strings: "" -> 0.0
    - None values: None -> 0.0
    """
    # Handle None values
    if value is None:
        return 0.0
    
    # If already a float, return as-is
    if isinstance(value, float):
        return value
    
    # If an integer, convert to float
    if isinstance(value, int):
        return float(value)
    
    # Handle string values
    if isinstance(value, str):
        # Handle empty or whitespace-only strings
        value = value.strip()
        if not value:
            return 0.0
        
        try:
            return float(value)
        except ValueError as e:
            raise ValueError(f"Cannot convert '{value}' to float") from e
    
    # Try to convert other types
    try:
        return float(value)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Cannot convert {type(value).__name__} '{value}' to float") from e