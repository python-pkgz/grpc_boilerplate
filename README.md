# Grpc boilerplate
Code for help server and client usage

* grpcio `grpc_boilerplate.grpcio_tools`
  - Client unsecure connections
  - Client secure connections
  - Client token auth
  - Server insecure
  - Server secure
* grpcio.aio `grpc_boilerplate.grpcio_aio_tools`
  - Client unsecure connections
  - Client secure connections
  - Client token auth
  - Server insecure
  - Server secure
* grpclib `grpc_boilerplate.grpclib_tools`
  - Client unsecure connections
  - Client token auth
  - Server insecure
  - Server token auth
  - Server peer whitelist

## Examples
Examples proto: [helloworld.proto](helloworld.proto).

Each example implements `server` and `client` subcommands.

Run `make examples` to generate grpc and protobuf code for examples.

 * grpc [example_grpcio.py](example_grpcio.py)
 * grpc.aio [example_grpcio_aio.py](example_grpcio_aio.py)
 * grpclib [example_grpclib.py](example_grpclib.py)

## Test
```shell
$ make qa test
```
