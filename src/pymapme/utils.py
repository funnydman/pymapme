import inspect
from functools import reduce
from typing import Type, Optional, Any

from pydantic import BaseModel


def map_fields_from_model(
        destination_model_type: Type['BaseModel'],
        source_model: 'BaseModel',
        context: dict,
) -> dict:
    _default = object()
    model_data = {}
    for name, field in destination_model_type.__fields__.items():
        if source_path := field.field_info.extra.get('source'):
            value = map_from_model_field(
                source_model=source_model,
                source_path=source_path,
                sep=field.field_info.extra.get('source_sep', '.'),
                default=_default,
            )
        elif source_func := field.field_info.extra.get('source_func'):
            if isinstance(source_func, str):
                source_func = getattr(destination_model_type, source_func)

            source_func_context: dict = {}

            if context:
                source_func_params = inspect.signature(source_func).parameters
                source_func_context = {
                    key: value
                    for key, value in context.items()
                    if key in source_func_params
                }

            value = source_func(source_model, default=field.default or _default, **source_func_context)
        else:
            value = getattr(source_model, name, _default)

        if value is not _default:
            model_data[name] = value

    return model_data


def map_from_model_field(
        source_model: object,
        source_path: str,
        sep: Optional[str] = '.',
        default: Optional[Any] = None,
) -> Any:
    value = reduce(
        lambda val, key: getattr(val, key, default) if isinstance(val, object) else default,
        source_path.split(sep),
        source_model,
    )
    return value
