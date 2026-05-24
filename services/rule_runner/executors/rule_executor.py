from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...browser.ports import InteractionPort
    from ..models import RuleExecutionContext

import threading

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


from ..errors import (
    DuplicateRuleNameException,
    StoppedRequestException,
    PlaywrightSessionLostException,
)

from .actions import ActionsExecutor
from .conditions import ConditionsExecutor
from .triggers import TriggerExecutor
from ..models import (
    RuleExecutionResult,
    ExecutorTaskRef,
    EXECSTEPCALL,
    RuleExecutionState,
)


from ..enums import EXECUTORTASK, RULEEXECSTATUS, EXECUTORSCOPE
from .base.base_scope_executor import BaseScopeExecutor


class RuleExecutor(BaseScopeExecutor):
    """
    Worker class responsible for creating rules in a web application using Selenium WebDriver.
    It handles setting up the rule name, triggers, conditions, and actions, and submitting the rule form.
    Handles exceptions such as duplicate rule names and WebDriver issues.
    """

    def __init__(
        self,
        rule_context: RuleExecutionContext,
    ):

        state = RuleExecutionState(
            status=RULEEXECSTATUS.RUNNING,
            rule_name=rule_context.rule.rule_name,
            interaction_port=None,
            current_task=ExecutorTaskRef(
                scope=EXECUTORSCOPE.RULE,
                task=EXECUTORTASK.START,
                index=None,
                detail_type=None,
            ),
        )
        super().__init__(
            scope_id=EXECUTORSCOPE.RULE, rule_context=rule_context, state=state
        )

        self._flow = [
            EXECSTEPCALL(EXECUTORTASK.OPEN_FORM, self.open_rule_form),
            EXECSTEPCALL(EXECUTORTASK.SET_RULE_NAME, self.set_rule_name),
            EXECSTEPCALL(EXECUTORTASK.EXECUTE_TRIGGERS, self.execute_triggers),
            EXECSTEPCALL(EXECUTORTASK.EXECUTE_CONDITIONS, self.execute_conditions),
            EXECSTEPCALL(EXECUTORTASK.EXECUTE_ACTIONS, self.execute_actions),
            EXECSTEPCALL(EXECUTORTASK.SET_RULE_CATEGORY, self.set_rule_category),
            EXECSTEPCALL(EXECUTORTASK.SUBMIT_RULE, self.submit_rule),
        ]

    def execute(self) -> RuleExecutionResult:
        """
        Executes the rule creation process by navigating through the form pages, setting up triggers, conditions,
        and actions, and submitting the rule. Handles duplicate rule names and retries.
        """

        try:
            self.logging(
                f"Starting {self.__class__.__name__} in thread: {threading.get_ident()}",
                "INFO",
            )

            for step in self._flow:
                self.run_step(step)

            if self._state.rule_rename_attempts > 0:
                old_rule_name = self._ctx.rule.rule_name
                self.logging(f"{old_rule_name} renamed {self._state.rule_name}")

            return RuleExecutionResult(
                rule_guid=self._ctx.rule.guid,
                rule_name=self._state.rule_name,
                task_ref=self._state.current_task,
                success=True,
                status=RULEEXECSTATUS.SUCCESS,
                message="Rule submitted successfully.",
            )
        except StoppedRequestException:
            return self._build_error_result(
                ctx=self._ctx,
                state=self._state,
                status=RULEEXECSTATUS.RUNNER_STOPPED_ERROR,
                message="Stopped Requested.",
            )

        except DuplicateRuleNameException:
            return self._build_error_result(
                ctx=self._ctx,
                state=self._state,
                status=RULEEXECSTATUS.NAME_EXISTS_ERROR,
                message="Rule name still exists after 2 renaming tries.",
            )

        except PlaywrightSessionLostException as e:

            if self._ctx.should_stop():
                return self._build_error_result(
                    ctx=self._ctx,
                    state=self._state,
                    status=RULEEXECSTATUS.RUNNER_STOPPED_ERROR,
                    message="Stopped Requested.",
                )
            self.logging(str(e), "DEBUG")
            return self._build_error_result(
                ctx=self._ctx,
                state=self._state,
                status=RULEEXECSTATUS.BROWSER_ERROR,
                message="Browser doesnt exist.",
            )

        except PlaywrightTimeoutError as e:
            self.logging(str(e), "DEBUG")
            return self._build_error_result(
                ctx=self._ctx,
                state=self._state,
                status=RULEEXECSTATUS.TIMEOUT_ERROR,
                message="Finding element timed out. Rule Failed.",
            )

        except PlaywrightError as e:
            self.logging(str(e), "DEBUG")
            return self._build_error_result(
                ctx=self._ctx,
                state=self._state,
                status=RULEEXECSTATUS.BROWSER_ERROR,
                message="Browser error occurred.",
            )

        except Exception as e:

            if self._ctx.should_stop():
                return self._build_error_result(
                    ctx=self._ctx,
                    state=self._state,
                    status=RULEEXECSTATUS.RUNNER_STOPPED_ERROR,
                    message="Stopped Requested.",
                )

            self.logging(str(e), "DEBUG")
            return self._build_error_result(
                ctx=self._ctx,
                state=self._state,
                status=RULEEXECSTATUS.UNKNOWN_ERROR,
                message="Error happened in rule execution.",
            )

    # STEPS

    def open_rule_form(self, ctx: RuleExecutionContext, state: RuleExecutionState):
        self.logging("Navigating to the Rules Page...", "INFO")
        ctx.browser_port.goto(
            f"https://{ctx.tenant}.intradiem.com/{ctx.profile.selectors.rule_form.page_path}"
        )
        ctx.browser_port.click(ctx.profile.selectors.rule_form.add_rule_button, 3000)
        frame_port = self.switch_to_rule_module(ctx)

        if frame_port is None:
            raise RuntimeError("Rule form interaction port has not been initialized.")
        self._state.interaction_port = frame_port

        if self.is_tutorial_page_present(ctx):
            self.logging("Tutorial Page is present...", "INFO")
            self.next_page(ctx)

    def set_rule_name(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ) -> None:
        """
        Sets the rule name in the rule creation form.
        """
        self.logging("Setting the Rule Name...", "INFO")

        self.form_port.fill(
            ctx.profile.selectors.rule_form.rule_name_input, state.rule_name
        )

    def execute_triggers(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ) -> None:
        """
        Starts processing the triggers for the rule by initializing the TriggerWorker.
        """

        TriggerExecutor(ctx, state).execute()
        self.next_page(ctx)

    def execute_conditions(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ) -> None:
        """
        Starts processing the conditions for the rule by initializing the ConditionsWorker.
        """

        if ctx.rule.conditions:
            self.conditions = ConditionsExecutor(ctx, state)
            self.conditions.execute()
        self.next_page(ctx)

    def execute_actions(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ) -> None:
        """
        Starts processing the actions for the rule by initializing the ActionsWorker.
        """

        if ctx.rule.actions:
            executor = ActionsExecutor(ctx, state)
            executor.execute()
        self.next_page(ctx)

    def set_rule_category(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ) -> None:
        """
        Sets the rule category in the rule creation form.
        """
        self.logging("Setting the rule category", "INFO")
        self.form_port.click(ctx.profile.selectors.rule_form.add_rule_category_button)

        category_frame = ctx.browser_port.frame_locator(
            ctx.profile.selectors.rule_form.rule_category_frame
        )
        category_frame.click(
            ctx.profile.selectors.rule_form.rule_category_dropdown_arrow
        )
        category_frame.select_exact_item_from_list(
            ctx.profile.selectors.rule_form.rule_category_dropdown_list,
            ctx.rule.rule_category,
        )
        self.logging("Switching the main frame", "INFO")

    def submit_rule(self, ctx: RuleExecutionContext, state: RuleExecutionState) -> None:
        """
        Submits the rule form, handling duplicate rule alerts by renaming the rule and retrying.
        """

        self.logging(f"Submitting Rule - {state.rule_name }...", "INFO")

        def submit_rule_succeed():
            for _ in range(2):

                # Retry twice before giving up

                alert = ctx.browser_port.frame_click_and_accept_alert_if_appears(
                    self.form_port,
                    ctx.profile.selectors.rule_form.submit_button,
                    "A Rule with this name already exists",
                    10000,
                )
                if alert:
                    self.rename_rule(ctx, state)
                    self.logging(
                        f"Retrying Rule Submission for renamed rule - {state.rule_name }...",
                        "INFO",
                    )
                    continue

                else:
                    return True  # No alert found, submission is successful
            return False

        if not submit_rule_succeed():
            self.logging(
                f"Rule '{state.rule_name}' could not be submitted after multiple retries.",
                "ERROR",
            )
            raise DuplicateRuleNameException

        self.success_message(ctx, state)

    # HELPERS

    def switch_to_rule_module(self, ctx: RuleExecutionContext) -> InteractionPort:
        """
        Switches the WebDriver to the rule modal frame to interact with rule elements.
        """
        self.logging("Switching to the Rule Modal...", "INFO")
        return ctx.browser_port.frame_locator(
            ctx.profile.selectors.rule_form.rule_modal_frame
        )

    def next_page(self, ctx: RuleExecutionContext) -> None:
        """
        Navigates to the next page in the rule creation form.
        """
        self.logging("Navigating to the Next Page...", "INFO")

        self.form_port.click(ctx.profile.selectors.rule_form.next_page_button)

    def is_tutorial_page_present(self, ctx: RuleExecutionContext) -> bool:
        """
        Checks if the tutorial page is present and can be skipped.

        Returns:
            bool: True if the tutorial page is present, False otherwise.
        """

        return self.form_port.is_visible(
            ctx.profile.selectors.rule_form.tutorial_checkbox
        )

    def rename_rule(self, ctx: RuleExecutionContext, state: RuleExecutionState) -> None:
        """
        Renames the rule in case of a duplicate name error.
        """
        state.rule_rename_attempts += 1

        old_rule_name = ctx.rule.rule_name
        state.rule_name = f"{old_rule_name}-{state.rule_rename_attempts}"

        self.logging(
            f"Trying to rename rule: {old_rule_name} as {state.rule_name}",
            "WARN",
        )
        self.set_rule_name(ctx, state)

    def success_message(
        self, ctx: RuleExecutionContext, state: RuleExecutionState
    ) -> None:
        """
        Logs a success message after the rule has been successfully created.
        """
        success = ctx.browser_port.is_visible(
            ctx.profile.selectors.rule_form.success_marker, 10000
        )
        if not success:
            raise RuntimeError("No Success Message")
        self.logging(f"Rule: {state.rule_name} has been created.", "INFO")
