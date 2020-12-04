from typing import Optional, List

import ssl


# Generate keys:
# openssl req -x509 -newkey rsa:2048 -nodes -subj '/CN=localhost' -keyout trusted.key -out trusted.crt
# openssl req -x509 -newkey rsa:2048 -nodes -subj '/CN=example.com' -keyout client.key -out client.crt


def create_secure_context(
    client_cert: str,
    client_key: str,
    trusted_certs: List[str],
) -> Optional[ssl.SSLContext]:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.load_cert_chain(str(client_cert), str(client_key))

    for trusted in trusted_certs:
        ctx.load_verify_locations(trusted)

    ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    ctx.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20')
    ctx.set_alpn_protocols(['h2'])
    try:
        ctx.set_npn_protocols(['h2'])
    except NotImplementedError:
        pass
    return ctx
