class GenerateRuleObject:

    def __init__(self, schema_path, user_selection_obj):
        self.schema_path = schema_path
        self.schema = None
        self.user_selection_obj = user_selection_obj
        self.rule_object = self.generate_dynamic_object()

    def load_schema(self):
        try:
            with open("schemas/rules_schema.json", "r") as schema_file:
                self.schema = json.load(schema_file)
        except Exception as e:
            (f"An unexpected error occurred: {e}")

    def get_rule_object(self):
        return self.rule_object

    def evaluate_anyOf_conditions(
        self, schema_key: str, user_value: str, parent_obj: object
    ):
        """Evaluate conditions in the schema and return required fields."""
        required_fields = []

        for condition in parent_obj.get("anyOf", []):
            if "if" in condition and "properties" in condition["if"]:
                condition_props = condition["if"]["properties"]
                if schema_key in condition_props and user_value == condition_props[
                    schema_key
                ].get("const"):
                    required_fields.extend(
                        condition.get("then", {}).get("required", [])
                    )

        return required_fields

    def generate_dynamic_object(self):
        result = {}

        # Iterate over the schema properties to build the object
        for key, value in self.schema.get("properties", {}).items():

            if key == "frequency_based" and self.user_selection_obj.get(key, False):
                frequency = {
                    prop: val.get("default", "")
                    for prop, val in value["properties"].items()
                }
                result[key] = frequency

            # TODO: Add for Action Based - when added to schema

            elif key == "actions":
                result[key] = []
                for action in self.user_selection_obj.get(key, []):

                    action_obj = {
                        prop: action.get(prop, "")
                        for prop in value["items"]["properties"]
                    }

                    # TODO: Add for Action Based - when added to schema
                    if "details" in action_obj:
                        for detail_key, _ in value["items"]["properties"]["details"][
                            "properties"
                        ].items():
                            if detail_key in action_obj["details"]:
                                required_fields = self.evaluate_anyOf_conditions(
                                    detail_key,
                                    action_obj["details"][detail_key],
                                    value["items"]["properties"]["details"],
                                )

                                for field in required_fields:
                                    action_obj["details"][field] = action[
                                        "details"
                                    ].get(field, "")
                    result[key].append(action_obj)

            elif key == "conditions":
                result[key] = []
                for condition in self.user_selection_obj.get(key, []):
                    condition_obj = {
                        prop: condition.get(prop, "")
                        for prop in value["items"]["properties"]
                    }

                    if condition.get("details", {}).get("condition_type") == "stats":
                        for detail in value["items"]["properties"]["details"]["then"][
                            "required"
                        ]:
                            condition_obj["details"][detail] = condition["details"].get(
                                detail, ""
                            )
                    result[key].append(condition_obj)
            elif key not in ["frequency_based", "action_based"]:
                result[key] = value.get("default", "")

        return result


import json

user_inputs = {
    "frequency_based": True,
    "actions": [
        {
            "details": {
                "action_type": "email",
            },
        }
    ],
}


# Load your JSON schema


print(GenerateRuleObject("schemas/rules_schema.json", user_inputs).get_rule_object())
