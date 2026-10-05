from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.browser.ports import InteractionPort
    from services.api.queues.models import (
        ProviderInfo,
        ProviderInstanceInfo,
        CustomResource,
    )
from dataclasses import dataclass


@dataclass
class QueueRunnerState:
    form_port: InteractionPort | None = None
    queue_port: InteractionPort | None = None
    provider_info: ProviderInfo | None = None
    provider_instance: ProviderInstanceInfo | None = None
    queue_custom_resource: CustomResource | None = None
