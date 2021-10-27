from typing import Type, TypeVar, Tuple, Callable

from grpclib.client import Channel
from grpclib.events import SendRequest, listen

from grpc_boilerplate.constants import API_TOKEN_HEADER
from grpc_boilerplate.connectionstring import parse_grpc_connectionstring

ApiStub = TypeVar('ApiStub')


def api_stub(
    connection_string: str,
    stub: Type[ApiStub],
    api_token_header=API_TOKEN_HEADER,
) -> Tuple[ApiStub, Callable[[], None]]:
    """
    Create grpclib client from connection_string
    see grpc_boilerplate.connectionstring.parse_grpc_connectionstring for connectionstring format
    Returns stub instance, close function
    """

    parsed = parse_grpc_connectionstring(connection_string=connection_string)

    if parsed.is_secure():
        raise ValueError("secure channels is not supported")

    channel = Channel(parsed.host, parsed.port)

    if parsed.api_token:
        async def on_send_request(event: SendRequest) -> None:
            assert parsed.api_token is not None
            event.metadata[api_token_header] = parsed.api_token
        listen(channel, SendRequest, on_send_request)

    return stub(channel), lambda: channel.close()  # type: ignore
