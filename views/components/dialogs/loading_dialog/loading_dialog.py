from typing import Optional

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QProgressBar,
)

from ..gradient_dialog import GradientDialog
from .loading_dialog_css import STYLES


class LoadingDialog(GradientDialog):
    """
    A custom dialog for displaying a message with a gradient background.

    Args:
        title (str): The title of the dialog window.
        message (str): The message to display in the dialog.
        parent (Optional[QWidget]): The parent widget of the dialog, defaults to None.
    """

    def __init__(
        self,
        title: str,
        message: str,
        parent: Optional[QWidget] = None,
        allow_close=False,
    ):
        gradient_colors = [(0.05, "#228752"), (0.75, "#014637"), (1, "#014637")]
        super().__init__(gradient_colors, parent)
        self.title = title
        self.setFixedHeight(200)
        self.setFixedWidth(400)
        self.setWindowTitle(self.title)
        self.message = message
        self.setStyleSheet(STYLES)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)

        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        self.progress.setValue(0)
        self.progress.setAlignment(Qt.AlignCenter)
        self.settings_layout = QVBoxLayout(self)
        self.settings_layout.setAlignment(Qt.AlignCenter)
        message_text = QLabel(self.message)
        message_text.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        logo_label.setPixmap(QPixmap(":/system_icons/logo48_48.ico"))
        message_layout = QHBoxLayout()
        message_layout.setAlignment(Qt.AlignCenter)
        message_layout.addWidget(logo_label)
        message_layout.addWidget(message_text)
        self.settings_layout.addLayout(message_layout)
        self.settings_layout.addWidget(self.progress)
        self._allow_close = allow_close

        self._progress_value = 0
        self._progress_step = 2
        self._progress_timer = QTimer(self)
        self._progress_timer.setInterval(75)
        self._progress_timer.timeout.connect(self._update_progress)
        self._progress_timer.start()

    @Slot(bool)
    def set_allow_close(self, value: bool):
        self._allow_close = value

    def _update_progress(self) -> None:
        """Advance the progress bar and reset it when it reaches the end."""
        self._progress_value += self._progress_step

        if self._progress_value > self.progress.maximum():
            self._progress_value = self.progress.minimum()

        self.progress.setValue(self._progress_value)

    def closeEvent(self, event) -> None:
        """Stop the progress timer when the dialog closes."""

        if self._allow_close:
            self._progress_timer.stop()
            super().closeEvent(event)

            return

        event.ignore()
