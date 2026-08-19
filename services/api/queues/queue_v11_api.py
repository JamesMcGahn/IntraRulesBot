from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from services.logger.adapters import LogAdapter
    from services.network.network_client import NetworkClient
    from services.network.network_throttle import NetworkThrottle

from services.network.base_api import BaseApi
from services.network.models import NetworkRequest, NetworkResponse
from services.network.enums import HTTPMETHOD, AUTHMODE
from .models import (
    ProviderInfo,
    ProviderInstanceInfo,
    CustomResource,
    ProviderStatistics,
    ProviderQueue,
)
from services.queues.models import Queue
from base.errors import (
    NotAuthenticatedException,
    RetryableNetworkException,
    NetworkResponseException,
)
from urllib.parse import quote


class V11QueueApi(BaseApi):

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
        self._handle_response(response)

        providers = response.data.get("value", [])
        found_providers = []

        for provider in providers:
            prov = ProviderInfo(
                provider.get("id", 0),
                provider.get("name", "No Name"),
                provider.get("category", "Other"),
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
        self._handle_response(response)

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
        self._handle_response(response)

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
    ) -> None:
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
        self._handle_response(response)

    def get_provider_instance(
        self, tenant: str, provider_instance: ProviderInstanceInfo
    ) -> ProviderInstanceInfo:
        url = f"https://{tenant}providerapi.intradiem.com/api/instances/providers({provider_instance.id})"
        request = NetworkRequest(
            method=HTTPMETHOD.GET,
            url=url,
            headers={"x-api-version": "2"},
            auth_mode=AUTHMODE.BEARER,
        )

        self._network_throttle.wait()
        response = self._execute(request)
        self._handle_response(response)
        return self._process_provider_payload(response.data)

    def update_provider_instance_settings(
        self, tenant: str, provider_instance: ProviderInstanceInfo, queue: Queue
    ):
        payload = self._build_provider_settings_payload(provider_instance, queue)
        url = f"https://{tenant}providerapi.intradiem.com/api/instances/providers({provider_instance.id})"
        request = NetworkRequest(
            method=HTTPMETHOD.PATCH,
            url=url,
            headers={"x-api-version": "2"},
            json=payload,
            auth_mode=AUTHMODE.BEARER,
        )

        self._network_throttle.wait()
        response = self._execute(request)
        self._handle_response(response)

    def _build_provider_settings_payload(
        self, provider_instance: ProviderInstanceInfo, queue: Queue
    ) -> dict[str, Any]:
        queue_list = [
            {
                "@odata.type": queue.odata_type,
                "queue_name": queue.queue_name,
                "queue_number": queue.queue_number,
                "queue_id": queue.queue_id,
            }
            for queue in provider_instance.queue_list
        ]

        queue_list.append(
            {
                "@odata.type": "#com.intradiem.enterprise.edm.instances.QueueList",
                "queue_name": queue.queue_name,
                "queue_number": queue.queue_name,
                "queue_id": queue.guid,
            }
        )

        return {
            "id_manage_acd_queues": queue_list,
            "id_manage_acd_queues@odata.type": provider_instance.id_manage_acd_queues_odata_type,
            "name": provider_instance.name,
            "description": provider_instance.description,
            "providerDefinitionId": provider_instance.providerDefinitionId,
            "id": provider_instance.id,
        }

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

    def _handle_response(self, response: NetworkResponse):

        if response.ok:
            return

        match response.status:
            case 0:
                raise NetworkResponseException
            case 401:
                raise NotAuthenticatedException
            case 429:
                retry_after = response.headers.get("Retry-After")

                if retry_after:
                    delay = self._client.parse_retry_after_time(retry_after)
                    self._network_throttle.delay(delay)

                self._network_throttle.increase_wait_interval()
                raise RetryableNetworkException
            case 408 | 500 | 502 | 503 | 504:
                self._network_throttle.delay(5.0)
                raise RetryableNetworkException
            case status if status >= 400:
                raise NetworkResponseException
