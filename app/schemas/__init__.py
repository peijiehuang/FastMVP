import re

from pydantic import BaseModel, ConfigDict


def to_camel(name: str) -> str:
    """Convert snake_case to camelCase.  e.g. user_name -> userName"""
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class CamelModel(BaseModel):
    """Base schema that accepts both camelCase and snake_case field names."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
