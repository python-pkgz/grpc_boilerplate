OPENSSL=openssl

.PHONY: clean
clean:
	rm -rf .mypy_cache .pytest_cache dist grpc_boilerplate.egg-info .coverage certs helloworld_pb2_grpc.py helloworld_pb2.py helloworld_grpc.py

.PHONY: examples
examples: certs
	poetry run python -m grpc_tools.protoc -I. --python_out=. ./helloworld.proto          # Protobuf messages (helloworld_pb2.py)
	poetry run python -m grpc_tools.protoc -I. --grpc_python_out=. ./helloworld.proto     # Grpcio (helloworld_pb2_grpc.py)
	poetry run python -m grpc_tools.protoc -I. --grpclib_python_out=. ./helloworld.proto  # Grpclib (helloworld_grpc.py)


certs:
	mkdir -p certs
	$(OPENSSL) genrsa -out certs/server.key 4096  # server.key: a private RSA key to sign and authenticate the public key
	$(OPENSSL) req -new -x509 -sha256 -key certs/server.key -subj '/CN=server' -out certs/server.crt -days 3650 -addext 'subjectAltName = IP:127.0.0.1'  # server.pem/server.crt: self-signed X.509 public keys for distribution


.PHONY: qa
qa:
	poetry run flake8 grpc_boilerplate
	poetry run mypy --warn-unused-ignores grpc_boilerplate


.PHONY: test
test:
	poetry run pytest --cov=grpc_boilerplate tests/


.PHONY: dist
dist:
	poetry publish
	git tag `poetry version -s`
	git push --tags
