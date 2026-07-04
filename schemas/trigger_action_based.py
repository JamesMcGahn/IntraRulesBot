TRIGGER_ACTION_BASED = {
    "$id": "/schemas/trigger_action_based",
    "type": "object",
    "properties": {
        "provider_category": {"type": "string", "enum": ["ACD", "Intradiem", "WFM"]},
        "provider_instance": {"type": "string", "minLength": 3},
        "provider_condition": {"type": "string", "minLength": 3},
        "details": {
            "type": "object",
            "properties": {
                "action_type": {
                    "type": "string",
                    "enum": [
                        "state_changed",
                        "user_logged_in",
                        "user_logged_out",
                        "time_in_state",
                        "quick_action",
                        "segment_occurrence",
                    ],
                },
                "state": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "state": {"type": "string", "minLength": 5},
                            "aux": {"type": "string"},
                        },
                        "required": ["state", "aux"],
                    },
                },
                "equality_operator": {
                    "type": "string",
                    "enum": ["Equal To", "Not Equal To"],
                },
                "aux_equality_operator": {
                    "type": "string",
                    "enum": ["Equal To", "Not Equal To"],
                },
                "equality_threshold": {"type": "number", "minimum": 1},
                "user_list": {
                    "type": "string",
                    "default": "All Users",
                    "minLength": 3,
                },
                "quick_action_name": {
                    "type": "string",
                    "minLength": 3,
                },
                "segment_codes": {
                    "type": "array",
                    "minItems": 1,
                    "items": {"type": "string"},
                },
                "lead_time": {"type": "number", "minimum": 1, "default": 5},
                "lookup_operator": {
                    "type": "string",
                    "enum": ["Before", "After"],
                },
                "segment_lookup": {
                    "type": "string",
                    "enum": ["Segment Start", "Segment End"],
                },
            },
            "required": ["action_type"],
            "allOf": [
                {
                    "if": {"properties": {"action_type": {"const": "state_changed"}}},
                    "then": {"required": ["state", "equality_operator", "user_list"]},
                },
                {
                    "if": {"properties": {"action_type": {"const": "time_in_state"}}},
                    "then": {
                        "required": [
                            "state",
                            "equality_operator",
                            "equality_threshold",
                            "user_list",
                            "aux_equality_operator",
                        ]
                    },
                },
                {
                    "if": {"properties": {"action_type": {"const": "user_logged_in"}}},
                    "then": {"required": ["user_list"]},
                },
                {
                    "if": {"properties": {"action_type": {"const": "user_logged_out"}}},
                    "then": {"required": ["user_list"]},
                },
                {
                    "if": {"properties": {"action_type": {"const": "quick_action"}}},
                    "then": {"required": ["quick_action_name"]},
                },
                {
                    "if": {
                        "properties": {"action_type": {"const": "segment_occurrence"}}
                    },
                    "then": {
                        "required": [
                            "segment_codes",
                            "lead_time",
                            "lookup_operator",
                            "segment_lookup",
                            "user_list",
                        ]
                    },
                },
            ],
        },
    },
    "required": [
        "provider_category",
        "provider_instance",
        "provider_condition",
        "details",
    ],
    "allOf": [
        {
            "if": {"properties": {"provider_category": {"const": "ACD"}}},
            "then": {
                "properties": {
                    "details": {
                        "properties": {
                            "action_type": {
                                "enum": [
                                    "state_changed",
                                    "user_logged_in",
                                    "user_logged_out",
                                    "time_in_state",
                                ]
                            }
                        }
                    }
                }
            },
        },
        {
            "if": {"properties": {"provider_category": {"const": "Intradiem"}}},
            "then": {"properties": {"provider_instance": {"enum": ["Users"]}}},
        },
        {
            "if": {"properties": {"provider_instance": {"const": "Users"}}},
            "then": {
                "properties": {
                    "provider_condition": {"enum": ["Quick Action Button Clicked"]}
                }
            },
        },
    ],
}
