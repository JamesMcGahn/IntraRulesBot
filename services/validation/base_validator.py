from __future__ import annotations

from typing import TYPE_CHECKING

from base import QObjectBase

if TYPE_CHECKING:
    from ..base.models import JobRequest, JobResponse

    from .models import ValidationRequest, ValidationResponse


class BaseValidator(QObjectBase):

    def __init__(self):
        super().__init__()

    def validate(
        self, job: JobRequest[ValidationRequest]
    ) -> JobResponse[ValidationResponse]:
        raise NotImplementedError
