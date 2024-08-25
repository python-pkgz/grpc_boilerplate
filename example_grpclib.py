from argparse import ArgumentParser
from ipaddress import IPv4Network, IPv6Network
from typing import List, Union

from management_commands import Command, main
from grpclib.server import Stream
import helloworld_grpc
import helloworld_pb2

from grpc_boilerplate.grpclib_tools.client import api_stub
from grpc_boilerplate.grpclib_tools.server import Server as GRPCServer


HOST = "127.0.0.1"
PORT = 50002


class GreeterService(helloworld_grpc.GreeterBase):
    async def SayHello(self, stream: Stream[helloworld_pb2.HelloRequest, helloworld_pb2.HelloReply]) -> None:
        request = await stream.recv_message()
        assert request is not None
        await stream.send_message(helloworld_pb2.HelloReply(message=f"Hello, {request.name}"))


class Server(Command):
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--host", default=HOST)
        parser.add_argument("--port", type=int, default=PORT)
        parser.add_argument("--token", default="")
        parser.add_argument("--peer", type=IPv4Network, nargs="+")

    async def handle(self, **kwargs):
        peer_whitelist: List[Union[IPv4Network, IPv6Network]] = []
        if kwargs["peer"]:
            peer_whitelist = kwargs["peer"]

        server = GRPCServer([GreeterService()], api_token=kwargs["token"], peer_whitelist=peer_whitelist)
        print(f'Serving on {kwargs["host"]}:{kwargs["port"]}')
        await server.serve(kwargs["host"], kwargs["port"])


class Client(Command):
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--connection_string", default=f"h2c://{HOST}:{PORT}")
        parser.add_argument("--message", default="World")

    async def handle(self, **kwargs):
        connection_string = kwargs["connection_string"]
        with api_stub(connection_string, stub=helloworld_grpc.GreeterStub) as client:
            resp = await client.SayHello(helloworld_pb2.HelloRequest(name=kwargs["message"]))
        print(resp)


if __name__ == "__main__":
    main(commands=[Server(), Client()])
