RULES_SCHEMA = {
    "$id": "/schemas/rules",
    "type": "object",
    "properties": {
        "rule_name": {"type": "string", "minLength": 5},
        "guid": {"type": "string"},
        "rule_category": {"type": "string", "minLength": 5, "default": "Admin - Other"},
        "frequency_based": {
            "type": "object",
            "properties": {
                "time_interval": {"type": "number", "minimum": 1, "default": 15}
            },
            "required": ["time_interval"],
        },
        "action_based": {"$ref": "/schemas/trigger_action_based"},
        "conditions": {"type": "array", "items": {"$ref": "/schemas/conditions"}},
        "actions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "provider_category": {"type": "string", "enum": ["Communications"]},
                    "provider_instance": {"type": "string", "minLength": 3},
                    "provider_condition": {"type": "string", "minLength": 3},
                    "details": {
                        "type": "object",
                        "properties": {
                            "action_type": {"type": "string", "enum": ["email"]},
                            "email_subject": {"type": "string", "minLength": 3},
                            "email_body": {"type": "string", "minLength": 3},
                            "email_address": {
                                "type": "string",
                                "format": "email",
                                "minLength": 3,
                            },
                        },
                        "required": ["action_type"],
                        "anyOf": [
                            {
                                "if": {
                                    "properties": {"action_type": {"const": "email"}}
                                },
                                "then": {
                                    "required": [
                                        "email_subject",
                                        "email_body",
                                        "email_address",
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
            },
        },
    },
    "required": ["rule_name", "rule_category", "conditions", "actions"],
    "anyOf": [{"required": ["frequency_based"]}, {"required": ["action_based"]}],
}
