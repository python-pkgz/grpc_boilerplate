from grpc_boilerplate.connectionstring import parse_grpc_connectionstring


def test_parse_grpc_connectionstring():
    parse_grpc_connectionstring("h2c://localhost:50002")
