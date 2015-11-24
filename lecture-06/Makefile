TEST_CMD = python3 -m doctest
CHECKSTYLE_CMD = flake8
PORT = 9999
RECORDS_FILE = movie-titles-extended.txt

all: compile test checkstyle

compile:
	@echo "Nothing to compile for Python"

test:
	$(TEST_CMD) *.py

checkstyle:
	$(CHECKSTYLE_CMD) *.py

clean:
	rm -f *.pyc
	rm -rf __pycache__

start:
	python3 server.py $(RECORDS_FILE) $(PORT)
