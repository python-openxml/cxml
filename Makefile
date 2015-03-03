MAKE   = make
PYTHON = python
SETUP  = $(PYTHON) ./setup.py

.PHONY: clean

help:
	@echo "Please use \`make <target>' where <target> is one or more of"
	@echo "  clean     delete intermediate work product and start fresh"

clean:
	find . -type f -name \*.pyc -exec rm {} \;
	rm -rf dist *.egg-info .coverage .DS_Store

coverage:
	py.test --cov-report term-missing --cov=cxml tests/

sdist:
	$(SETUP) sdist

test: clean
	flake8
	py.test -x
