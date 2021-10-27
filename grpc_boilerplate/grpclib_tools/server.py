import logging
from typing import TYPE_CHECKING, List, Any, Dict, Optional, Union
from ipaddress import IPv4Network, IPv6Network

from grpclib.health.service import Health
from grpclib.server import Server as GRPCLibServer
from grpclib.utils import graceful_exit

from grpc_boilerplate.grpclib_tools.server_middlewares import attach_middlewares
from grpc_boilerplate.constants import API_TOKEN_HEADER

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

    async def serve(
        self,
        host: str = 'localhost',
        port: int = 50000,
    ):
        with graceful_exit([self.server]):
            await self.server.start(host, port)
            logger.debug(f'Serving on {host}:{port}')
            await self.server.wait_closed()
