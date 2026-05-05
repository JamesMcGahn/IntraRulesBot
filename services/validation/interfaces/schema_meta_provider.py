from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from jsonschema import Draft202012Validator
    from schemas.enums import SCHEMATYPE


class SchemaMetaProvider(Protocol):

    def get_validator(self, selected_schema: SCHEMATYPE) -> Draft202012Validator: ...
