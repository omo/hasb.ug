
PIP_REQUIREMENT = "requirement.txt"

all:
	echo "Not yet."

freeze: ${PIP_REQUIREMENT}

${PIP_REQUIREMENT}:
	pip freeze > $@

.PHONY: ${PIP_REQUIREMENT}
