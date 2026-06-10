from __future__ import annotations

from typing import TYPE_CHECKING

from base import QObjectBase

if TYPE_CHECKING:
    from ..base.models import JobRequest, JobResponse
    from services.logger.adapters import LogAdapter
    from .models import ValidationRequest, ValidationResponse


class BaseValidator(QObjectBase):

    def __init__(self, logger: LogAdapter):
        super().__init__(logger)

    def validate(
        self, job: JobRequest[ValidationRequest]
    ) -> JobResponse[ValidationResponse]:
        raise NotImplementedError

    def validate_batch(
        self, job: JobRequest[ValidationRequest]
    ) -> JobResponse[ValidationResponse]:
        raise NotImplementedError
