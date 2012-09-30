import multiprocessing

bind = "0.0.0.0:80"
worker = multiprocessing.cpu_count() * 2 + 1
