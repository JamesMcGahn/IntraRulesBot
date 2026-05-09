from .example_rule_set import example_01
from .example_rule_set_2 import example_02


def default_rule_set_collector() -> list[dict]:
    rule_set_list = [example_01, example_02]
    return rule_set_list
