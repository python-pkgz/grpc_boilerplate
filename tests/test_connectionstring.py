import pytest
from grpc_boilerplate.connectionstring import parse_grpc_connectionstring


def test_parse_grpc_connectionstring():
    parsed = parse_grpc_connectionstring("h2c://localhost")
    assert parsed.api_token is None
    assert parsed.is_secure() is False
    assert parsed.target == "localhost"
    assert parsed.server_crt is None

    parsed = parse_grpc_connectionstring("h2c://localhost:50002")
    assert parsed.api_token is None
    assert parsed.is_secure() is False
    assert parsed.target == "localhost:50002"
    assert parsed.server_crt is None

    parsed = parse_grpc_connectionstring("h2c://localhost:50002,localhost:50003")
    assert parsed.api_token is None
    assert parsed.is_secure() is False
    assert parsed.target == "localhost:50002,localhost:50003"
    assert parsed.server_crt is None

    parsed = parse_grpc_connectionstring("h2://secret@1.2.3.4:50003?ServerCrt=123.crt")
    assert parsed.api_token == "secret"
    assert parsed.is_secure() is True
    assert parsed.target == "1.2.3.4:50003"
    assert parsed.server_crt == "123.crt"

    with pytest.raises(ValueError):
        parse_grpc_connectionstring("h2c://secret@1.2.3.4:50003?ServerCrt=123.crt")

    with pytest.raises(ValueError):
        parse_grpc_connectionstring("h2://1.2.3.4:50003")

    with pytest.raises(ValueError):
        parse_grpc_connectionstring("h2://1.2.3.4:50003?ServerCrt")

    with pytest.raises(ValueError):
        parse_grpc_connectionstring("h2://1.2.3.4?ServerCrt")
