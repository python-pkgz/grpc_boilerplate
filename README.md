# Grpc boilerplate
Code for help server and client usage

* grpcio `grpc_boilerplate.grpcio_tools`
  - Client unsecure connections
  - Client secure connections
  - Client token auth
* grpcio.aio `grpc_boilerplate.grpcio_aio_tools`
  - Client unsecure connections
  - Client secure connections
  - Client token auth

## Examples
Examples proto: [helloworld.proto](helloworld.proto).

Each example implements `server` and `client` subcommands.

Run `make examples` to generate grpc and protobuf code for examples.

 * grpc [example_grpcio.py](example_grpcio.py)
 * grpc.aio [example_grpcio_aio.py](example_grpcio_aio.py)

## Test
```shell
$ make qa test
```
