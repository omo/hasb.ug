
from fabric.api import local, run, cd, settings, sudo, env, put
import os

# http://stackoverflow.com/questions/1180411/activate-a-virtualenv-via-fabric-as-deploy-user
# FIXME: These should be env. variables.
PROJECT_DIR   = "/home/ubuntu/work/hasb.ug"
NVM_DIR       = "/home/ubuntu/.nvm"
VENV_ACTIVATE = os.path.join(PROJECT_DIR, "bin/activate")

env.use_ssh_config = True

def virtualenv(command):
    run(". " + VENV_ACTIVATE + ' && ' + command)

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
        run("export NVM_DIR={dir}".format(dir=NVM_DIR))
        virtualenv("pip install -r requirements.txt")
        virtualenv("npm install")
        virtualenv("bower install")
        put("confs/boto.conf", "confs/boto.conf")
        run("make clean all")

def reload_gunicorn():
    with cd(PROJECT_DIR):
        with settings(warn_only=True):
            sudo("stop gunicorn-hasbug")
            sudo("/etc/init.d/nginx stop")
        sudo("cp confs/gunicorn-upstart.conf /etc/init/gunicorn-hasbug.conf")
        sudo("cp confs/nginx.conf /etc/nginx/sites-enabled/hasbug.conf")
        sudo("cp confs/logrotate.conf /etc/logrotate.d/gunicorn-hasbug")
        sudo("start --verbose gunicorn-hasbug")
        sudo("/etc/init.d/nginx start")

def deploy():
    update()
    reload_gunicorn()
