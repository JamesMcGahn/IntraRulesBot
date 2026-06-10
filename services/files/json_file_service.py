from __future__ import annotations
from typing import Any
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..logger.adapters import LogAdapter

from pathlib import Path
import json
from .models import JSONLoadResult, JSONSaveResult
from base.service_base import ServiceBase


class JSONFileService(ServiceBase):

    def __init__(self, logger: LogAdapter):
        super().__init__(logger)

    def load(self, file_path: str | Path) -> JSONLoadResult:
        path = Path(file_path)

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            message = f"File Successfully loaded {path}"
            self._logging(message)
            return JSONLoadResult(
                ok=True,
                data=data,
                file_path=file_path,
                message=message,
            )

        except json.JSONDecodeError as e:
            message = f"JSON error in the file {path}"
            self._logging(message, "ERROR")
            self._logging(f"{e}", "DEBUG")
            return JSONLoadResult(
                ok=False,
                data=None,
                file_path=file_path,
                message=message,
            )
        except OSError as e:
            message = f"Could not read the file {path}"
            self._logging(message, "ERROR")
            self._logging(f"{e}", "DEBUG")
            return JSONLoadResult(
                ok=False,
                data=None,
                file_path=file_path,
                message=message,
            )

        except Exception as e:
            message = f"Unexpected error reading the file {path}"
            self._logging(message, "ERROR")
            self._logging(f"{e}", "DEBUG")
            return JSONLoadResult(
                ok=False,
                data=None,
                file_path=file_path,
                message=message,
            )

    def save(
        self, data: dict[str, Any] | list[Any], file_path: str | Path
    ) -> JSONSaveResult:
        path = Path(file_path)
        try:
            with path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
            message = f"File Successfully saved {path}"
            self._logging(message)
            return JSONSaveResult(ok=True, file_path=file_path, message=message)
        except OSError as e:
            message = f"Could not save the file {path}"
            self._logging(message, "ERROR")
            self._logging(f"{e}", "DEBUG")
            return JSONSaveResult(ok=False, file_path=file_path, message=message)

        except Exception as e:
            message = f"Unexpected error saving the file {path}"
            self._logging(message, "ERROR")
            self._logging(f"{e}", "DEBUG")
            return JSONSaveResult(ok=False, file_path=file_path, message=message)
