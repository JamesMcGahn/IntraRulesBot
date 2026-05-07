from ..auth.enums import PROVIDERS

from ..auth.session.base_provider_session import BaseProviderSession


class IntraProviderSession(BaseProviderSession):

    def __init__(self, logger):
        super().__init__(logger=logger)

    class Config:
        provider_name = PROVIDERS.INTRA
        has_token = False
        has_cookies = True
        has_auth_cookies = True
        auth_cookies = {"KnowlagentAccessMT", ".Knowlagent", "ASP.NET_SessionId"}
        domains = {"intradiem.com"}
