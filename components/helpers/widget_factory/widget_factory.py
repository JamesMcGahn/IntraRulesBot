from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QIcon, QValidator
from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QLineEdit, QSizePolicy

from components.boxes import GradientGroupBox

from ..style_helper import StyleHelper


class WidgetFactory:

    @staticmethod
    def create_form_box(
        title,
        parent_layout,
        gradient_box=False,
        border_color=None,
        drop_shadow_effect=True,
        object_name="",
        max_width=None,
        title_color="black",
        title_font_size=16,
    ):
        if gradient_box:
            box = GradientGroupBox(
                title,
                title_color,
                gradient_box,
                border_color,
                drop_shadow_effect=drop_shadow_effect,
            )
            box.set_gradient_start_stop(
                box.width() / 2, 0, box.width() / 2, box.height()
            )
        else:
            box = QGroupBox(title)
            box.setObjectName(object_name)
            box.setStyleSheet("QGroupBox::title { color:" + f"{title_color}" + ";}")
            # TODO - refactor to UI helper function
            if drop_shadow_effect:
                if isinstance(drop_shadow_effect, bool):
                    drop_shadow_effect = (8, 3, 3, QColor(0, 0, 0, 60))

                radius, xoffset, yoffset, color = drop_shadow_effect
                StyleHelper.drop_shadow(box, radius, xoffset, yoffset, color)

        StyleHelper.dpi_scale_set_font(box, font_size=title_font_size)

        box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        if max_width is not None:
            box.setMaximumWidth(max_width)

        layout = QFormLayout(box)
        layout.setVerticalSpacing(20)

        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        box.setLayout(layout)

        parent_layout.addWidget(box)
        return layout

    @staticmethod
    def create_input_field(
        initial_value="", background_color="#FCFCFC", validator: QValidator = None
    ):
        field = QLineEdit(initial_value)
        field.setStyleSheet(f"background-color: {background_color} ")
        field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        if validator is not None:
            field.setValidator(validator)

        return field

    @staticmethod
    def create_form_input_row(
        line_edit_value: str,
        label_text: str,
        parent_layout: QFormLayout,
        background_color="#FCFCFC",
        validator: QValidator = None,
    ):
        el = WidgetFactory.create_input_field(
            line_edit_value, background_color, validator
        )
        label = QLabel(label_text)
        label.setStyleSheet("background-color: transparent;")
        parent_layout.addRow(label, el)
        return el

    @staticmethod
    def create_icon(
        parent,
        file_location,
        width,
        height,
        checkable=False,
        file_location_2=None,
        exclusive=True,
    ):
        icon = QIcon()

        icon.addFile(
            file_location,
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )

        if checkable and file_location_2:
            icon.addFile(
                file_location_2,
                QSize(),
                QIcon.Mode.Normal,
                QIcon.State.On,
            )

        parent.setIcon(icon)
        parent.setIconSize(QSize(width, height))
        parent.setCheckable(checkable)
        parent.setAutoExclusive(exclusive)
        parent.setCursor(Qt.PointingHandCursor)
