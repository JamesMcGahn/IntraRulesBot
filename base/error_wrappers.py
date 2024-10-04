from selenium.common.exceptions import (
    NoSuchFrameException,
    NoSuchWindowException,
    TimeoutException,
    WebDriverException,
)


class ErrorWrappers:

    @staticmethod
    def qworker_web_raise_error(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)

            except NoSuchWindowException:
                self.logging(
                    f"Something went wrong in {self.__class__.__name__}:Can't Find Window. The browser was closed.",
                    "ERROR",
                )
                raise NoSuchWindowException from NoSuchWindowException
            except NoSuchFrameException:
                self.logging(
                    f"Something went wrong in {self.__class__.__name__}: Can't Find Frame. The Frame was closed.",
                    "ERROR",
                )
                raise NoSuchFrameException from NoSuchFrameException
            except Exception as e:
                self.logging(
                    f"Something went wrong in {self.__class__.__name__}: {e}", "ERROR"
                )
                raise Exception(e) from Exception

        return wrapper
