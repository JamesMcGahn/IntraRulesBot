from dataclasses import dataclass, field
from typing import Generic, TypeVar

from ..enums import VALIDATEJOBTYPE

T = TypeVar("T")


@dataclass(frozen=True)
class ValidationBatchResponse(Generic[T]):
    kind: VALIDATEJOBTYPE
    data: list[T] = field(default_factory=list)
