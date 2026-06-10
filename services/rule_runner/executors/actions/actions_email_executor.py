from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models import RuleExecutionContext, RuleExecutionState
    from ...models.executor_item_context import ExecutorItemContext

from ....rules.models.actions import Action, ActionsEmailDetails
from ..base import BaseChildDetailedExecutor

from ...enums import EXECUTORSCOPE
from ....profiles.models.action_selectors import ActionDetailSelectors


class ActionsEmailExecutor(
    BaseChildDetailedExecutor[ActionsEmailDetails, ActionDetailSelectors]
):
    """
    Executor Actions Detail : Email
    """

    def __init__(
        self,
        context: RuleExecutionContext,
        state: RuleExecutionState,
        selectors: ActionDetailSelectors,
        item_context: ExecutorItemContext[Action[ActionsEmailDetails]],
    ):
        super().__init__(
            EXECUTORSCOPE.CONDITION, context, state, selectors, item_context
        )
        self._flow = [
            self.click_email_settings_page,
            self.set_email_subject,
            self.set_email_message,
            self.click_next_page,
            self.set_email_address,
        ]

    def click_email_settings_page(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Action[ActionsEmailDetails]],
    ) -> None:
        """
        Clicks on the email settings button to open the email configuration page.
        """
        self.form_port.click(self.selectors.email_settings_button)

    def set_email_subject(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Action[ActionsEmailDetails]],
    ) -> None:
        """
        Sets the subject of the email based on the rule name.
        """
        self.logging(f"Setting email subject for Action {item_ctx.index+1}...", "INFO")
        self.form_port.fill(
            self.selectors.email_subject, item_ctx.item.details.email_subject
        )

    def set_email_message(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Action[ActionsEmailDetails]],
    ) -> None:
        """
        Sets the email message body based on the provided action details.
        """
        self.logging(f"Setting email message for Action {item_ctx.index+1}...", "INFO")

        self.form_port.fill(
            self.selectors.email_message, item_ctx.item.details.email_body
        )

    def click_next_page(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Action[ActionsEmailDetails]],
    ) -> None:
        """
        Clicks the next button to proceed to the next step in the email configuration.
        """
        self.form_port.click(self.selectors.user_settings_button)

    def set_email_address(
        self,
        ctx: RuleExecutionContext,
        state: RuleExecutionState,
        item_ctx: ExecutorItemContext[Action[ActionsEmailDetails]],
    ) -> None:
        """
        Sets the recipient email address based on the rule condition source
        and the provided action details.
        """
        self.logging(
            f"Setting receiver email address for Action {item_ctx.index+1}...", "INFO"
        )
        self.form_port.click(self.selectors.email_individual_radio)

        self.form_port.fill(
            self.selectors.email_address, item_ctx.item.details.email_address
        )
