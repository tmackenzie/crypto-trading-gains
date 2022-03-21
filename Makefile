.PHONY: test

activate:
	source env/bin/activate

install:
	python -m pip install -r requirements.txt

test:
	python -m unittest
