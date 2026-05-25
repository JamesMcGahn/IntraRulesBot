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
    from ..logger.adapters import LogAdapter

from PySide6.QtCore import Signal

from ..lifecycle import ShutdownCoordinator
from .enums import VALIDATEJOBTYPE
from .schema_validator import SchemaValidationService
from .settings_validator import SettingsValidationService


class ValidationService(QObjectBase):
    task_complete = Signal(object)
    shut_down_requested = Signal()
    shutdown_ready = Signal(str)

    def __init__(
        self,
        settings_meta_provider: SettingsMetaProvider,
        schema_meta_provider: SchemaMetaProvider,
        session: IntraProviderSession,
        auth_service: AuthService,
        browser_session_factory: BrowserSessionFactory,
        logger: LogAdapter,
    ):
        super().__init__()
        self._logger = logger
        self.shut_down_coordinator = ShutdownCoordinator(self._logger)
        self.settings_validation = SettingsValidationService(
            settings_meta_provider=settings_meta_provider,
            session=session,
            auth_service=auth_service,
            browser_session_factory=browser_session_factory,
            logger=self._logger,
        )
        self.schema_validation = SchemaValidationService(
            schema_meta_provider=schema_meta_provider
        )

        self._validators: dict[VALIDATEJOBTYPE, BaseValidator] = {
            VALIDATEJOBTYPE.SETTINGS: self.settings_validation,
            VALIDATEJOBTYPE.SCHEMA: self.schema_validation,
        }

        self.shut_down_coordinator.register_service(
            "settings_validation", self.settings_validation
        )

        # CONNECTIONS

        self.settings_validation.task_complete.connect(self.task_complete)
        self.schema_validation.task_complete.connect(self.task_complete)

        self.shut_down_coordinator.shutdown_confirmed.connect(
            self.confirm_ready_for_shutdown
        )

    def validate(self, job: JobRequest[ValidationRequest]) -> None:
        validator = self._validators.get(job.payload.kind)

        if not validator:
            msg = f"{self.__class__.__name__}: There is not a validator registered for {job.payload.kind}"
            self._logger(msg, "ERROR")
            raise ValueError(msg)
        validator.validate(job)

    def validate_batch(self, job: JobRequest[ValidationRequest]) -> None:
        validator = self._validators.get(job.payload.kind)

        if not validator:
            msg = f"{self.__class__.__name__}: There is not a validator registered for {job.payload.kind}"
            self._logger(msg, "ERROR")
            raise ValueError(msg)
        validator.validate_batch(job)

    def request_app_shutdown(self) -> bool:
        ready_for_shutdown = self.shut_down_coordinator.request_shutdown()
        if not ready_for_shutdown:
            self._logger(
                f"{self.__class__.__name__}: Validation Services still active. Deferring app shutdown.",
                "WARN",
            )
            return False
        else:
            return True

    def confirm_ready_for_shutdown(self):
        self.shutdown_ready.emit("validation_service")
