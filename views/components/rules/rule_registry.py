from ...base import FieldRegistry


class RuleFieldRegistry(FieldRegistry):

    def __init__(self):
        super().__init__()
        self._field_map = {}

    def has_field(self, key):
        return key in self._registry

    def set_value(self, key, value):
        if not self.has_field(key):
            return
        self.set_text_value(key, value)

    def register_field(self, full_path, widget):
        self._registry[full_path] = widget
        self._register_nested_field(full_path, widget)

    def _register_nested_field(self, path: str, widget):
        """
        Builds nested field map structures from dot-separated paths.

        Example:
            conditions.0.details.queue_source

        Produces:
        {
            "conditions": [
                {
                    "details": {
                        "queue_source": widget
                    }
                }
            ]
        }
        """
        parts = path.split(".")
        current = self._field_map

        for i, token in enumerate(parts[:-1]):
            next_token = parts[i + 1]

            if isinstance(current, dict):
                if next_token.isdigit():
                    is_created = current.get(token)
                    if is_created is None:
                        current[token] = []
                    current = current[token]

                else:
                    current = current.setdefault(token, {})
            elif isinstance(current, list):
                if not token.isdigit():
                    raise ValueError

                index = int(token)
                while len(current) <= index:

                    container = [] if next_token.isdigit() else {}

                    current.append(container)

                current = current[index]
        leaf = parts[-1]
        current[leaf] = widget

    def get_field_map(self):
        return self._field_map

    @property
    def field_map(self):
        return self._field_map

    @field_map.setter
    def field_map(self, field_map: dict):
        self._field_map = field_map
