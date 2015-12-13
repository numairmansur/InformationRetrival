TEST_CMD = python3 -m doctest
CHECKSTYLE_CMD = flake8

all: compile test checkstyle

compile:
	@echo "Nothing to compile for Python"

test:
	$(TEST_CMD) inverted_index.py

checkstyle:
	$(CHECKSTYLE_CMD) inverted_index.py

clean:
	rm -f inverted_index.pyc
	rm -rf __pycache__
	@echo "Cleaning done"
