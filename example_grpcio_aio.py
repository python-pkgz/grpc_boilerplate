from argparse import ArgumentParser
from management_commands import Command, main

import helloworld_pb2_grpc
import helloworld_pb2
from grpc_boilerplate.grpcio_aio_tools.client import api_stub
import grpc  # type: ignore


HOST = "127.0.0.1"
PORT = 50002
TLS_CRT = "certs/server.crt"
TLS_KEY = "certs/server.key"


class GreeterService(helloworld_pb2_grpc.GreeterServicer):
    async def SayHello(self, request: helloworld_pb2.HelloRequest, context: grpc.RpcContext) -> helloworld_pb2.HelloReply:
        return helloworld_pb2.HelloReply(message=f"Hello, {request.name}")


class Server(Command):
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--host", default=HOST)
        parser.add_argument("--port", type=int, default=PORT)
        parser.add_argument("--tls", action="store_true")
        parser.add_argument("-tls_crt", default=TLS_CRT)
        parser.add_argument("-tls_key", default=TLS_KEY)

    async def handle(self, **kwargs):
        server = grpc.aio.server()
        helloworld_pb2_grpc.add_GreeterServicer_to_server(GreeterService(), server)
        if kwargs["tls"] is True:
            with open(kwargs["tls_crt"], "rb") as f:
                tls_crt = f.read()
            with open(kwargs["tls_key"], "rb") as f:
                tls_key = f.read()
            creds = grpc.ssl_server_credentials(
                [
                    (tls_key, tls_crt),
                ]
            )
            server.add_secure_port(f'{kwargs["host"]}:{kwargs["port"]}', creds)
        else:
            server.add_insecure_port(f'{kwargs["host"]}:{kwargs["port"]}')

        await server.start()
        print(f'Serving on {kwargs["host"]}:{kwargs["port"]}')
        await server.wait_for_termination()


class Client(Command):
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--connection_string", default=f"h2c://{HOST}:{PORT}")
        parser.add_argument("--message", default="World")

    async def handle(self, **kwargs):
        connection_string = kwargs["connection_string"]
        async with api_stub(connection_string, stub=helloworld_pb2_grpc.GreeterStub) as client:
            resp = await client.SayHello(helloworld_pb2.HelloRequest(name=kwargs["message"]))
        print(resp)


if __name__ == "__main__":
    main(commands=[Server(), Client()])
