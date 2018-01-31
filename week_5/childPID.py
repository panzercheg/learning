import time
import os

pid = os.fork()
if pid == 0:
    # Дочерний процесс
    while True:
        print("child:", os.getpid())
        time.sleep(5)

    else:
    # родительский процесс
        print("parent: ", os.getpid())
        os.wait()