from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .provider_queue import ProviderQueue
    from .provider_stats import ProviderStatistics

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProviderInstanceInfo:
    id: str
    name: str
    providerDefinitionId: str
    description: str
    queue_list: list[ProviderQueue] = field(default_factory=list)
    stats_monitored: list[ProviderStatistics] = field(default_factory=list)
    id_statistics_monitored_odata_type: str = (
        "#Collection(com.intradiem.enterprise.edm.instances.KeyValue)"
    )

    id_manage_acd_queues_odata_type: str = (
        "#Collection(com.intradiem.enterprise.edm.instances.QueueList)"
    )
