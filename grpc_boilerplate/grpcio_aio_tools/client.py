import typing
import grpc  # type: ignore

from grpc_boilerplate.constants import API_TOKEN_HEADER
from grpc_boilerplate.connectionstring import parse_grpc_connectionstring


ApiStub = typing.TypeVar("ApiStub")


def _token_auth(header: str, token: str) -> grpc.aio.UnaryUnaryClientInterceptor:
    class AuthInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
        async def intercept_unary_unary(self, continuation, client_call_details, request):
            metadata = []
            if client_call_details.metadata is not None:
                metadata = list(client_call_details.metadata)

            metadata.append((header, token))

            return await continuation(
                grpc.aio.ClientCallDetails(
                    client_call_details.method,
                    client_call_details.timeout,
                    metadata,
                    client_call_details.credentials,
                    client_call_details.wait_for_ready,
                ),
                request,
            )

    return AuthInterceptor()


class api_stub(typing.Generic[ApiStub]):
    """
    Create grpc.aio client from connection_string
    see grpc_boilerplate.connectionstring.parse_grpc_connectionstring for connectionstring format

    Usage:
    async with api_stub("h2c://127.0.0.1:50001", helloworld_pb2_grpc.GreeterStub) as greeter:
       resp = client.SayHello(helloworld_pb2.HelloRequest(name=kwargs['message']))
       print(resp)
    """

    def __init__(
        self,
        connection_string: str,
        stub: typing.Type[ApiStub],
        api_token_header: str = API_TOKEN_HEADER,
        interceptors: typing.Sequence[grpc.aio.ClientInterceptor] = (),
        channel_options: typing.Optional[typing.Sequence[typing.Tuple[str, typing.Any]]] = None,
    ) -> None:
        parsed = parse_grpc_connectionstring(connection_string=connection_string)
        interceptors = list(interceptors)

        if parsed.api_token:
            assert parsed.api_token is not None
            interceptors.append(_token_auth(api_token_header, parsed.api_token))

        if parsed.is_secure():
            assert parsed.server_crt is not None
            with open(parsed.server_crt, "rb") as f:
                creds = grpc.ssl_channel_credentials(f.read())

            channel = grpc.aio.secure_channel(
                f"{parsed.host}:{parsed.port}",
                credentials=creds,
                interceptors=interceptors,
                options=channel_options,
            )
        else:
            channel = grpc.aio.insecure_channel(
                f"{parsed.host}:{parsed.port}",
                interceptors=interceptors,
                options=channel_options,
            )

        self.stub: ApiStub = stub(channel)  # type: ignore
        self.channel: grpc.aio.Channel = channel

    async def __aenter__(self) -> ApiStub:
        return self.stub

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.channel.close()
