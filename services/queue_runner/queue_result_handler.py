from __future__ import annotations

from typing import Callable


from base.enums import INTRAVERSION

from .enums import (
    QUEUEEXECSTATUS,
    QUEUERUNSTATUS,
    QRESULTACTION,
    QRECOVERYACTION,
)
from .models import (
    QueueExecutionResult,
    QueueRunItem,
)
from services.queues.enums import QUEUEACTION
from .models import QueueResultDecision


class QueueResultHandler:

    def __init__(
        self,
        logging: Callable[[str, str, bool], None],
        send_result_progress: Callable[
            [QueueRunItem, QueueExecutionResult, str, bool], None
        ],
        platform_version: INTRAVERSION,
    ):
        self._logging = logging
        self._send_result_progress = send_result_progress
        self._platform_version = platform_version
        self._consecutive_execution_errors = 0

    def handle_result(
        self,
        item: QueueRunItem,
        result: QueueExecutionResult,
        run_position: int,
        total_count: int,
    ) -> QueueResultDecision:
        self._logging(
            f"({run_position}/{total_count}) - Recieved result for Row: {item.queue.row_number} - {item.queue.queue_name}"
        )
        if result.success:
            return self._handle_result_success(item, result, run_position, total_count)

        if self._consecutive_execution_errors > 6:
            # NOTE Fails actually on 8
            return self._handle_result_consecutive_execution_errors(
                item, result, run_position, total_count
            )

        self._consecutive_execution_errors += 1

        match result.status:
            case QUEUEEXECSTATUS.RUNNER_STOPPED_ERROR:
                return self._handle_result_runner_stopped(
                    item, result, run_position, total_count
                )
            case QUEUEEXECSTATUS.NAME_EXISTS_ERROR:
                item.is_duplicate = True
                if INTRAVERSION.V11 == self._platform_version:
                    self._logging(
                        f"({run_position}/{total_count}) - Queue Already Exists: {item.queue.row_number} - {item.queue.queue_name}"
                    )
                    return self._handle_result_success(
                        item, result, run_position, total_count
                    )
                else:
                    return self._handle_result_queue_exists(
                        item, result, run_position, total_count
                    )
            case QUEUEEXECSTATUS.QUEUE_NOT_FOUND_ERROR:
                if INTRAVERSION.V11 == self._platform_version:
                    if item.action_type == QUEUEACTION.DELETE:
                        self._logging(
                            f"({run_position}/{total_count}) - Queue Already Does Not Exist: {item.queue.row_number} - {item.queue.queue_name}"
                        )
                        return self._handle_result_success(
                            item, result, run_position, total_count
                        )
                    if item.action_type == QUEUEACTION.ADD:
                        return self._handle_requeue_retry(
                            item, result, run_position, total_count
                        )

                return self._handle_result_queue_not_found(
                    item, result, run_position, total_count
                )

            case QUEUEEXECSTATUS.QUEUE_FOUND_ERROR:
                return self._handle_requeue_retry(
                    item, result, run_position, total_count
                )

            case QUEUEEXECSTATUS.BROWSER_ERROR:
                return self._handle_browser_result_retry(
                    item, result, run_position, total_count
                )
            case QUEUEEXECSTATUS.TIMEOUT_ERROR:
                if INTRAVERSION.V11 == self._platform_version:
                    return self._handle_requeue_retry(
                        item, result, run_position, total_count
                    )
                else:
                    return self._handle_browser_result_retry(
                        item, result, run_position, total_count
                    )

            case QUEUEEXECSTATUS.UNKNOWN_ERROR:
                if INTRAVERSION.V11 == self._platform_version:
                    return self._handle_network_result_retry(
                        item, result, run_position, total_count
                    )
                else:
                    return self._handle_browser_result_retry(
                        item, result, run_position, total_count
                    )

            case QUEUEEXECSTATUS.NETWORK_RETRYABLE_ERROR:
                return self._handle_requeue_retry(
                    item, result, run_position, total_count
                )
            case QUEUEEXECSTATUS.NOT_AUTHENTICATED:
                return self._handle_network_result_retry(
                    item, result, run_position, total_count
                )
            case QUEUEEXECSTATUS.NETWORK_RESPONSE_ERROR:
                return self._handle_result_failure(
                    item, result, run_position, total_count
                )
            case _:
                return self._handle_result_failure(
                    item, result, run_position, total_count
                )

    def _handle_result_success(
        self,
        item: QueueRunItem,
        result: QueueExecutionResult,
        run_position: int,
        total_count: int,
    ) -> QueueResultDecision:
        self._consecutive_execution_errors = 0
        self._logging(
            f"({run_position}/{total_count}) - SUCCESS - Row: {item.queue.row_number} - {item.queue.queue_name} - succeeded."
        )
        item.status = QUEUERUNSTATUS.SUCCESS
        self._send_result_progress(item, result, "Succeeded", use_exec_status=False)
        return QueueResultDecision(QRESULTACTION.SUCCESS, QRECOVERYACTION.NONE)

    def _handle_result_runner_stopped(
        self,
        item: QueueRunItem,
        result: QueueExecutionResult,
        run_position: int,
        total_count: int,
    ) -> QueueResultDecision:
        item.status = QUEUERUNSTATUS.STOPPED
        self._send_result_progress(item, result, "Stop Requested", use_exec_status=True)
        self._logging("Queue Executor stopped.", "WARN")
        return QueueResultDecision(QRESULTACTION.STOP, QRECOVERYACTION.NONE)

    def _handle_result_consecutive_execution_errors(
        self,
        item: QueueRunItem,
        result: QueueExecutionResult,
        run_position: int,
        total_count: int,
    ) -> QueueResultDecision:
        item.status = QUEUERUNSTATUS.FAILED
        self._send_result_progress(
            item, result, "Too many errors in a row.", use_exec_status=True
        )
        self._logging("Queue Executor stopped. Too many errors in a row.", "WARN")
        return QueueResultDecision(QRESULTACTION.ABORT_RUN, QRECOVERYACTION.NONE)

    def _handle_result_queue_not_found(
        self,
        item: QueueRunItem,
        result: QueueExecutionResult,
        run_position: int,
        total_count: int,
    ) -> QueueResultDecision:
        if item.retry_count >= 2 or item.action_type not in (
            QUEUEACTION.VERIFY_NOT_EXISTS,
            QUEUEACTION.DELETE,
        ):
            return self._handle_result_failure(item, result, run_position, total_count)

        self._logging(
            f"({run_position}/{total_count}) - FAILED - Row: {item.queue.row_number} - {item.queue.queue_name} - Queue Does NOT Exist Already."
        )

        self._send_result_progress(
            item,
            result,
            "Queue Name Does NOT Exist Already.",
            use_exec_status=False,
        )

        item.retry_count += 1
        item.status = QUEUERUNSTATUS.RETRYING
        item.action_type = QUEUEACTION.VERIFY_NOT_EXISTS
        self._send_result_progress(
            item,
            result,
            "Verifying Queue Actually Does Not Exist",
            use_exec_status=False,
        )

        self._logging(
            f"({run_position}/{total_count}) - adding queue item back to queue for validation."
        )
        self._logging(
            f"({run_position}/{total_count}) - VALIDATING (ATTEMPT: {item.retry_count}) - Row: {item.queue.row_number} - {item.queue.queue_name}"
        )
        return QueueResultDecision(QRESULTACTION.RETRY, QRECOVERYACTION.NONE)

    def _handle_result_queue_exists(
        self,
        item: QueueRunItem,
        result: QueueExecutionResult,
        run_position: int,
        total_count: int,
    ) -> QueueResultDecision:
        if item.retry_count >= 2:
            return self._handle_result_failure(item, result, run_position, total_count)
        self._logging(
            f"({run_position}/{total_count}) - FAILED - Row: {item.queue.row_number} - {item.queue.queue_name} - Queue Exists."
        )
        self._send_result_progress(
            item,
            result,
            "Queue Name Exists Already.",
            use_exec_status=False,
        )
        item.retry_count += 1
        item.status = QUEUERUNSTATUS.RETRYING
        item.action_type = QUEUEACTION.VERIFY_EXISTS

        self._send_result_progress(
            item, result, "Verifying Queue Actually Exists", use_exec_status=False
        )
        self._logging(
            f"({run_position}/{total_count}) - adding queue item back to queue for validation."
        )

        self._logging(
            f"({run_position}/{total_count}) - VALIDATING (ATTEMPT: {item.retry_count}) - Row: {item.queue.row_number} - {item.queue.queue_name}"
        )
        return QueueResultDecision(QRESULTACTION.RETRY, QRECOVERYACTION.NONE)

    def _handle_browser_result_retry(
        self,
        item: QueueRunItem,
        result: QueueExecutionResult,
        run_position: int,
        total_count: int,
    ) -> QueueResultDecision:
        if item.retry_count >= 2:
            return self._handle_result_failure(item, result, run_position, total_count)
        self._logging(
            f"({run_position}/{total_count}) - FAILED - Row: {item.queue.row_number} - {item.queue.queue_name} - failed."
        )
        item.retry_count += 1
        item.status = QUEUERUNSTATUS.RETRYING
        self._logging(
            f"({run_position}/{total_count}) - RETRYING (ATTEMPT: {item.retry_count}) - Row: {item.queue.row_number} - {item.queue.queue_name} - failed."
        )
        self._send_result_progress(item, result, "Retrying...", use_exec_status=False)
        return QueueResultDecision(QRESULTACTION.RETRY, QRECOVERYACTION.REBUILD_BROWSER)

    def _handle_network_result_retry(
        self,
        item: QueueRunItem,
        result: QueueExecutionResult,
        run_position: int,
        total_count: int,
    ) -> QueueResultDecision:
        if item.retry_count >= 2:
            return self._handle_result_failure(item, result, run_position, total_count)
        self._logging(
            f"({run_position}/{total_count}) - FAILED - Row: {item.queue.row_number} - {item.queue.queue_name} - failed."
        )
        item.retry_count += 1
        item.status = QUEUERUNSTATUS.RETRYING
        self._logging(
            f"({run_position}/{total_count}) - RETRYING (ATTEMPT: {item.retry_count}) - Row: {item.queue.row_number} - {item.queue.queue_name} - failed."
        )
        self._send_result_progress(item, result, "Retrying...", use_exec_status=False)
        return QueueResultDecision(QRESULTACTION.RETRY, QRECOVERYACTION.AUTHENTICATE)

    def _handle_requeue_retry(
        self,
        item: QueueRunItem,
        result: QueueExecutionResult,
        run_position: int,
        total_count: int,
    ) -> QueueResultDecision:
        if item.retry_count >= 2:
            return self._handle_result_failure(item, result, run_position, total_count)
        self._logging(
            f"({run_position}/{total_count}) - FAILED - Row: {item.queue.row_number} - {item.queue.queue_name} - failed."
        )
        item.retry_count += 1
        item.status = QUEUERUNSTATUS.RETRYING
        self._logging(
            f"({run_position}/{total_count}) - RETRYING (ATTEMPT: {item.retry_count}) - Row: {item.queue.row_number} - {item.queue.queue_name} - failed."
        )
        self._send_result_progress(item, result, "Retrying...", use_exec_status=False)
        return QueueResultDecision(QRESULTACTION.RETRY, QRECOVERYACTION.NONE)

    def _handle_result_failure(
        self,
        item: QueueRunItem,
        result: QueueExecutionResult,
        run_position: int,
        total_count: int,
    ) -> QueueResultDecision:
        self._logging(
            f"({run_position}/{total_count}) - FAILED - Row: {item.queue.row_number} - {item.queue.queue_name} - not retrying running queue."
        )
        item.status = QUEUERUNSTATUS.FAILED
        self._send_result_progress(
            item, result, "Failed. Not retrying.", use_exec_status=False
        )
        return QueueResultDecision(QRESULTACTION.FAIL, QRECOVERYACTION.NONE)
