import inspect
from functools import reduce
from typing import Any

from pydantic import BaseModel


def map_fields_from_model(
    destination_model_type: type["BaseModel"],
    source_model: "BaseModel",
    context: dict,
) -> dict:
    _default = object()
    model_data = {}
    for name, field in destination_model_type.model_fields.items():
        if (
            field.json_schema_extra
            and isinstance(field.json_schema_extra, dict)
            and (source_path := field.json_schema_extra.get("source"))
        ):
            sep = field.json_schema_extra.get("source_sep", ".") if field.json_schema_extra else "."
            value = map_from_model_field(
                source_model=source_model,
                source_path=str(source_path),
                sep=str(sep) if sep is not None else ".",
                default=_default,
            )
        elif (
            field.json_schema_extra
            and isinstance(field.json_schema_extra, dict)
            and (source_func := field.json_schema_extra.get("source_func"))
        ):
            if isinstance(source_func, str):
                source_func = getattr(destination_model_type, source_func)

            source_func_context: dict = {}

            if context and callable(source_func):
                source_func_params = inspect.signature(source_func).parameters
                source_func_context = {key: value for key, value in context.items() if key in source_func_params}

            if callable(source_func):
                value = source_func(source_model, default=field.default or _default, **source_func_context)
            else:
                value = _default
        else:
            value = getattr(source_model, name, _default)

        if value is not _default:
            model_data[name] = value

    return model_data


def map_from_model_field(
    source_model: object,
    source_path: str,
    sep: str | None = ".",
    default: Any | None = None,
) -> Any:
    return reduce(
        lambda val, key: getattr(val, key, default) if isinstance(val, object) else default,
        source_path.split(sep),
        source_model,
    )
