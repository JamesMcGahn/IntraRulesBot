from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.logger.adapters import LogAdapter
    from services.network.network_client import NetworkClient
    from services.network.models import NetworkResponse
    from requests import Response

from PySide6.QtCore import Slot, Signal
from services.network.base_api import BaseApi
from services.network.models import NetworkRequest
from services.network.enums import HTTPMETHOD, AUTHMODE
from .models import ProviderInfo, ProviderInstanceInfo
from services.queues.models import Queue


class V11QueueApi(BaseApi):
    token_failed = Signal()
    token_response = Signal(object)

    def __init__(self, logger: LogAdapter, network_client: NetworkClient):
        super().__init__(logger, network_client)
        self.token_fetch_in_progress = False

    def get_providers(self, tenant: str) -> list[ProviderInfo]:
        url = f"https://{tenant}providerapi.intradiem.com/api/definitions/providers?$skip=0&$top=500"
        self._logging(f"Sending Request to url: {url}", "DEBUG")
        request = NetworkRequest(
            method=HTTPMETHOD.GET,
            url=url,
            auth_mode=AUTHMODE.BEARER,
        )
        response = self._execute(request)
        self._logging(f"Received Response: {response}", "DEBUG")
        providers = response.data.get("value", [])
        # print(providers)
        found_providers = []
        for provider in providers:

            parameters = provider.get("parameters", [])
            queue_parm = [
                parm
                for parm in parameters
                if parm.get("name") == "id_manage_acd_queues"
            ]

            prov = ProviderInfo(
                provider.get("id", 0),
                provider.get("name", "No Name"),
                provider.get("category", "Other"),
                queue_parm[0].get("id") if queue_parm else None,
            )
            found_providers.append(prov)
        return found_providers

    def get_provider_instances(
        self, tenant: str, provider_info: ProviderInfo
    ) -> list[ProviderInstanceInfo]:
        url = f"https://{tenant}providerapi.intradiem.com/api/instances/providers?$filter=providerDefinitionId%20eq%20{provider_info.id}"
        self._logging(f"Sending Request to url: {url}", "DEBUG")
        request = NetworkRequest(
            method=HTTPMETHOD.GET,
            url=url,
            auth_mode=AUTHMODE.BEARER,
        )
        response = self._execute(request)
        self._logging(f"Received Response: {response}", "DEBUG")
        instances = response.data.get("value", [])

        found_instances = []
        for instance in instances:
            queues = instance.get("id_manage_acd_queues", False) or instance.get(
                provider_info.manage_queue_id, []
            )
            queue_list = [
                Queue(
                    queue["queue_id"],
                    queue["queue_name"],
                    queue["queue_number"],
                    0,
                    "",
                    "",
                )
                for queue in queues
            ]
            ins = ProviderInstanceInfo(
                instance.get("id", 0), instance.get("name", "No Name"), queue_list
            )
            found_instances.append(ins)

        return found_instances
