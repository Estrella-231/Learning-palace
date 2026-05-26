from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator


class ORMModel(BaseModel):
    """Base model with UUID -> str coercion for SQLAlchemy compatibility."""
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def coerce_uuids(cls, data: Any) -> Any:
        # data can be an ORM object (when from_attributes=True, before validator gets the ORM instance)
        if not isinstance(data, dict):
            # It's an ORM object or other non-dict; extract attribute names we care about
            # Pydantic will handle attribute extraction, but we need UUID→str conversion
            # Try to convert it to a dict
            if hasattr(data, '__dict__'):
                result = {}
                for key, val in vars(data).items():
                    if not key.startswith('_'):
                        result[key] = str(val) if isinstance(val, UUID) else val
                return result
            return data
        return {
            k: str(v) if isinstance(v, UUID) else v
            for k, v in data.items()
        }
