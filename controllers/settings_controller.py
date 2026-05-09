from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.settings import SettingsService
    from services.validation import ValidationService
    from services.settings.enums import SETTINGSCATEGORIES
    from services.settings.models import AppSettings
    from services.base.models import JobResponse
    from services.validation.models import ValidationResponse, SettingsValidateResponse

from uuid import uuid4

from PySide6.QtCore import Signal, Slot

from base import QObjectBase
from base.enums import UIEVENTTYPE, LOGLEVEL
from services.base.enums import JOBSTATUS

from base.events import UIEvent, ToastEvent
from services.base.models import JobRequest
from services.settings.enums import FIELDSTATESTATUS
from services.settings.events import FieldStateEvent, SettingUpdatedEvent
from services.settings.models import SettingUpdatedPayload, SettingValidatedPayload
from services.validation.enums import VALIDATEJOBTYPE
from services.validation.models import (
    SettingsValidatePayload,
    ValidationRequest,
    ValidationResponse,
    ValidationBatchRequest,
    ValidationBatchResponse,
)
from views.components.toasts.qtoast.enums import QTOASTSTATUS


class SettingsController(QObjectBase):
    verify_response_update = Signal(object)
    setting_updated = Signal(object)
    ui_event = Signal(object)

    def __init__(
        self,
        settings_service: SettingsService,
        validation_service: ValidationService,
    ):
        super().__init__()
        self.settings_service = settings_service
        self.validation_service = validation_service

        self._active_jobs: dict[str, str] = {}

        self.validation_service.task_complete.connect(self.on_validation_complete)

    def get_settings(self) -> AppSettings:
        self.settings_service.load_settings()
        return self.settings_service.get_settings()

    def get_settings_validation(self) -> dict[SETTINGSCATEGORIES, dict[str, bool]]:
        self.settings_service.load_settings()
        return self.settings_service.get_validations()

    def on_field_change(self, tab, key, value):
        self.settings_service.update_setting(
            SettingUpdatedPayload(category=tab, field=key, value=value)
        )

    def on_field_verify(self, category: SETTINGSCATEGORIES, field: str, value):
        print("controller", category, field, value)

        job_id = str(uuid4())

        payload = SettingsValidatePayload(category=category, field=field, value=value)

        job = JobRequest(
            id=job_id,
            task=None,
            payload=ValidationRequest(kind=VALIDATEJOBTYPE.SETTINGS, data=payload),
        )

        self._active_jobs[job_id] = payload
        self.validation_service.validate(job)

    def on_batch_verify(self, batch: list[tuple]):
        job_id = str(uuid4())
        payloads = []
        for item in batch:
            category, field, value = item
            payload = SettingsValidatePayload(
                category=category, field=field, value=value
            )
            payloads.append(payload)

        job = JobRequest(
            id=job_id,
            task=None,
            payload=ValidationBatchRequest(
                kind=VALIDATEJOBTYPE.SETTINGS, data=payloads
            ),
        )

        self._active_jobs[job_id] = payload
        self.validation_service.validate_batch(job)

    @Slot(object)
    def on_validation_complete(
        self,
        job_res: JobResponse[
            ValidationResponse[SettingsValidateResponse]
            | ValidationBatchResponse[SettingsValidateResponse]
        ],
    ):
        print("received")
        job_id = job_res.job_ref.id
        if job_id not in self._active_jobs:
            return

        payload = job_res.payload.data

        items = []
        if not isinstance(payload, list):
            items.append(payload)
        else:
            items = payload
        for item in items:
            category = item.category
            field = item.field
            value = item.value
            status = item.status
            message = item.message

            if status == FIELDSTATESTATUS.VALID:
                is_valid = True
            else:
                is_valid = False

            settings_validate_payload = SettingValidatedPayload(
                category=category, field=field, is_valid=is_valid
            )

            ui_event = UIEvent(
                event_type=UIEVENTTYPE.UPDATE,
                payload=FieldStateEvent(
                    category=category, field=field, status=status, message=message
                ),
            )

            if job_res.job_ref.status == JOBSTATUS.COMPLETE:
                self.settings_service.set_validated(settings_validate_payload)
                self.setting_updated.emit(
                    SettingUpdatedEvent(category=category, field=field, value=value)
                )
                self.verify_response_update.emit(ui_event)
                self.create_toast_event(status, message)
            elif job_res.job_ref.status in (JOBSTATUS.ERROR, JOBSTATUS.PARTIAL_ERROR):
                self.settings_service.set_validated(settings_validate_payload)
                self.verify_response_update.emit(ui_event)
                self.create_toast_event(status, message)
        self._active_jobs.pop(job_id)

    def create_toast_event(self, status: FIELDSTATESTATUS, msg: str):
        log_level = LOGLEVEL.INFO
        if status == FIELDSTATESTATUS.VALID:
            toast_level = QTOASTSTATUS.SUCCESS
        elif status == FIELDSTATESTATUS.INVALID:
            log_level = LOGLEVEL.ERROR
            toast_level = QTOASTSTATUS.ERROR
        elif status == FIELDSTATESTATUS.LOADING:
            toast_level = QTOASTSTATUS.INFORMATION

        toast = ToastEvent(
            message="Field Validation Update",
            title=msg,
            toast_level=toast_level,
            log_level=log_level,
        )
        event = UIEvent(UIEVENTTYPE.DISPLAY, payload=toast)
        self.ui_event.emit(event)
