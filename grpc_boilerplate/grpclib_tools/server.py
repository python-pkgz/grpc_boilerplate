import logging
import ssl
from typing import TYPE_CHECKING, List, Any, Dict, Optional, Union
from ipaddress import IPv4Network, IPv6Network

from grpclib.health.service import Health
from grpclib.server import Server as GRPCLibServer
from grpclib.utils import graceful_exit

from grpc_boilerplate.grpclib_tools.server_middlewares import attach_middlewares
from grpc_boilerplate.constants import API_TOKEN_HEADER, TLS_CLIENT_CRT, TLS_CLIENT_KEY, TLS_TRUSTED_CERTS
from grpc_boilerplate.grpclib_tools.tls import create_secure_context

if TYPE_CHECKING:
    from grpclib._typing import IServable  # noqa


logger = logging.getLogger(__name__)


class Server:
    def __init__(
        self,
        handlers: List['IServable'],

        # grpclib.server.Server kwargs
        server_kwargs: Optional[Dict[str, Any]] = None,

        # Token auth middleware
        api_token: str = "",
        api_token_header: str = API_TOKEN_HEADER,

        # Peer whitelist middleware
        peer_whitelist: List[Union[IPv4Network, IPv6Network]] = [],
    ):
        if server_kwargs is None:
            server_kwargs = dict()

        handlers.append(Health())
        self.server: GRPCLibServer = GRPCLibServer(handlers=handlers, **server_kwargs)
        attach_middlewares(
            server=self.server,
            api_token=api_token, api_token_header=api_token_header,
            peer_whitelist=peer_whitelist
        )

        self._ssl_ctx: Optional[ssl.SSLContext] = None

    def create_tls_context(
        self,
        tls_client_cert=TLS_CLIENT_CRT,
        tls_client_key=TLS_CLIENT_KEY,
        tls_trusted_certs=TLS_TRUSTED_CERTS,
    ):
        self._ssl_ctx = create_secure_context(
            client_cert=tls_client_cert,
            client_key=tls_client_key,
            trusted_certs=tls_trusted_certs,
        )

    async def serve(
        self,
        host: str = 'localhost',
        port: int = 50000,
    ):
        with graceful_exit([self.server]):
            await self.server.start(host, port, ssl=self._ssl_ctx)
            logger.debug(f'Serving on {host}:{port}')
            await self.server.wait_closed()
