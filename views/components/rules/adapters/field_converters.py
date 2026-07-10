def to_int_or_original(value: str) -> int | str:
    if value.isdigit():
        return int(value)
    return value


def comma_string_to_list(value: str) -> list[str]:
    return value.split(",")


FIELD_CONVERTERS = {
    "time_interval": to_int_or_original,
    "equality_threshold": to_int_or_original,
    "lead_time": to_int_or_original,
    "segment_codes": comma_string_to_list,
    "segment_offset": to_int_or_original,
    "segment_duration": to_int_or_original,
}
