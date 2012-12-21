
SSH_KEY         = ""
PIP_REQUIREMENT = "requirements.txt"
BOTOCONF        = "./confs/boto.conf"
TEST_OPTIONS    = ""
#TEST_OPTIONS    = -p test_ownership.py
CSS_BIN         = public/stylesheets/main.css
LESS_DIR        = fe/less
LESS_SRC        = ${LESS_DIR}/hasbug.less ${LESS_DIR}//variables.less

all:
	echo "Not yet."

grun:
	source ./bin/activate && gunicorn --config==confs/gunicorn.conf.py web:app
run:
	source ./bin/activate && python web.py

test:
	source ./bin/activate && python -m unittest discover ${TEST_OPTIONS}
dbtest:
	source ./bin/activate && HASBUG_TEST_DATABASE=1 python -m unittest discover ${TEST_OPTIONS}
deploy:
	source ./bin/activate && fab -H hasb.ug -u ubuntu deploy

freeze: ${PIP_REQUIREMENT}

asset: ${CSS_BIN}

${CSS_BIN}: ${LESS_SRC}
	lessc --strict-import --include-path=${LESS_DIR}:components/bootstrap/less/ $< > $@

${PIP_REQUIREMENT}:
	source ./bin/activate && pip freeze > $@

clean:
	find hasbug -name "*.pyc" | xargs rm
	-rm rm *.pyc

.PHONY: ${PIP_REQUIREMENT} deploy run clean test
