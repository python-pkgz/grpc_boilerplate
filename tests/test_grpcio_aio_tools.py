import grpc  # type: ignore
from tests.proto import helloworld_pb2_grpc
from contextlib import asynccontextmanager
from tests.proto import helloworld_pb2
from grpc_boilerplate.grpcio_aio_tools.client import api_stub
import pytest


class GreeterService(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request: helloworld_pb2.HelloRequest, context: grpc.RpcContext) -> helloworld_pb2.HelloReply:
        return helloworld_pb2.HelloReply(message=f"Hello, {request.name}")


class TestGrpcioTools:
    @asynccontextmanager
    async def server(self, hostport: str, tls: bool, tls_crt_path: str = "", tls_key_path: str = "") -> grpc.Server:
        server = grpc.aio.server()
        helloworld_pb2_grpc.add_GreeterServicer_to_server(GreeterService(), server)
        if tls is True:
            with open(tls_crt_path, "rb") as f:
                tls_crt = f.read()
            with open(tls_key_path, "rb") as f:
                tls_key = f.read()
            creds = grpc.ssl_server_credentials([(tls_key, tls_crt)])
            server.add_secure_port(hostport, creds)
        else:
            server.add_insecure_port(hostport)

        await server.start()
        yield server
        await server.stop(None)

    @pytest.mark.asyncio
    async def test_grpcio_tools(self):
        async with self.server("127.0.0.1:50002", False):
            async with api_stub("h2c://127.0.0.1:50002", helloworld_pb2_grpc.GreeterStub) as client:
                resp = await client.SayHello(helloworld_pb2.HelloRequest(name="World"))
                assert resp.message == "Hello, World"

                resp = await client.SayHello(helloworld_pb2.HelloRequest(name="Morld"))
                assert resp.message == "Hello, Morld"
