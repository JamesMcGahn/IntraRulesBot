from ..enums import SETTINGSCATEGORIES
from .validator_helper import ValidatorHelper

helper = ValidatorHelper(SETTINGSCATEGORIES.BROWSER)


def validate_browser_move_delay_speed(field, value):
    success_error = helper.is_int(value) and int(value) >= 500
    display_field = field.replace("_", " ").title()
    msg = (
        f"{display_field} is valid."
        if success_error
        else "Value must be an integer greater than 500."
    )
    f"{display_field} is valid."
    return helper.settings_response(field, value, success_error, msg)


def validate_browser_headless(field, value):
    return helper.settings_response(field, value, True)
