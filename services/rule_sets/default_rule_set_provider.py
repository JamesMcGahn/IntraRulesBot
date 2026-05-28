from .default_rule_sets.default_rule_set_collector import default_rule_set_collector


class DefaultRuleSetProvider:
    def load(self) -> list[dict]:
        return default_rule_set_collector()
