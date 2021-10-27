from typing import Type, TypeVar, Callable, Tuple
import collections

import grpc  # type: ignore

from grpc_boilerplate.constants import API_TOKEN_HEADER
from grpc_boilerplate.connectionstring import parse_grpc_connectionstring


ApiStub = TypeVar('ApiStub')


class _ClientCallDetails(
    collections.namedtuple('_ClientCallDetails', ('method', 'timeout', 'metadata', 'credentials')),
    grpc.aio.ClientCallDetails
):
    pass


def _token_auth(header: str, token: str) -> grpc.aio.UnaryUnaryClientInterceptor:
    class AuthInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
        async def intercept_unary_unary(self, continuation, client_call_details, request):
            metadata = []
            if client_call_details.metadata is not None:
                metadata = list(client_call_details.metadata)
            metadata.append((header, token))
            client_call_details = _ClientCallDetails(
                client_call_details.method, client_call_details.timeout, metadata, client_call_details.credentials)
            return continuation(client_call_details, request)

    return AuthInterceptor()


# Create grpc.aio client from connection_string
# see grpc_boilerplate.connectionstring.parse_grpc_connectionstring for connectionstring format
# Returns stub instance, close function
def api_stub(
    connection_string: str,
    stub: Type[ApiStub],
    api_token_header=API_TOKEN_HEADER,
) -> Tuple[ApiStub, Callable[[], None]]:
    parsed = parse_grpc_connectionstring(connection_string=connection_string)

    if parsed.is_secure():
        assert parsed.server_crt is not None
        with open(parsed.server_crt, 'rb') as f:
            creds = grpc.ssl_channel_credentials(f.read())
        channel = grpc.aio.secure_channel(f"{parsed.host}:{parsed.port}", creds)
    else:
        channel = grpc.aio.insecure_channel(f"{parsed.host}:{parsed.port}")

    if parsed.api_token:
        assert parsed.api_token is not None
        channel = grpc.intercept_channel(channel, _token_auth(api_token_header, parsed.api_token))

    return stub(channel), lambda: channel.close()  # type: ignore
