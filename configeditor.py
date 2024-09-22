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
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ConfigEditor(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.current_rule_index = 0

        main_layout = QVBoxLayout(self)
        # self.rules_list_layout = QVBoxLayout()
        # main_layout.addLayout(self.rules_list_layout)

        self.stacked_widget = QStackedWidget()
        # main_layout.addWidget(self.stacked_widget)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.stacked_widget)
        main_layout.addWidget(scroll_area)
        for rule in self.config["avaya"]["rules"]:
            self.create_rule_form(rule)

        button_layout = QVBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.show_previous_rule)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_next_rule)
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)

        main_layout.addLayout(button_layout)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_config)
        main_layout.addWidget(save_button)

        self.rules = []


    def show_previous_rule(self):
        if self.current_rule_index > 0:
            self.current_rule_index -= 1
            self.stacked_widget.setCurrentIndex(self.current_rule_index)

    def show_next_rule(self):
        if self.current_rule_index < self.stacked_widget.count() - 1:
            self.current_rule_index += 1
            self.stacked_widget.setCurrentIndex(self.current_rule_index)

    def create_rule_form(self, rule):
        rule_widget = QWidget()
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


        rule_input = { }


        rule_name = QLineEdit(rule["rule_name"])
        rule_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        rule_input["rule_name"] = rule_name

        general_settings_layout.addRow(QLabel("Rule Name:"),rule_name )
        
        general_settings_box.setLayout(general_settings_layout)
        rule_layout.addRow(general_settings_box)

        if "frequency_based" in rule:
            frequency_settings_box = QGroupBox("Frequency Settings")
            frequency_settings_layout = QFormLayout(frequency_settings_box)
            frequency_settings_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
            frequency_settings_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
            frequency_input = QLineEdit(str(rule["frequency_based"]["time_interval"]))
            frequency_settings_layout.addRow( QLabel("Time Interval:"),frequency_input)
            rule_layout.addRow(frequency_settings_box)
            rule_input["frequency_based"] = {
                "time_interval" : frequency_input
            }

        conditions = []
        for i,condition in enumerate(rule["conditions"]):
            condition_group_box = QGroupBox(f"Condition - {(i+1)} - {condition["details"]["condition_type"].title()}")
            condition_layout = QFormLayout(condition_group_box)
            condition_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
            inputs = self.create_condition_fields(condition_layout, condition)
            # condition_group_box.setLayout(condition_layout)
            rule_layout.addRow(condition_group_box)
            conditions.append(inputs)
        rule_input["conditions"] = conditions

        actions  = []
        for i,action in enumerate(rule["actions"]):
            action_group_box = QGroupBox(f"Action - {(i+1)} - {action["details"]["action_type"].title()}")
            action_layout = QFormLayout(action_group_box)
            action_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
            inputs = self.create_action_fields(action_layout, action)
            actions.append(inputs)
            # action_group_box.setLayout(condition_layout)
            rule_layout.addRow(action_group_box)
        rule_input["actions"] = actions

        rule_group_box.setLayout(rule_layout)
        rule_layout = QVBoxLayout()
        rule_layout.addWidget(rule_group_box)
        rule_widget.setLayout(rule_layout)
        self.stacked_widget.addWidget(rule_widget)

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

            provider_condition_type_input = QLineEdit(details["condition_type"])
            details_layout.addRow(QLabel("condition_type:"), provider_condition_type_input)

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
                "provider_condition": provider_condition_input,
                "detials":{
                    "condition_type": provider_condition_type_input,
                    "equality_operator": equality_operator_input,
                    "equality_threshold": equality_threshold_input,
                    "queues_source": queues_source_input,
                }
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
                "provider_condition": provider_condition_input,
                "details":{
                    "action_type": action_type,
                    "email_subject": email_subject_input,
                    "email_body": email_body_input,
                    "email_address": email_address_input,
                }
            }