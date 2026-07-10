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
                    "enum": ["stats", "segment_codes"],
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
                "segment_codes": {
                    "type": "array",
                    "minItems": 1,
                    "items": {"type": "string"},
                },
                "match_mode": {
                    "type": "string",
                    "enum": ["Any", "All"],
                },
                "segment_time_interval": {
                    "type": "string",
                    "enum": ["Duration", "Start and End Time"],
                },
                "segment_start_time": {
                    "type": "string",
                    "enum": [
                        "Rule Runtime",
                        "Rule Runtime Minus",
                        "Rule Runtime Plus",
                        "Shift Start Time",
                        "VTO Request Start Time",
                    ],
                },
                "segment_offset": {"type": "number", "minimum": 1, "default": 5},
                "segment_end_time": {
                    "type": "string",
                    "enum": [
                        "Shift End Time",
                        "VTO Request End Time",
                    ],
                },
                "segment_duration": {"type": "number", "minimum": 1, "default": 5},
                "segment_occurrence": {
                    "type": "string",
                    "enum": [
                        "Any Part of Segment",
                        "Entire Segment",
                        "Segment End",
                        "Segment Start",
                    ],
                },
                "user_list": {
                    "type": "string",
                    "default": "All Users",
                    "minLength": 3,
                },
            },
            "required": ["condition_type"],
            "allOf": [
                {
                    "if": {"properties": {"condition_type": {"const": "stats"}}},
                    "then": {
                        "required": [
                            "equality_operator",
                            "equality_threshold",
                            "queues_source",
                        ]
                    },
                },
                {
                    "if": {
                        "properties": {"condition_type": {"const": "segment_codes"}}
                    },
                    "then": {
                        "required": [
                            "equality_operator",
                            "segment_codes",
                            "match_mode",
                            "segment_time_interval",
                            "segment_start_time",
                            "segment_occurrence",
                            "user_list",
                        ],
                        "properties": {
                            "equality_operator": {
                                "enum": [
                                    "Equal To",
                                    "Not Equal To",
                                ]
                            }
                        },
                    },
                },
                {
                    "if": {
                        "properties": {"segment_time_interval": {"const": "Duration"}},
                        "required": ["condition_type", "segment_time_interval"],
                    },
                    "then": {
                        "required": [
                            "segment_duration",
                        ],
                    },
                },
                {
                    "if": {
                        "properties": {
                            "segment_time_interval": {"const": "Start and End Time"},
                        },
                        "required": ["condition_type", "segment_time_interval"],
                    },
                    "then": {
                        "required": [
                            "segment_end_time",
                        ],
                    },
                },
                {
                    "if": {
                        "properties": {
                            "segment_start_time": {
                                "enum": [
                                    "Rule Runtime Minus",
                                    "Rule Runtime Plus",
                                ],
                            }
                        },
                        "required": ["condition_type", "segment_start_time"],
                    },
                    "then": {
                        "required": [
                            "segment_offset",
                        ],
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
                    "details": {"properties": {"condition_type": {"enum": ["stats"]}}}
                }
            },
        },
        {
            "if": {"properties": {"provider_category": {"const": "WFM"}}},
            "then": {
                "properties": {
                    "details": {
                        "properties": {"condition_type": {"enum": ["segment_codes"]}}
                    }
                }
            },
        },
    ],
}
