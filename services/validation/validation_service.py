from __future__ import annotations

from typing import TYPE_CHECKING

from base import QObjectBase

if TYPE_CHECKING:
    from ..base.models import JobRequest
    from .models import ValidationRequest
    from .base_validator import BaseValidator
    from .interfaces.settings_meta_provider import SettingsMetaProvider
    from .interfaces.schema_meta_provider import SchemaMetaProvider
    from ..auth.auth_service import AuthService
    from ..intra.intra_provider_session import IntraProviderSession
    from ..browser import BrowserSessionFactory

from PySide6.QtCore import Signal

from .enums import VALIDATEJOBTYPE
from .settings_validator import SettingsValidationService
from .schema_validator import SchemaValidationService


class ValidationService(QObjectBase):
    task_complete = Signal(object)

    def __init__(
        self,
        settings_meta_provider: SettingsMetaProvider,
        schema_meta_provider: SchemaMetaProvider,
        session: IntraProviderSession,
        auth_service: AuthService,
        browser_session_factory: BrowserSessionFactory,
    ):
        super().__init__()

        self.settings_validation = SettingsValidationService(
            settings_meta_provider=settings_meta_provider,
            session=session,
            auth_service=auth_service,
            browser_session_factory=browser_session_factory,
        )
        self.schema_validation = SchemaValidationService(
            schema_meta_provider=schema_meta_provider
        )

        self._validators: dict[VALIDATEJOBTYPE, BaseValidator] = {
            VALIDATEJOBTYPE.SETTINGS: self.settings_validation,
            VALIDATEJOBTYPE.SCHEMA: self.schema_validation,
        }

        self.settings_validation.task_complete.connect(self.task_complete)
        self.schema_validation.task_complete.connect(self.task_complete)

    def validate(self, job: JobRequest[ValidationRequest]) -> None:
        validator = self._validators.get(job.payload.kind)

        if not validator:
            msg = f"There is not a validator registered for {job.payload.kind}"
            self.logging(msg, "ERROR")
            raise ValueError(msg)
        validator.validate(job)

    def validate_batch(self, job: JobRequest[ValidationRequest]) -> None:
        validator = self._validators.get(job.payload.kind)

        if not validator:
            msg = f"There is not a validator registered for {job.payload.kind}"
            self.logging(msg, "ERROR")
            raise ValueError(msg)
        validator.validate_batch(job)
