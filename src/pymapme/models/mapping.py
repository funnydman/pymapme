import logging

from pydantic import BaseModel
from pydantic import ValidationError as ModelValidationError

from pymapme.exceptions import PyMapMeValidationError
from pymapme.utils import map_fields_from_model


class MappingModelMixin:
    @classmethod
    def map_from_model(  # type: ignore
        cls: type["MappingModel"],
        source_model: BaseModel,
        context: dict | None = None,
    ) -> "MappingModel":
        model_data = map_fields_from_model(cls, source_model, context or {})
        return cls(**model_data)


class MappingModel(MappingModelMixin, BaseModel):
    @classmethod
    def build_from_model(
        cls: type["MappingModel"],
        model: BaseModel,
        context: dict | None = None,
    ) -> "MappingModel":
        try:
            return cls.map_from_model(
                source_model=model,
                context=context,
            )
        except (AttributeError, TypeError) as exc:
            logging.error(
                "Failed to map model due to error. Reason: %s",
                exc,
            )
            raise PyMapMeValidationError(exc) from exc
        except ModelValidationError as exc:
            logging.error("Failed to map model due to model validation error. Reason: %s", exc)
            raise PyMapMeValidationError(exc) from exc
