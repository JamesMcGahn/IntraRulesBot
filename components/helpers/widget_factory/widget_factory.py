from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QLineEdit, QSizePolicy

from components.boxes import GradientGroupBox


class WidgetFactory:

    @staticmethod
    def create_form_box(
        title,
        parent_layout,
        gradient_box=False,
        border_color=None,
        drop_shadow_effect="default",
        object_name="",
        max_width=None,
        alignment="left",
    ):
        if gradient_box:
            box = GradientGroupBox(
                title,
                "black",
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

        box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        if max_width is not None:
            box.setMaximumWidth(max_width)

        layout = QFormLayout(box)
        layout.setVerticalSpacing(25)

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
