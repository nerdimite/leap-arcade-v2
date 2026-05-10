"""Domain type definitions.

Internal Pydantic DTOs used between the DAO and service layers.
API request/response shapes live in ``leap.api.schema``.
"""

from pydantic import BaseModel, ConfigDict


class BaseLeapModel(BaseModel):
    """Base model for all internal domain types.

    - extra fields are ignored (safe when DB adds new columns before code deploys)
    - from_attributes=True so SQLAlchemy ORM objects can be passed directly
    """

    model_config = ConfigDict(extra="ignore", from_attributes=True)
