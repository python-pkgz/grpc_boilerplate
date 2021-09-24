import logging
from typing import List, Union
from ipaddress import ip_address, IPv4Network, IPv6Network

from grpclib.const import Status
from grpclib.events import RecvRequest, listen
from grpclib.exceptions import GRPCError
from grpclib.server import Server

from grpc_boilerplate.constants import API_TOKEN_HEADER


logger = logging.getLogger(__name__)


def attach_check_peer_method(
    event,
    address_whitelist: List[Union[IPv4Network, IPv6Network]]
):
    method_func = event.method_func

    async def wrapper(stream):
        address_str = stream._stream._transport.get_extra_info('peername')[0]
        address = ip_address(address_str)

        for network in address_whitelist:
            if address in network:
                return await method_func(stream)
        logger.warning(f"{address} not in whitelist. Blocking.")
        raise GRPCError(Status.UNAUTHENTICATED)

    event.method_func = wrapper


def attach_token_auth(event, api_header: str, api_token: str):
    method_func = event.method_func

    async def wrapper(stream):
        if event.metadata.get(api_header, "") != api_token and stream._method_name != '/grpc.health.v1.Health/Check':
            raise GRPCError(Status.UNAUTHENTICATED)
        return await method_func(stream)

    event.method_func = wrapper


def attach_middlewares(
    server: Server,
    api_token: str = "",
    api_token_header: str = API_TOKEN_HEADER,
    peer_whitelist: List[Union[IPv4Network, IPv6Network]] = [],
):
    if api_token and api_token_header:
        logger.info("api token middleware attached")
    else:
        logger.info("api token middleware NOT attached")

    if peer_whitelist:
        logger.info(f"peer whitelist middleware attached with networks: {peer_whitelist}")
    else:
        logger.info("peer whitelist middleware NOT attached")

    async def recv_request(event: RecvRequest):
        # Middlewares called in reversed order
        if api_token and api_token_header:
            attach_token_auth(event, api_header=api_token_header, api_token=api_token)

        if peer_whitelist:
            attach_check_peer_method(event, address_whitelist=peer_whitelist)

    listen(server, RecvRequest, recv_request)
