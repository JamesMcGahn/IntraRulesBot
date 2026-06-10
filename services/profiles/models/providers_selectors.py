from dataclasses import dataclass


@dataclass
class ProviderSelectors:
    page_path: str
    category_items: str
    category_header: str
    provider_cards: str
    provider_name: str
    provider_edit_button: str
    acd_category_title: str
    switch_instance_alert_text: str
