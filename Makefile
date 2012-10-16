
SSH_KEY         = ""
PIP_REQUIREMENT = "requirements.txt"
BOTOCONF        = "./confs/boto.conf"

all:
	echo "Not yet."

grun:
	source ./bin/activate && gunicorn --config==confs/gunicorn.conf.py web:app
run:
	source ./bin/activate && python web.py

test:
	source ./bin/activate && python -m unittest discover
dbtest:
	source ./bin/activate && HASBUG_TEST_DATABASE=1 python -m unittest discover
deploy:
	source ./bin/activate && fab -H hasb.ug -u ubuntu deploy

freeze: ${PIP_REQUIREMENT}

${PIP_REQUIREMENT}:
	pip freeze > $@

clean:
	find hasbug -name "*.pyc" | xargs rm
	-rm rm *.pyc

.PHONY: ${PIP_REQUIREMENT} deploy run clean test
