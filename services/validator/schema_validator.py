from typing import Tuple

from jsonschema import Draft202012Validator, ValidationError
from jsonschema.validators import RefResolver

from schemas import MAIN_SCHEMA, RULES_SCHEMA


class SchemaValidator:
    def __init__(self, schemaId: str):
        self.schema_store = {}
        self.validator = None
        self.load_schemas()
        self.select_schema(schemaId)

    def load_schemas(self) -> None:
        for schema_file in (MAIN_SCHEMA, RULES_SCHEMA):
            self.schema_store[schema_file["$id"]] = schema_file

    def select_schema(self, selected_schema: str) -> Draft202012Validator:
        if selected_schema not in self.schema_store:
            raise ValueError(f"Schema '{selected_schema}' not found in store.")

        main_schema = self.schema_store[selected_schema]
        resolver = RefResolver.from_schema(main_schema, store=self.schema_store)
        self.validator = Draft202012Validator(main_schema, resolver=resolver)

    def get_validator(self) -> Draft202012Validator:
        return self.validator

    def validate(self, instance: dict) -> None:
        self.validator.validate(instance)

    @staticmethod
    def format_validation_error(error: ValidationError) -> Tuple[str, str, str]:
        error_message = (
            error.json_path.replace("$.", "")
            .replace("[", ".")
            .replace("]", "")
            .split(".")
        )
        failed_feild = error_message[-1]
        format_error = ""
        for i, error_part in enumerate(error_message):
            if i == 0 and error_part != "rules":
                break
            if i == 0:
                format_error = "There was an error in rules "
            elif error_part.isdigit():
                format_error += f"item number {int(error_part) +1} "
            else:
                format_error += f"- {error_part} "

        error_path_msg = format_error.strip() + "."

        return (failed_feild, error_path_msg, error.message)
