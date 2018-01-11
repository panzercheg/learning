import time


class timer():
    def __init__(self):
        self.start = time.time()

    def current_time(self):
        return time.time() - self.start

    def __enter__(self):
        return self

    def __exit__(self, *args):
        print("Elapsed time: {}".format(time.time() - self.start))


with timer() as t:
    time.sleep(1)
    print('Current time: {}'.format(t.current_time()))
    time.sleep(1)


timer()