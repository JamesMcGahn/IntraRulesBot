from typing import Callable

from selenium.common.exceptions import (
    NoSuchFrameException,
    NoSuchWindowException,
)


class ErrorWrappers:
    @staticmethod
    def qworker_web_raise_error(func: Callable) -> Callable:
        """
        Wrapper for handling Selenium WebDriver exceptions.

        This decorator catches Selenium-related exceptions, logs them,
        and then re-raises the errors.

        Args:
            func (Callable): The function to be wrapped.

        Returns:
            Callable: A wrapped function that includes error handling.
        """

        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)

            except NoSuchWindowException as e:
                self.logging(
                    f"{self.__class__.__name__}:Can't Find Window. The browser was closed.",
                    "ERROR",
                )
                self.loggin(f"{e}", "DEBUG")
                raise NoSuchWindowException from NoSuchWindowException
            except NoSuchFrameException as e:
                self.logging(
                    f"{self.__class__.__name__}: Can't Find Frame. The Frame was closed.",
                    "ERROR",
                )
                self.loggin(f"{e}", "DEBUG")
                raise NoSuchFrameException from NoSuchFrameException
            except Exception as e:
                self.logging(f"{self.__class__.__name__}: {e}", "ERROR")
                raise Exception(e) from Exception

        return wrapper
