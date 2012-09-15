
PIP_REQUIREMENT = "requirements.txt"

all:
	echo "Not yet."

setup:
	virtualenv pyenv --distribute
	pip install -r requirements.txt

freeze: ${PIP_REQUIREMENT}

${PIP_REQUIREMENT}:
	pip freeze > $@

.PHONY: ${PIP_REQUIREMENT} setup
