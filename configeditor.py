from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ConfigEditor(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config


        main_layout = QVBoxLayout(self)
        self.rules_list_layout = QVBoxLayout()
        main_layout.addLayout(self.rules_list_layout)

        for rule in self.config["avaya"]["rules"]:
            self.create_rule_form(rule)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_config)
        main_layout.addWidget(save_button)

    def create_rule_form(self, rule):
        print(rule)
        rule_group_box = QGroupBox(f"Rule Configuration - {rule["rule_name"]}")
        rule_group_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        rule_layout = QFormLayout(rule_group_box)
        rule_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # General Settings Box
        general_settings_box = QGroupBox("General Settings")
        general_settings_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # general_settings_box.setMinimumWidth(300)

        general_settings_layout = QFormLayout(general_settings_box)
        general_settings_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        general_settings_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        # general_settings_layout.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        rule_name = QLineEdit(rule["rule_name"])
        rule_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
       
        general_settings_layout.addRow(QLabel("Rule Name:"),rule_name )
        
        general_settings_box.setLayout(general_settings_layout)
        rule_layout.addRow(general_settings_box)

        if "frequency_based" in rule:
            frequency_settings_box = QGroupBox("Frequency Settings")
            frequency_settings_layout = QFormLayout(frequency_settings_box)
            frequency_settings_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
            frequency_settings_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

            frequency_settings_layout.addRow(
                QLabel("Time Interval:"),
                QLineEdit(str(rule["frequency_based"]["time_interval"])),
            )
            rule_layout.addRow(frequency_settings_box)


        for i,condition in enumerate(rule["conditions"]):
            condition_group_box = QGroupBox(f"Condition - {(i+1)} - {condition["details"]["condition_type"].title()}")
            condition_layout = QFormLayout(condition_group_box)
            condition_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
            inputs = self.create_condition_fields(condition_layout, condition)
            # condition_group_box.setLayout(condition_layout)
            rule_layout.addRow(condition_group_box)

        for i,action in enumerate(rule["actions"]):
            action_group_box = QGroupBox(f"Action - {(i+1)} - {action["details"]["action_type"].title()}")
            action_layout = QFormLayout(action_group_box)
            action_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
            inputs = self.create_action_fields(action_layout, action)
            # action_group_box.setLayout(condition_layout)
            rule_layout.addRow(action_group_box)



        rule_group_box.setLayout(rule_layout)
        self.rules_list_layout.addWidget(rule_group_box)

    def save_config(self):
        is_valid, message = self.validate_inputs()
        if not is_valid:
            #  QMessageBox.warning(self, "Input Error", message)
            return
        # Save logic..

    def create_condition_fields(self, layout, condition):
        # Common fields
        condition_general_settings_box = QGroupBox("Condition Provider Settings")
        condition_general_settings_layout = QFormLayout(condition_general_settings_box)
        condition_general_settings_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        condition_general_settings_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        provider_category_input = QLineEdit(condition["provider_category"])
        condition_general_settings_layout.addRow(QLabel("Provider Category:"), provider_category_input)

        provider_instance_input = QLineEdit(condition["provider_instance"])
        condition_general_settings_layout.addRow(QLabel("Provider Instance:"), provider_instance_input)

        provider_condition_input = QLineEdit(condition["provider_condition"])
        condition_general_settings_layout.addRow(QLabel("Provider Instance:"), provider_condition_input)

        layout.addRow(condition_general_settings_box)
        # Dynamically generate fields based on condition type
        details = condition["details"]
        if details["condition_type"] == "stats":
            details_group_box = QGroupBox(f"{condition["provider_condition"]} Settings")
            details_layout = QFormLayout(details_group_box)
            details_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
            details_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

            equality_operator_input = QLineEdit(details["equality_operator"])
            details_layout.addRow(QLabel("Equality Operator:"), equality_operator_input)

            equality_threshold_input = QLineEdit(str(details["equality_threshold"]))
            details_layout.addRow(QLabel("Equality Threshold:"), equality_threshold_input)

            queues_source_input = QLineEdit(details["queues_source"])
            details_layout.addRow(QLabel("Queue Source:"), queues_source_input)

            layout.addRow(details_group_box)
            # Store inputs in a structured way
            return {
                "provider_category": provider_category_input,
                "provider_instance": provider_instance_input,
                "equality_operator": equality_operator_input,
                "equality_threshold": equality_threshold_input,
            }
        
    def create_action_fields(self, layout, action):
        condition_general_settings_box = QGroupBox("Action Provider Settings")
        condition_general_settings_layout = QFormLayout(condition_general_settings_box)
        condition_general_settings_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        condition_general_settings_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        provider_category_input = QLineEdit(action["provider_category"])
        condition_general_settings_layout.addRow(QLabel("Provider Category:"), provider_category_input)

        provider_instance_input = QLineEdit(action["provider_instance"])
        condition_general_settings_layout.addRow(QLabel("Provider Instance:"), provider_instance_input)

        provider_condition_input = QLineEdit(action["provider_condition"])
        condition_general_settings_layout.addRow(QLabel("Provider Instance:"), provider_condition_input)

        layout.addRow(condition_general_settings_box)
        # Dynamically generate fields based on condition type
        details = action["details"]
        if details["action_type"] == "email":
            details_group_box = QGroupBox(f"{action["provider_condition"]} Settings")
            details_layout = QFormLayout(details_group_box)
            details_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
            details_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

            action_type = QLineEdit(details["action_type"])
            details_layout.addRow(QLabel("Condition Type:"), action_type)

            email_subject_input = QLineEdit(details["email_subject"])
            details_layout.addRow(QLabel("Email Subject:"), email_subject_input)

            email_body_input = QTextEdit(str(details["email_body"]))
            details_layout.addRow(QLabel("Email Body:"), email_body_input)

            email_address_input = QLineEdit(details["email_address"])
            details_layout.addRow(QLabel("To Email Address:"), email_address_input)

            layout.addRow(details_group_box)


            # Store inputs in a structured way
            return {
                "provider_category": provider_category_input,
                "provider_instance": provider_instance_input,
                # "equality_operator": equality_operator_input,
                # "equality_threshold": equality_threshold_input,
            }