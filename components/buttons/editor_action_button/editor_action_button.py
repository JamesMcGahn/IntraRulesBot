from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QPushButton


class EditorActionButton(QPushButton):
    """
    A QPushButton subclass that changes its checked state based on mouse press and release events.

    Args:
        text (str): The text label of the button.
    """

    def __init__(self, text: str):
        """
        Initialize the EditorActionButton.

        Args:
            text (str): The text to display on the button.
        """
        super().__init__(text=text)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handle the mouse press event to set the button as checked if the left mouse button is pressed.

        Args:
            event (QMouseEvent): The mouse press event.

        Returns:
            None: This function does not return a value.
        """
        if event.button() == Qt.LeftButton:
            self.setChecked(True)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        Handle the mouse release event to uncheck the button when the left mouse button is released.

        Args:
            event (QMouseEvent): The mouse release event.

        Returns:
            None: This function does not return a value.
        """
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.setChecked(False)
