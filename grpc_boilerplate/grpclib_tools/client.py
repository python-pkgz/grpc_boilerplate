from typing import Optional, Type, TypeVar

import ssl
from grpclib.client import Channel
from grpclib.events import SendRequest, listen

from grpc_boilerplate.constants import API_TOKEN_HEADER
from grpc_boilerplate.grpclib_tools.tls import create_secure_context
from grpc_boilerplate.connectionstring import parse_grpc_connectionstring

ApiStub = TypeVar('ApiStub')


# Parse grpc connectionstring `h2c|h2cs://[<token>@]host:port[?ServerCrt=<path to server cert>]`
# Attempt to create generic connectionstring format for grpc connections
def api_stub(
    connection_string: str,
    stub: Type[ApiStub],
    api_token_header=API_TOKEN_HEADER,
) -> ApiStub:
    parsed = parse_grpc_connectionstring(connection_string=connection_string)

    ssl_ctx: Optional[ssl.SSLContext] = None
    if parsed.is_secure():
        assert parsed.server_crt is not None
        ssl_ctx = create_secure_context(crt=parsed.server_crt)

    channel = Channel(parsed.host, parsed.port, ssl=ssl_ctx)

    if parsed.api_token:
        async def on_send_request(event: SendRequest) -> None:
            assert parsed.api_token is not None
            event.metadata[api_token_header] = parsed.api_token
        listen(channel, SendRequest, on_send_request)

    return stub(channel)  # type: ignore
