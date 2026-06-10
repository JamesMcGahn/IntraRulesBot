from base.enums import LOGLEVEL


class LogAdapter:
    def __init__(self, logger):
        self.logger = logger

    def __call__(self, msg: str, level: LOGLEVEL, print_msg=True) -> None:
        self.logger.insert(msg, level, print_msg)
