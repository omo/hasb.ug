import multiprocessing
import os

prod_dir = "/home/ubuntu/work/hasbug/"
worker = multiprocessing.cpu_count() * 2 + 1

if os.environ.get("HASBUG_PROD"):
    user = "ubuntu"
    group = "ubuntu"
    bind = "0.0.0.0:80"
    accesslog  = os.path.join(prod_dir, "log/access.log")
    errorlog   = os.path.join(prod_dir, "log/error.log")
    pidfile    = os.path.join(prod_dir, "run/gunicorn.pid")
    #debug = True
else:
    bind = "0.0.0.0:8000"
    debug = True
