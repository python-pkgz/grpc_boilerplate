import typing
import collections

import grpc  # type: ignore

from grpc_boilerplate.constants import API_TOKEN_HEADER
from grpc_boilerplate.connectionstring import parse_grpc_connectionstring


ApiStub = typing.TypeVar("ApiStub")


class _ClientCallDetails(
    collections.namedtuple(
        "_ClientCallDetails",
        (
            "method",
            "timeout",
            "metadata",
            "credentials",
            "wait_for_ready",
            "compression",
        ),
    ),
    grpc.ClientCallDetails,
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
                client_call_details.method,
                client_call_details.timeout,
                metadata,
                client_call_details.credentials,
                client_call_details.wait_for_ready,
                client_call_details.compression,
            )
            return continuation(client_call_details, request)

    return AuthInterceptor()


class api_stub(typing.Generic[ApiStub]):
    """
    Create grpc client from connection_string
    see grpc_boilerplate.connectionstring.parse_grpc_connectionstring for connectionstring format

    Usage:
    with api_stub("h2c://127.0.0.1:50001", GreeterStub) as greeter:
       resp = client.SayHello(HelloRequest(name=kwargs['message']))
       print(resp)
    """

    def __init__(
        self,
        connection_string: str,
        stub: typing.Type[ApiStub],
        api_token_header: str = API_TOKEN_HEADER,
        channel_options: typing.Optional[typing.Sequence[typing.Tuple[str, typing.Any]]] = None,
    ) -> None:
        parsed = parse_grpc_connectionstring(connection_string=connection_string)

        if parsed.is_secure():
            assert parsed.server_crt is not None
            with open(parsed.server_crt, "rb") as f:
                creds = grpc.ssl_channel_credentials(f.read())
            channel = grpc.secure_channel(f"{parsed.host}:{parsed.port}", creds, options=channel_options)
        else:
            channel = grpc.insecure_channel(f"{parsed.host}:{parsed.port}", options=channel_options)

        if parsed.api_token:
            assert parsed.api_token is not None
            channel = grpc.intercept_channel(channel, _token_auth(api_token_header, parsed.api_token))

        self.stub: ApiStub = stub(channel)  # type: ignore
        self.channel: grpc.Channel = channel

    def __enter__(self) -> ApiStub:
        return self.stub

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.channel.close()
