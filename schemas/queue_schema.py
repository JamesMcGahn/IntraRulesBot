QUEUE_SCHEMA = {
    "$id": "/schemas/queue",
    "type": "object",
    "properties": {
        "queue_name": {"type": "string", "minLength": 1},
        "queue_number": {"type": "string", "minLength": 1},
        "guid": {"type": "string"},
        "action_type": {
            "type": "string",
            "enum": ["ADD", "VERIFY_EXISTS", "VERIFY_NOT_EXISTS", "DELETE"],
            "default": "ADD",
        },
    },
    "required": ["queue_name", "queue_number"],
}
