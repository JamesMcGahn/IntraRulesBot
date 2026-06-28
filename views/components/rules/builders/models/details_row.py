from dataclasses import dataclass


@dataclass
class DetailsRow:
    initial_value: str
    label_text: str
    rule_input_path: str
