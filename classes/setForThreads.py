import threading

class SetForThreads:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.actualSet = set()

    def isValExists(self, valToCheck):
        self.lock.acquire()
        exists = valToCheck in self.actualSet
        self.lock.release()
        return exists

    def add(self,item):
        self.lock.acquire()
        self.actualSet.add(item)
        self.lock.release()
        