import threading

class CountForThreads:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.count = 0

    def inc(self, by = 1):
        self.lock.acquire()
        self.count += by
        self.lock.release()

    def getCount(self):
        self.lock.acquire()
        count = self.count
        self.lock.release()
        return count
    
    def reset(self):
        self.lock.acquire()
        self.count = 0
        self.lock.release()