import json


class RuleStore:

    def __init__(self):
        pass

    def load_from_json(self, file_path: str):
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
            return data, None
        except json.JSONDecodeError as e:
            message = f"JSON error in the file {file_path} - {str(e)}"
            return None, message
        except Exception as e:
            message = f"Error in the file {file_path} - {str(e)}"
            return None, message

    def save(self, data: dict, file_path: str):
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            return True, None
        except Exception as e:
            message = f"Error saving the file {file_path} - {str(e)}"
            return True, message
