install:
	poetry install

build:
	poetry build

clean:
	rm -rf dist

local-install:
	pip install ./dist/obiba_mica-*.tar.gz 
