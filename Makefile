PYTHON = python3

clean:
	black .
	${PYTHON} -m flake8
	isort --profile black .

