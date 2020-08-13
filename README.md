# RedisImplementsMutex

This project shows a basic example of mutual exclusion's usage among two threads using Redis to synchronize them. Basically, each thread has a mutual exclusion logic which depends
to other one release the resource to execute. The change of status between them is made using Redis pub/sub concept, so each thread has his own chaneel to publish your current
status (take ou give, for example) and subscribe in a channel that stores the other task status.

For example, thread1 subscribe in thread 2 channel:

```
    def subscriber(self):
        pubsub = self._redis.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe("semaphore_thread2_released")
        for notification in pubsub.listen():
            if notification["channel"] == "semaphore_thread2_released":
                self.thread2_released = notification["data"]
```

and in your main method, wait until the thread2 give the semaphore to it, to execute, and notify yout status to thread2

```
    def run(self):
        while(True):
            if self._thread2_released is True:
                self.publisher("semaphore_thread1_released", False)
                print("Executing thread 1!") 
                print(datetime.now())
                self.publisher("semaphore_thread1_released", True)
                gevent.sleep(5)
            else:
                self.publisher("semaphore_thread1_released", True)
            gevent.sleep(1) #Dorme a thread por 1 segundo
```

To run this application:
``` 
git clone git@github.com:gitandlucsil/RedisImplementsMutex.git
pip3 install gevent
pip3 install redis
cd /RedisImplementsMutex && python3 semaforo.py
cd /RedisImplementsMutex && python3 semaforo2.py
```

To monitore the semaphore status to each thread, redis-cli can be used
```
redis-cli
subscribe semaphore_thread1_released
subscribe semaphore_thread2_released
```
