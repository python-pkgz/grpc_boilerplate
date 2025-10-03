OPENSSL=openssl

.PHONY: clean
clean:
	rm -rf .mypy_cache .pytest_cache dist grpc_boilerplate.egg-info .coverage certs ./tests/proto/helloworld_pb2_grpc.py ./tests/proto/helloworld_pb2.py ./tests/proto/helloworld_grpc.py ./tests/proto/helloworld_pb2.pyi

.PHONY: protoc
protoc: certs
	poetry run python -m grpc_tools.protoc -I. --mypy_out=. --python_out=. ./tests/proto/helloworld.proto          # Protobuf messages (helloworld_pb2.py)
	poetry run python -m grpc_tools.protoc -I. --mypy_out=. --grpc_python_out=. ./tests/proto/helloworld.proto     # Grpcio (helloworld_pb2_grpc.py)

certs:
	mkdir -p certs
	$(OPENSSL) genrsa -out certs/server.key 4096  # server.key: a private RSA key to sign and authenticate the public key
	$(OPENSSL) req -new -x509 -sha256 -key certs/server.key -subj '/CN=server' -out certs/server.crt -days 3650 -addext 'subjectAltName = IP:127.0.0.1'  # server.pem/server.crt: self-signed X.509 public keys for distribution


.PHONY: qa
qa: protoc
	poetry run ruff check .
	poetry run ruff format --check
	poetry run mypy --warn-unused-ignores .


.PHONY: test
test: protoc
	poetry run pytest --cov=grpc_boilerplate tests/


.PHONY: dist
dist:
	poetry publish --build
	git tag `poetry version -s`
	git push --tags
