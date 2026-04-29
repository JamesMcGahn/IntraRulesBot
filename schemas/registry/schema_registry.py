from jsonschema import Draft202012Validator
from jsonschema.validators import RefResolver

from schemas import MAIN_SCHEMA, RULES_SCHEMA
from ..enums import SCHEMATYPE


class SchemaRegistry:
    """
    A registry class for JSON schemas using Draft 2020-12 validators.
    It loads and stores schemas, selects the appropriate schema for validation.

    Attributes:
        schema_store (dict): A store of schemas identified by their `$id`.
    """

    def __init__(self):
        """
        Initializes the SchemaValidator by loading schemas and selecting the appropriate schema.

        Args:
            schemaId (str): The ID of the schema to be used for validation.
        """
        self.schema_store = {}
        self.load_schemas()

    def load_schemas(self) -> None:
        """
        Loads schemas into the schema store from predefined schema files (e.g., MAIN_SCHEMA, RULES_SCHEMA).

        Returns:
            None: This function does not return a value.
        """
        for schema_file in (MAIN_SCHEMA, RULES_SCHEMA):
            self.schema_store[schema_file["$id"]] = schema_file

    def get_schema(self, selected_schema: SCHEMATYPE) -> str:
        """
        Selects and sets the schema validator based on the schema ID.

        Args:
            selected_schema (SCHEMATYPE): The enum of the schema to select for validation.

        Returns:
            selected schema.

        Raises:
            ValueError: If the selected schema is not found in the schema store.
        """
        if selected_schema not in self.schema_store:
            raise ValueError(f"Schema '{selected_schema}' not found in store.")

        return self.schema_store[selected_schema]

    def get_validator(self, selected_schema: SCHEMATYPE) -> Draft202012Validator:
        """

        Args:
        selected_schema (SCHEMATYPE): The enum of the schema to select for validation.


        Returns the current schema validator.

        Returns:
            Draft202012Validator: The schema validator.
        """
        schema = self.get_schema(selected_schema)
        resolver = RefResolver.from_schema(schema, store=self.schema_store)
        return Draft202012Validator(schema, resolver=resolver)
