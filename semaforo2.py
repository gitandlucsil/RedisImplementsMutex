import gevent
from gevent import monkey
import redis
from datetime import datetime

monkey.patch_socket()
# All greenlets running on system
greenlets = []


class Thread2(object):

    REDIS_CONFIG = {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'decode_responses': True,
    }

    def __init__(self):
        self._redis = redis.StrictRedis(**Thread2.REDIS_CONFIG)
        self._thread1_released = False

    @property
    def thread1_released(self):
        return self._thread1_released

    @thread1_released.setter
    def thread1_released(self, status):
        if isinstance(status, str):
            _status = status.lower()
            if _status == "true":
                self._thread1_released = True
            elif _status == "false":
                self._thread1_released = False

    def run(self):
        while(True):
            if self._thread1_released is True:
                self.publisher("semaphore_thread2_released", False)
                print("Executando thread 2!")
                print(datetime.now())
                self.publisher("semaphore_thread2_released", True)
                gevent.sleep(5)
            else:
                self.publisher("semaphore_thread2_released", True)
            gevent.sleep(1)  # Dorme a thread por 1 segundo

    def subscriber(self):
        pubsub = self._redis.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe("semaphore_thread1_released")
        for notification in pubsub.listen():
            if notification["channel"] == "semaphore_thread1_released":
                self.thread1_released = notification["data"]

    def publisher(self, channel, value):
        self._redis.set(str(channel), str(value))
        self._redis.publish(str(channel), str(value))


def stop_greenlets():
    """
    Metodo para matar todos os processos do modulo
    """
    gevent.killall(greenlets)


def dealing_exception(greenlet):
    """
    Metodo para lidar com os processos do modulo
    """
    stop_greenlets()


def main():

    thread2 = Thread2()

    greenlets.append(gevent.spawn(thread2.run))
    greenlets.append(gevent.spawn(thread2.subscriber))

    for greenlet in greenlets:
        greenlet.link_exception(dealing_exception)
    gevent.joinall(greenlets)


if __name__ == '__main__':
    main()
