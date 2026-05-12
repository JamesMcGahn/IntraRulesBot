from ...base import FieldRegistry


class SettingsFieldRegistry(FieldRegistry):

    def __init__(self):
        super().__init__()

    def get_line_edit_text(self, key, tab=None):
        if tab:
            line_edit = self.get_text_value(f"{tab}/line_edit_{key}")
        else:
            line_edit = self.get_text_value(f"line_edit_{key}")
        return line_edit

    def get_combo_box_text(self, key, tab=None):
        if tab:
            combo_box = self.get_text_value(f"{tab}/combo_box_{key}")
        else:
            combo_box = self.get_text_value(f"combo_box_{key}")
        return combo_box

    def get_text_edit_text(self, key, tab=None):
        if tab:
            textEdit = self.get_text_value(f"{tab}/text_edit_{key}")
        else:
            textEdit = self.get_text_value(f"text_edit_{key}")
        return textEdit
