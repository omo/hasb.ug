
from fabric.api import local, run, cd, settings, sudo
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

# This should be a part of initial per-user setup
#def setup_pyenv():
#    with cd(PROJECT_DIR):
#        run("virtualenv pyenv --distribute")

def update():
    with cd(PROJECT_DIR):
        run("git pull origin master")
        virtualenv("pip install -r requirements.txt")

def reload_gunicorn():
    with cd(PROJECT_DIR):
        with settings(warn_only=True):
            sudo("stop gunicorn")
        sudo("cp confs/gunicorn-upstart.conf /etc/init/gunicorn.conf")
        sudo("start --verbose gunicorn")

def deploy():
    update()
    reload_gunicorn()
