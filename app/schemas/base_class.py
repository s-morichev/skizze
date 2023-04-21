from typing import Any, Callable

import orjson
from pydantic import BaseModel


def orjson_dumps(
    dump_value: Any, *, default: Callable[[Any], Any] | None
) -> str:
    return orjson.dumps(dump_value, default=default).decode()


class BaseSchema(BaseModel):
    class Config(object):
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        allow_population_by_field_name = True
