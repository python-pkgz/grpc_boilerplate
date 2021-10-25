from argparse import ArgumentParser
from management_commands import Command, main

from grpc_boilerplate.pygrpc_tools.client import api_stub
from grpc

class Server(Command):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('--host', default="127.0.0.1")
        parser.add_argument('--port', type=int, default=50002)
        parser.add_argument('--token', default='')
        parser.add_argument('--tls', action='store_true')
        parser.add_argument('-tls-crt', default="certs/server.crt")
        parser.add_argument('-tls-key', default="certs/server.key")

    def handle(self, **kwargs):
        pass


class Client(Command):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument("connection_string", default="h2c://127.0.0.1:50002")

    def handle(self, **kwargs):
        connection_string = kwargs['connection_string']
        client = api_stub(connection_string, stub=)


if __name__ == "__main__":
    main(commands=[Server(), Client()])
