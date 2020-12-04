from typing import Type, Optional, Protocol

import urllib.parse

from grpclib.client import Channel
from grpclib.events import SendRequest, listen

from grpc_boilerplate.constants import API_TOKEN_HEADER, TLS_CLIENT_CRT, TLS_CLIENT_KEY, TLS_TRUSTED_CERTS
from grpc_boilerplate.grpclib_tools.tls import create_secure_context


class ApiStub(Protocol):
    def __init__(self, channel: Channel):
        pass


def api_stub(
    connection_string: str,
    stub: Type[ApiStub],

    tls_client_cert=TLS_CLIENT_CRT,
    tls_client_key=TLS_CLIENT_KEY,
    tls_trusted_certs=TLS_TRUSTED_CERTS,
) -> ApiStub:
    parsed = urllib.parse.urlparse(connection_string, allow_fragments=False)
    host: str = parsed.hostname or 'localhost'
    port: int = parsed.port or 50000
    token: Optional[str] = parsed.username or None

    if parsed.scheme == 'h2c':
        ssl_ctx = None
    elif parsed.scheme == 'h2cs':
        ssl_ctx = create_secure_context(
            client_cert=tls_client_cert,
            client_key=tls_client_key,
            trusted_certs=tls_trusted_certs
        )
    else:
        raise ValueError(
            f"Unknown scheme: '{parsed.scheme}' for '{connection_string}'"
        )

    channel = Channel(host, int(port), ssl=ssl_ctx)

    if token is not None:
        async def on_send_request(event: SendRequest) -> None:
            assert token is not None
            event.metadata[API_TOKEN_HEADER] = token
        listen(channel, SendRequest, on_send_request)

    return stub(channel)
