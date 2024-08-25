from typing import Type, TypeVar, Generic

from grpclib.client import Channel
from grpclib.events import SendRequest, listen

from grpc_boilerplate.constants import API_TOKEN_HEADER
from grpc_boilerplate.connectionstring import parse_grpc_connectionstring

ApiStub = TypeVar("ApiStub")


class api_stub(Generic[ApiStub]):
    """
    Create grpclib client from connection_string
    see grpc_boilerplate.connectionstring.parse_grpc_connectionstring for connectionstring format

    Usage:
    with api_stub("h2c://127.0.0.1:50001", GreeterStub) as greeter:
       resp = await client.SayHello(HelloRequest(name=kwargs['message']))
       print(resp)
    """

    def __init__(
        self,
        connection_string: str,
        stub: Type[ApiStub],
        api_token_header: str = API_TOKEN_HEADER,
    ) -> None:
        parsed = parse_grpc_connectionstring(connection_string=connection_string)

        if parsed.is_secure():
            raise ValueError("secure channels is not supported")

        channel = Channel(parsed.host, parsed.port)

        if parsed.api_token:

            async def on_send_request(event: SendRequest) -> None:
                assert parsed.api_token is not None
                event.metadata[api_token_header] = parsed.api_token

            listen(channel, SendRequest, on_send_request)

        self.stub: ApiStub = stub(channel)  # type: ignore
        self.channel: Channel = channel

    def __enter__(self) -> ApiStub:
        return self.stub

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.channel.close()
