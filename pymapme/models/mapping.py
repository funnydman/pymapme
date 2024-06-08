import logging
from typing import Type, Optional

from pydantic import (ValidationError as ModelValidationError, BaseModel)

from pymapme.exceptions import PyMapMelValidationError
from pymapme.utils import map_fields_from_model


class MappingModelMixin:
    @classmethod
    def map_from_model(  # type: ignore
            cls: Type['MappingModel'],
            source_model: BaseModel,
            context: Optional[dict] = None,
    ) -> 'MappingModel':
        model_data = map_fields_from_model(cls, source_model, context or {})
        return cls(**model_data)


class MappingModel(MappingModelMixin, BaseModel):

    @classmethod
    def build_from_model(
            cls: Type['MappingModel'],
            model: BaseModel,
            context: Optional[dict] = None,
    ) -> 'MappingModel':
        try:
            return cls.map_from_model(
                source_model=model,
                context=context,
            )
        except (AttributeError, TypeError) as exc:
            logging.error(
                'Failed to map model due to error. Reason: %s',
                exc,
            )
            raise PyMapMelValidationError(exc) from exc
        except ModelValidationError as exc:
            logging.error(
                'Failed to map model due to model validation error. Reason: %s', exc
            )
            raise PyMapMelValidationError(exc) from exc
