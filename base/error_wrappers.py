from typing import Callable

from selenium.common.exceptions import (
    NoSuchFrameException,
    NoSuchWindowException,
    TimeoutException,
    WebDriverException,
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
                    f"Something went wrong in {self.__class__.__name__}:Can't Find Window. The browser was closed.",
                    "ERROR",
                )
                if hasattr(self, "error_occurred"):
                    self.error_occurred.emit(f"Browser closed: {str(e)}")
                else:
                    raise NoSuchWindowException from NoSuchWindowException
            except NoSuchFrameException as e:
                self.logging(
                    f"Something went wrong in {self.__class__.__name__}: Can't Find Frame. The Frame was closed.",
                    "ERROR",
                )
                if hasattr(self, "error_occurred"):
                    self.error_occurred.emit(f"The Frame was closed.: {str(e)}")
                else:
                    raise NoSuchFrameException from NoSuchFrameException
            except Exception as e:
                self.logging(
                    f"Something went wrong in {self.__class__.__name__}: {e}", "ERROR"
                )
                if hasattr(self, "error_occurred"):
                    self.error_occurred.emit(
                        f"Something went wrong in {self.__class__.__name__}: {str(e)}"
                    )
                else:
                    raise Exception(e) from Exception

        return wrapper
