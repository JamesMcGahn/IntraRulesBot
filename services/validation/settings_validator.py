from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..auth.auth_service import AuthService

    from ..intra.intra_provider_session import IntraProviderSession
    from ..base.models import JobRequest
    from .models import (
        ValidationRequest,
        SettingsValidatePayload,
        ValidationBatchRequest,
    )

    from settings.models import SettingsFieldMeta
    from .interfaces.settings_meta_provider import SettingsMetaProvider

from PySide6.QtCore import Signal, QThread

from base import QObjectBase
from ..base.enums import JOBSTATUS
from ..base.models import JobRef, JobResponse
from ..settings.enums import FIELDSTATESTATUS
from .enums import VALIDATEJOBTYPE
from .models import (
    SettingsValidateResponse,
    ValidationResponse,
    ValidationBatchResponse,
)
from ..intra.login_worker import IntraLoginWorker


class SettingsValidationService(QObjectBase):
    task_complete = Signal(object)

    def __init__(
        self,
        settings_meta_provider: SettingsMetaProvider,
        session: IntraProviderSession,
        auth_service: AuthService,
    ):
        super().__init__()
        self.settings_meta_provider = settings_meta_provider
        self._session = session
        self._auth_service = auth_service

        self._pending_jobs = {}
        self._intra_login_thread = None

    def validate(
        self, job: JobRequest[ValidationRequest[SettingsValidatePayload]]
    ) -> JobResponse[ValidationResponse]:
        self._pending_jobs[job.id] = job

        payload = job.payload.data
        field_meta: SettingsFieldMeta = self.settings_meta_provider.get_field_meta(
            payload.category, payload.field
        )
        if not field_meta:
            self.handle_failure(
                job.id,
                payload.category,
                payload.field,
                payload.value,
                message="Field has not metadata",
            )
            return

        result = field_meta.verify(payload.field, payload.value)
        if result is None:
            self.handle_failure(
                job.id,
                payload.category,
                payload.field,
                payload.value,
                message="Field failed validation",
            )
            return

        if isinstance(result, SettingsValidateResponse):
            self.send_validation_response(job.id, result)
        else:
            raise ValueError("Invalid validator return type")

    def build_failure_payload(category, field, value, message):
        return SettingsValidateResponse(
            category=category,
            field=field,
            value=value,
            status=FIELDSTATESTATUS.INVALID,
            message=message,
        )

    def handle_failure(self, job_id, category, field, value, message):
        self._pending_jobs.pop(job_id, None)
        self.send_validation_response(
            job_id, self.build_failure_payload(category, field, value, message)
        )

    def validate_batch(
        self, job: JobRequest[ValidationBatchRequest[SettingsValidatePayload]]
    ) -> JobResponse[ValidationResponse]:
        self._pending_jobs[job.id] = job

        payload = job.payload.data
        print("payload validate", payload)
        failed = False
        async_function = None
        batch_object = {}
        for index, field in enumerate(payload):
            field_meta: SettingsFieldMeta = self.settings_meta_provider.get_field_meta(
                field.category, field.field
            )
            if index == 1:
                async_function = field_meta.async_verify_group
            if not field_meta:
                failed = True
                continue
            batch_object[field.field] = field.value
            result = field_meta.verify(field.field, field.value)
            if result is None or result.status == FIELDSTATESTATUS.INVALID:
                failed = True

        if failed:
            [
                self.handle_failure(
                    job.id,
                    field.category,
                    field.field,
                    field.value,
                    "All fields in batch must be valid",
                )
            ]

        if async_function is not None:
            async_handler = getattr(self, async_function)
            async_handler(job.id, batch_object)
        else:
            raise ValueError("Invalid validator return type")

    def send_validation_response(self, job_id, res: SettingsValidateResponse):
        job = self._pending_jobs.get(job_id)
        if not job:
            return
        job_response = JobResponse(
            job_ref=JobRef(job_id, task=None, status=JOBSTATUS.COMPLETE),
            payload=ValidationResponse(kind=VALIDATEJOBTYPE.SETTINGS, data=res),
        )
        print("emitting")
        self.task_complete.emit(job_response)
        self._pending_jobs.pop(job_id)

    def validate_intra_login(self, job_id, batch_object):
        if self._intra_login_thread and self._intra_login_thread.isRunning():
            return

        self._intra_login_thread = QThread()
        self._intra_worker = IntraLoginWorker(
            job_id, batch_object, self._session, self._auth_service, self.logger.insert
        )

        self._intra_worker.moveToThread(self._intra_login_thread)

        self._intra_login_thread.started.connect(self._intra_worker.do_work)
        self._intra_worker.done.connect(self._intra_login_thread.quit)
        self._intra_worker.done.connect(self._intra_worker.deleteLater)
        self._intra_worker.is_valid.connect(self.handle_intra_login_response)
        self._intra_login_thread.finished.connect(self._clean_up_intra_thread)
        self._intra_login_thread.start()

    def _clean_up_intra_thread(self):
        if self._intra_login_thread:
            self._intra_login_thread.deleteLater()
            self._intra_login_thread = None
            self._intra_worker = None

    def handle_intra_login_response(self, job_id: str, is_valid: bool):
        print("hey now", is_valid)
        job = self._pending_jobs.get(job_id)
        payload = job.payload.data
        response_payloads = []
        for job in payload:
            if is_valid:
                status = FIELDSTATESTATUS.VALID
                msg = f"Field {job.field } is valid."
            else:
                status = FIELDSTATESTATUS.INVALID
                msg = f"Field {job.field } is invalid."

            response_payloads.append(
                SettingsValidateResponse(
                    category=job.category,
                    field=job.field,
                    value=job.value,
                    status=status,
                    message=msg,
                ),
            )
        job_response = JobResponse(
            job_ref=JobRef(job_id, task=None, status=JOBSTATUS.COMPLETE),
            payload=ValidationBatchResponse(
                kind=VALIDATEJOBTYPE.SETTINGS, data=response_payloads
            ),
        )
        self.task_complete.emit(job_response)
        self._pending_jobs.pop(job_id)
