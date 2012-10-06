
SSH_KEY         = ""
PIP_REQUIREMENT = "requirements.txt"

all:
	echo "Not yet."

run:
	python web.py

test:
	source ./pyenv/bin/activate && python -m unittest discover

deploy:
	fab -H hasb.ug -u ubuntu -i ${SSH_KEY} deploy

freeze: ${PIP_REQUIREMENT}

${PIP_REQUIREMENT}:
	pip freeze > $@

clean:
	find hasbug -name "*.pyc" | xargs rm
	-rm rm *.pyc

.PHONY: ${PIP_REQUIREMENT} deploy run clean test
