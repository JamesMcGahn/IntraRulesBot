MAIN_SCHEMA = {
    "$id": "/schemas/main",
    "type": "object",
    "properties": {
        "rule_set_name": {"type": "string", "minLength": 5},
        "description": {"type": "string"},
        "guid": {"type": "string"},
        "rules": {"type": "array", "items": {"$ref": "/schemas/rules"}},
    },
    "required": ["rule_set_name", "description", "rules"],
}
