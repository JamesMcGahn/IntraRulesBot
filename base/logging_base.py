from services.logger.adapters import LogAdapter


class LoggingBase:

    def __init__(self, logger: LogAdapter):
        self.logger = logger

    def logging(self, msg, level="INFO", print_msg=True) -> None:
        msg = f"{self.__class__.__name__}: {msg}"
        self.logger(msg, level, print_msg)
