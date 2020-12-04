from typing import Type, Optional, TypeVar
import collections
import urllib.parse

import grpc  # type: ignore

from grpc_boilerplate.constants import API_TOKEN_HEADER, TLS_CLIENT_CRT, TLS_CLIENT_KEY, TLS_TRUSTED_CERTS


ApiStub = TypeVar('ApiStub')


class _ClientCallDetails(
    collections.namedtuple('_ClientCallDetails', ('method', 'timeout', 'metadata', 'credentials')),
    grpc.ClientCallDetails
):
    pass


def _token_auth(header, token) -> grpc.UnaryUnaryClientInterceptor:
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


def api_stub(
    connection_string: str,
    stub: Type[ApiStub],

    tls_client_cert=TLS_CLIENT_CRT,
    tls_client_key=TLS_CLIENT_KEY,
    tls_trusted_certs=TLS_TRUSTED_CERTS,

    api_token_header=API_TOKEN_HEADER,
) -> ApiStub:
    parsed = urllib.parse.urlparse(connection_string, allow_fragments=False)
    host: str = parsed.hostname or 'localhost'
    port: int = parsed.port or 50000
    token: Optional[str] = parsed.username or None

    if parsed.scheme == 'h2c':
        c = grpc.insecure_channel(f"{host}:{port}")
    elif parsed.scheme == 'h2cs':
        c = grpc.secure_channel(f"{host}:{port}", grpc.ssl_channel_credentials(
            root_certificates=open(tls_trusted_certs, 'rb').read(),
            private_key=open(tls_client_key, 'rb').read(),
            certificate_chain=open(tls_client_cert, 'rb').read()
        ))
    else:
        raise ValueError(
            f"Unknown scheme: '{parsed.scheme}' for '{connection_string}'"
        )

    channel = grpc.intercept_channel(c, _token_auth(api_token_header, token))
    return stub(channel)  # type: ignore
