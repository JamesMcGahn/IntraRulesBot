from dataclasses import dataclass


@dataclass
class LoginSelectors:
    user_name_input: str
    password_input: str
    submit_button: str
    error_container: str
    main_page_container: str
    logged_out_session: str
