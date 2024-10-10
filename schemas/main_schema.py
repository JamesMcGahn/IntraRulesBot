MAIN_SCHEMA = {
  "$id": "/schemas/main",
  "type": "object",
  "properties": {
    "rules": {
      "type": "array",
      "items": {
        "$ref": "/schemas/rules"
      }
    }
  },
  "required": ["rules"]
}