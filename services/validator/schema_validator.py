from typing import Tuple

from jsonschema import Draft202012Validator, ValidationError
from jsonschema.validators import RefResolver

from schemas import MAIN_SCHEMA, RULES_SCHEMA


class SchemaValidator:
    """
    A class for validating data against JSON schemas using Draft 2020-12 validators.
    It loads and stores schemas, selects the appropriate schema for validation, and provides
    error formatting for validation failures.

    Attributes:
        schema_store (dict): A store of schemas identified by their `$id`.
        validator (Draft202012Validator): The current validator for the selected schema.

    Args:
        schemaId (str): The ID of the schema to be used for validation.
    """

    def __init__(self, schemaId: str):
        """
        Initializes the SchemaValidator by loading schemas and selecting the appropriate schema.

        Args:
            schemaId (str): The ID of the schema to be used for validation.
        """
        self.schema_store = {}
        self.validator = None
        self.load_schemas()
        self.select_schema(schemaId)

    def load_schemas(self) -> None:
        """
        Loads schemas into the schema store from predefined schema files (e.g., MAIN_SCHEMA, RULES_SCHEMA).

        Returns:
            None: This function does not return a value.
        """
        for schema_file in (MAIN_SCHEMA, RULES_SCHEMA):
            self.schema_store[schema_file["$id"]] = schema_file

    def select_schema(self, selected_schema: str) -> Draft202012Validator:
        """
        Selects and sets the schema validator based on the schema ID.

        Args:
            selected_schema (str): The ID of the schema to select for validation.

        Returns:
            Draft202012Validator: The validator for the selected schema.

        Raises:
            ValueError: If the selected schema is not found in the schema store.
        """
        if selected_schema not in self.schema_store:
            raise ValueError(f"Schema '{selected_schema}' not found in store.")

        main_schema = self.schema_store[selected_schema]
        resolver = RefResolver.from_schema(main_schema, store=self.schema_store)
        self.validator = Draft202012Validator(main_schema, resolver=resolver)

    def get_validator(self) -> Draft202012Validator:
        """
        Returns the current schema validator.

        Returns:
            Draft202012Validator: The schema validator.
        """
        return self.validator

    def validate(self, instance: dict) -> None:
        """
        Validates an instance (a dictionary) against the selected schema.

        Args:
            instance (dict): The data instance to validate against the selected schema.

        Returns:
            None: This function does not return a value.

        Raises:
            ValidationError: If the instance fails schema validation.
        """
        self.validator.validate(instance)

    @staticmethod
    def format_validation_error(error: ValidationError) -> Tuple[str, str, str]:
        """
        Formats a JSON schema validation error into a tuple containing the field that failed,
        the error path, and the error message.

        Args:
            error (ValidationError): The validation error to format.

        Returns:
            Tuple[str, str, str]: A tuple containing:
                - The failed field (str)
                - The error path message (str)
                - The error message (str)
        """
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
