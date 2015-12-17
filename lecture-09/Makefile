TEST_CMD = python3 -m doctest
CHECKSTYLE_CMD = flake8

all: compile test checkstyle

compile:
	@echo "Nothing to compile for Python"

test:
	$(TEST_CMD) kmeans.py

checkstyle:
	$(CHECKSTYLE_CMD) kmeans.py

clean:
	rm -f kmeans.pyc
	rm -rf __pycache__
	@echo "Cleaning done"
