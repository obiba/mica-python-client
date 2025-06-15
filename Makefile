install:
	poetry install

test:
	poetry run pytest

build:
	poetry build

clean:
	rm -rf dist
