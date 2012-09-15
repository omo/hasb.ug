
SSH_KEY         = ""
PIP_REQUIREMENT = "requirements.txt"

all:
	echo "Not yet."

deploy:
	fab -H hasb.ug -u ubuntu -i ${SSH_KEY} deploy

freeze: ${PIP_REQUIREMENT}

${PIP_REQUIREMENT}:
	pip freeze > $@

.PHONY: ${PIP_REQUIREMENT} deploy
