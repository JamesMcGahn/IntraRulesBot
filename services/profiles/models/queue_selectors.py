from dataclasses import dataclass


@dataclass
class QueueSelectors:
    queues_modal_frame: str
    queue_number_input: str
    queue_name_input: str
    queue_add_btn: str
    queue_grid_container: str
    queue_grid_rows: str
    queue_row_name_item: str
    queue_row_number_item: str
    queue_row_attribute: str
