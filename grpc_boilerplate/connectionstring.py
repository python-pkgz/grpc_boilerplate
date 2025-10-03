from typing import Optional
import urllib.parse


class ParsedGrpcConnectionString:
    """
    GRPC Connectionstring represenration
    """

    target: str = ""  # Server target

    api_token: Optional[str] = None  # Server api token

    server_crt: Optional[str] = None  # Server certificate if connection is secure

    def is_secure(self) -> bool:
        """
        Connection is secure
        """
        return bool(self.server_crt)


def parse_grpc_connectionstring(connection_string: str) -> ParsedGrpcConnectionString:
    """
    Parse grpc connectionstring `h2c|h2://[<token>@]host[:port][?ServerCrt=<path to server cert>]`
    Attempt to create generic connectionstring format for grpc connections
    """

    result = ParsedGrpcConnectionString()

    parsed = urllib.parse.urlparse(connection_string, allow_fragments=False)
    result.api_token = parsed.username or None

    result.target = str(parsed.netloc)
    if "@" in result.target:
        result.target = result.target.split("@", maxsplit=1)[1]

    if not result.target:
        raise ValueError("host must be specified")

    qs = urllib.parse.parse_qs(parsed.query)
    server_crt_values = qs.get("ServerCrt", [])
    if len(server_crt_values) == 0:
        server_crt = None
    elif len(server_crt_values) == 1:
        server_crt = server_crt_values[0]
    else:
        raise ValueError("Multiple ServerCrt is not allowed")

    if parsed.scheme == "h2c":
        if server_crt:
            raise ValueError("Insecure connection must not contain ServerCrt")
        result.server_crt = None
    elif parsed.scheme == "h2":
        if not server_crt:
            raise ValueError("Secure connection must contain ServerCrt")
        result.server_crt = server_crt
    else:
        raise ValueError(f"Unknown scheme: '{parsed.scheme}' for '{connection_string}'")

    return result
