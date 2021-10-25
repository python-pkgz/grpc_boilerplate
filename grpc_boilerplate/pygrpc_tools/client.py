from typing import Type, TypeVar
import collections

import grpc  # type: ignore

from grpc_boilerplate.constants import API_TOKEN_HEADER
from grpc_boilerplate.connectionstring import parse_grpc_connectionstring


ApiStub = TypeVar('ApiStub')


class _ClientCallDetails(
    collections.namedtuple('_ClientCallDetails', ('method', 'timeout', 'metadata', 'credentials')),
    grpc.ClientCallDetails
):
    pass


def _token_auth(header: str, token: str) -> grpc.UnaryUnaryClientInterceptor:
    class AuthInterceptor(grpc.UnaryUnaryClientInterceptor):
        def intercept_unary_unary(self, continuation, client_call_details, request):
            metadata = []
            if client_call_details.metadata is not None:
                metadata = list(client_call_details.metadata)
            metadata.append((header, token))
            client_call_details = _ClientCallDetails(
                client_call_details.method, client_call_details.timeout, metadata, client_call_details.credentials)
            return continuation(client_call_details, request)

    return AuthInterceptor()


# Parse grpc connectionstring `h2c|h2cs://[<token>@]host:port[?ServerCrt=<path to server cert>]`
# Attempt to create generic connectionstring format for grpc connections
def api_stub(
    connection_string: str,
    stub: Type[ApiStub],
    api_token_header=API_TOKEN_HEADER,
) -> ApiStub:
    parsed = parse_grpc_connectionstring(connection_string=connection_string)

    if parsed.is_secure():
        assert parsed.server_crt is not None
        with open(parsed.server_crt, 'rb') as f:
            creds = grpc.ssl_channel_credentials(f.read())
        c = grpc.secure_channel(f"{parsed.host}:{parsed.port}", creds)
    else:
        c = grpc.insecure_channel(f"{parsed.host}:{parsed.port}")

    if parsed.api_token:
        assert parsed.api_token is not None
        channel = grpc.intercept_channel(c, _token_auth(api_token_header, parsed.api_token))
    return stub(channel)  # type: ignore
