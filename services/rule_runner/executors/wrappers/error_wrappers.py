from typing import Callable

from ...errors import StoppedRequestException, PlaywrightSessionLostException


from functools import wraps

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class ExecutorWrappers:
    @staticmethod
    def child_raise_error(func: Callable) -> Callable:
        """
        Wrapper for handling Playwright exceptions.

        This decorator catches Playwright-related exceptions, logs them,
        and then re-raises the errors. If the executor has been stopped,
        it converts the error into a StoppedRequestException.

        Args:
            func (Callable): The function to be wrapped.

        Returns:
            Callable: A wrapped function that includes error handling.
        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)

            except PlaywrightTimeoutError as e:
                if self._ctx.should_stop():
                    raise StoppedRequestException from e

                self.logging(
                    "Playwright operation timed out.",
                    "ERROR",
                )
                self.logging(f"{e}", "DEBUG")
                raise

            except PlaywrightError as e:
                if self._ctx.should_stop():
                    raise StoppedRequestException from e

                msg = str(e).lower()
                if "has been closed" in msg and any(
                    word in msg
                    for word in (
                        "browser",
                        "context",
                        "page",
                        "target",
                    )
                ):
                    self.logging("Playwright session lost.", "ERROR")
                    self.logging(str(e), "DEBUG")
                    raise PlaywrightSessionLostException from e

                self.logging(
                    "Playwright operation failed.",
                    "ERROR",
                )
                self.logging(f"{e}", "DEBUG")
                raise

            except Exception as e:
                if self._ctx.should_stop():
                    raise StoppedRequestException from e

                self.logging(str(e), "DEBUG")
                raise

        return wrapper


def is_browser_session_closed_error(e: Exception) -> bool:
    msg = str(e).lower()

    return "has been closed" in msg and any(
        word in msg
        for word in (
            "browser",
            "context",
            "page",
            "target",
        )
    )
