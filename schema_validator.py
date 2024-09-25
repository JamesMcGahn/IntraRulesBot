import json
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.validators import RefResolver


class SchemaValidator:
    def __init__(self, schemas_folder, schemaId):
        self.schemas_folder = Path(schemas_folder)
        self.schema_store = {}
        self.validator = None
        self.load_schemas()
        self.select_schema(schemaId)

    def load_schemas(self):
        for schema_file in self.schemas_folder.glob("*.json"):
            with open(schema_file, "r") as file:
                schema = json.load(file)
                self.schema_store[schema["$id"]] = schema
        print(self.schema_store)

    def select_schema(self, selected_schema):
        if selected_schema not in self.schema_store:
            raise ValueError(f"Schema '{selected_schema}' not found in store.")

        main_schema = self.schema_store[selected_schema]
        resolver = RefResolver.from_schema(main_schema, store=self.schema_store)
        self.validator = Draft202012Validator(main_schema, resolver=resolver)

    def validate(self, instance):
        self.validator.validate(instance)
