# patern validate_{field_name}

from ..enums import SETTINGSCATEGORIES
from .validator_helper import ValidatorHelper

helper = ValidatorHelper(SETTINGSCATEGORIES.LOGIN)


def validate_user_name(field, value):
    return helper.settings_response(field, value, helper.not_blank(value))


def validate_password(field, value):
    return helper.settings_response(field, value, helper.not_blank(value))


def validate_tenant(field, value):
    return helper.settings_response(field, value, helper.not_blank(value))


def validate_platform_version(field, value):
    return helper.settings_response(field, value, value in ["V10", "V11"])
