from schemas import RULES_SCHEMA


class GenerateRuleObject:

    def __init__(self, user_selection_obj):

        self.schema = RULES_SCHEMA
        self.user_selection_obj = user_selection_obj

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
                result[key] = self.generate_conditon_or_action(key, value)

            elif key == "conditions":
                result[key] = self.generate_conditon_or_action(key, value)

            elif key == "rule_name":
                result[key] = self.user_selection_obj.get("rule_name", "")

            elif key not in ["frequency_based", "action_based"]:
                result[key] = value.get("default", "")

        result["guid"] = self.user_selection_obj.get("guid", None)
        return result

    def generate_conditon_or_action(self, key, value):
        result = []
        for conditon in self.user_selection_obj.get(key, []):

            conditon_obj = {
                prop: conditon.get(prop, "") for prop in value["items"]["properties"]
            }

            if "details" in conditon_obj:
                for detail_key, _ in value["items"]["properties"]["details"][
                    "properties"
                ].items():
                    if detail_key in conditon_obj["details"]:
                        required_fields = self.evaluate_anyOf_conditions(
                            detail_key,
                            conditon_obj["details"][detail_key],
                            value["items"]["properties"]["details"],
                        )

                        for field in required_fields:
                            conditon_obj["details"][field] = conditon_obj[
                                "details"
                            ].get(field, "")
            result.append(conditon_obj)
        return result
