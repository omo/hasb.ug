
SSH_KEY         = ""
PIP_REQUIREMENT = "requirements.txt"
BOTOCONF        = "./confs/boto.conf"
TEST_OPTIONS    = ""
#TEST_OPTIONS    = -p test_ownership.py
CSS_BIN         = public/stylesheets/main.css
LESS_DIR        = fe/less
LESS_SRC        = ${LESS_DIR}/hasbug.less ${LESS_DIR}//variables.less
JS_VENDOR_DIR   = public/javascript/vendor
JS_VENDOR_BS    = ${JS_VENDOR_DIR}/bootstrap.js
FONT_SRC_DIR    = third_party/FortAwesome-Font-Awesome/font
FONT_SRC        = ${FONT_SRC_DIR}/fontawesome-webfont.eot \
                  ${FONT_SRC_DIR}/fontawesome-webfont.svg \
                  ${FONT_SRC_DIR}/fontawesome-webfont.ttf \
                  ${FONT_SRC_DIR}/fontawesome-webfont.woff
FONT_DST_DIR    = public/font
FONT_DST        = $(subst ${FONT_SRC_DIR},${FONT_DST_DIR},${FONT_SRC})

all: asset
	echo "Done."

grun:
	. ./bin/activate && gunicorn --config==confs/gunicorn.conf.py web:app
run:
	. ./bin/activate && python web.py

test:
	. ./bin/activate && python -m unittest discover ${TEST_OPTIONS}
dbtest:
	. ./bin/activate && HASBUG_TEST_DATABASE=1 python -m unittest discover ${TEST_OPTIONS}
deploy:
	. ./bin/activate && fab -H hasb.ug -u ubuntu deploy

freeze: ${PIP_REQUIREMENT}


asset: ${CSS_BIN} ${JS_VENDOR_BS} ${FONT_DST}

${FONT_DST}: ${FONT_SRC}
	mkdir -p ${FONT_DST_DIR}
	cp $? ${FONT_DST_DIR}

${JS_VENDOR_BS}:
	mkdir -p ${JS_VENDOR_DIR}
	cp components/bootstrap/docs/assets/js/bootstrap.js $@

${CSS_BIN}: ${LESS_SRC}
	. ./bin/activate && lessc --strict-import --include-path=${LESS_DIR}:components/bootstrap/less/ $< > $@

${PIP_REQUIREMENT}:
	. ./bin/activate && pip freeze > $@

clean:
	find hasbug -name "*.pyc" | xargs rm
	-rm rm *.pyc

.PHONY: ${PIP_REQUIREMENT} deploy run clean test
