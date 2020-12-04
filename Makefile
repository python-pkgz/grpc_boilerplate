.PHONY: clean
clean:
	rm -rf .mypy_cache .pytest_cache dist grpc_boilerplate.egg-info .coverage

.PHONY: qa
qa:
	pipenv run flake8 grpc_boilerplate
	pipenv run mypy --warn-unused-ignores grpc_boilerplate


.PHONY: test
test:
	pipenv run pytest --cov=grpc_boilerplate tests/


.PHONY: dist
dist:
	python3 setup.py sdist
	twine upload dist/*
	git tag `cat setup.py | grep VERSION | grep -v version | cut -d= -f2 | tr -d "[:space:]"`
	git push --tags