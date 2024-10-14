from schemas import RULES_SCHEMA


class GenerateRuleObject:
    """
    A class to dynamically generate a rule object based on a user selection and the rule schema.
    It handles evaluation of conditional fields within the schema and constructs the rule object accordingly.

    Attributes:
        schema (dict): The rule schema used for generating the object.
        user_selection_obj (dict): The user-selected values for generating the rule.

    Args:
        user_selection_obj (dict): The user selection object which contains the data used to build the rule object.
    """

    def __init__(self, user_selection_obj: dict):
        """
        Initializes the GenerateRuleObject with the user selection object and the rule schema.

        Args:
            user_selection_obj (dict): The user selection object containing user input.
        """

        self.schema = RULES_SCHEMA
        self.user_selection_obj = user_selection_obj

    def evaluate_anyOf_conditions(
        self, schema_key: str, user_value: str, parent_obj: object
    ) -> list:
        """
        Evaluates anyOf conditions in the schema to determine the required fields based on the user value.

        Args:
            schema_key (str): The key in the schema to check for conditions.
            user_value (str): The user-selected value for the schema key.
            parent_obj (object): The parent object in the schema where the conditions are defined.

        Returns:
            list: A list of required fields based on the evaluated conditions.
        """
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

    def generate_dynamic_object(self) -> dict:
        """
        Generates the dynamic rule object by iterating over the schema properties and populating
        the fields based on the user selection and schema defaults.

        Returns:
            dict: The dynamically generated rule object.
        """
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

    def generate_conditon_or_action(self, key: str, value: dict) -> list:
        """
        Generates the list of conditions or actions based on the user selection object and the schema.

        Args:
            key (str): The key indicating whether it's conditions or actions.
            value (dict): The schema definition for conditions or actions.

        Returns:
            list: A list of condition or action objects based on the user selection.
        """
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
