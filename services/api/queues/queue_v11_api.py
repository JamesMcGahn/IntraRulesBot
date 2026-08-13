from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.logger.adapters import LogAdapter
    from services.network.network_client import NetworkClient
    from services.network.network_throttle import NetworkThrottle

from PySide6.QtCore import Signal
from services.network.base_api import BaseApi
from services.network.models import NetworkRequest
from services.network.enums import HTTPMETHOD, AUTHMODE
from .models import (
    ProviderInfo,
    ProviderInstanceInfo,
    CustomResource,
    ProviderStatistics,
    ProviderQueue,
)
from services.queues.models import Queue

from urllib.parse import quote


class V11QueueApi(BaseApi):
    token_failed = Signal()
    token_response = Signal(object)

    def __init__(
        self,
        logger: LogAdapter,
        network_client: NetworkClient,
        network_throttle: NetworkThrottle,
    ):
        super().__init__(logger, network_client)
        self.token_fetch_in_progress = False
        self._network_throttle = network_throttle

    def get_providers(self, tenant: str) -> list[ProviderInfo]:
        url = f"https://{tenant}providerapi.intradiem.com/api/definitions/providers?$skip=0&$top=500"

        request = NetworkRequest(
            method=HTTPMETHOD.GET,
            url=url,
            headers={"x-api-version": "2"},
            auth_mode=AUTHMODE.BEARER,
        )

        self._network_throttle.wait()
        response = self._execute(request)

        providers = response.data.get("value", [])
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

        filter_value = quote(
            f"providerDefinitionId eq {provider_info.id}",
            safe="",
        )
        url = f"https://{tenant}providerapi.intradiem.com/api/instances/providers?$filter={filter_value}"

        request = NetworkRequest(
            method=HTTPMETHOD.GET,
            url=url,
            headers={"x-api-version": "2"},
            auth_mode=AUTHMODE.BEARER,
        )
        self._network_throttle.wait()
        response = self._execute(request)

        instances = response.data.get("value", [])

        found_instances = []
        for instance in instances:
            ins = self._process_provider_payload(instance)
            found_instances.append(ins)
        return found_instances

    def get_custom_resources(
        self, tenant: str, provider_info: ProviderInfo
    ) -> list[CustomResource]:
        filter_value = quote(
            f"providerDefinitionId eq {provider_info.id}",
            safe="",
        )
        url = f"https://{tenant}providerapi.intradiem.com/api/definitions/customResources?$filter={filter_value}"
        request = NetworkRequest(
            method=HTTPMETHOD.GET,
            url=url,
            headers={"x-api-version": "2"},
            auth_mode=AUTHMODE.BEARER,
        )
        self._network_throttle.wait()
        response = self._execute(request)

        values = response.data.get("value", [])
        return [
            CustomResource(
                resource.get("id", ""),
                resource.get("name", ""),
                resource.get("providerDefinitionId", ""),
            )
            for resource in values
        ]

    def add_queue(
        self,
        tenant: str,
        queue_resource: CustomResource,
        provider_instance: ProviderInstanceInfo,
        queue: Queue,
    ):
        url = f"https://{tenant}.intradiem.com/api/instances/customResources({queue.guid})"
        request = NetworkRequest(
            method=HTTPMETHOD.PATCH,
            url=url,
            auth_mode=AUTHMODE.BEARER,
            headers={"x-api-version": "2"},
            json={
                "customResourceDefinitionId": f"{queue_resource.id}",
                "providerInstanceId": f"{provider_instance.id}",
                "queue_name": f"{queue.queue_name}",
            },
        )
        self._network_throttle.wait()
        response = self._execute(request)

        if response.status == 204:
            return True
        else:
            return False

    def get_provider(self, tenant: str, provider_instance: ProviderInstanceInfo):
        url = f"https://{tenant}providerapi.intradiem.com/api/instances/providers({provider_instance.id})"
        request = NetworkRequest(
            method=HTTPMETHOD.GET,
            url=url,
            headers={"x-api-version": "2"},
            auth_mode=AUTHMODE.BEARER,
        )

        return self._process_provider_payload(request.data)

    def _process_provider_payload(self, payload: dict) -> ProviderInstanceInfo:
        queues = payload.get("id_manage_acd_queues", [])
        queue_list = [
            ProviderQueue(
                queue["queue_name"],
                queue["queue_number"],
                queue["queue_id"],
                queue["@odata.type"],
            )
            for queue in queues
        ]
        stats = payload.get("id_statistics_monitored", [])
        stats_list = [
            ProviderStatistics(
                stat["key"],
                stat["value"],
                stat["@odata.type"],
            )
            for stat in stats
        ]

        return ProviderInstanceInfo(
            id=payload.get("id", 0),
            name=payload.get("name", "No Name"),
            providerDefinitionId=payload.get("providerDefinitionId", ""),
            description=payload.get("description", ""),
            queue_list=queue_list,
            stats_monitored=stats_list,
        )
