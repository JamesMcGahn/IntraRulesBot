CONDITIONS_SCHEMA = {
    "$id": "/schemas/conditions",
    "type": "object",
    "properties": {
        "provider_category": {"type": "string", "enum": ["ACD", "WFM"]},
        "provider_instance": {"type": "string", "minLength": 3},
        "provider_condition": {"type": "string", "minLength": 3},
        "details": {
            "type": "object",
            "properties": {
                "condition_type": {
                    "type": "string",
                    "enum": ["stats"],
                },
                "equality_operator": {
                    "type": "string",
                    "enum": [
                        "Equal To",
                        "Greater Than",
                        "Greater Than or Equal To",
                        "Less Than",
                        "Less Than or Equal To",
                        "Not Equal To",
                    ],
                },
                "equality_threshold": {"type": "number", "minimum": 1},
                "queues_source": {
                    "type": "string",
                    "enum": ["queues", "users"],
                },
            },
            "required": ["condition_type"],
            "anyOf": [
                {
                    "if": {"properties": {"condition_type": {"const": "stats"}}},
                    "then": {
                        "required": [
                            "equality_operator",
                            "equality_threshold",
                            "queues_source",
                        ]
                    },
                }
            ],
        },
    },
    "required": [
        "provider_category",
        "provider_instance",
        "provider_condition",
        "details",
    ],
}
