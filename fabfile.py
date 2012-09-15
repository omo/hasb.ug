
from fabric.api import local, run, cd
import os

# http://stackoverflow.com/questions/1180411/activate-a-virtualenv-via-fabric-as-deploy-user
# FIXME: These should be env. variables.
PROJECT_DIR   = "~/work/hasb.ug"
VENV_ACTIVATE = os.path.join(PROJECT_DIR, "pyenv/bin/activate")

def virtualenv(command):
    run("source " + VENV_ACTIVATE + ' && ' + command)

# Invokable commands:

def hello():
    print "Hello!"

def update():
    with cd(PROJECT_DIR):
        run("git pull")
        run("virtualenv pyenv --distribute")
        virtualenv("pip install -r requirements.txt")

def deploy():
    update()
