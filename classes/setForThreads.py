import threading

class SetForThreads:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.actualSet = set()

    def __len__(self):
        self.lock.acquire()
        length = len(self.actualSet)
        self.lock.release()
        return length
    
    def __iter__(self):
        return self

    def isValExists(self, valToCheck):
        self.lock.acquire()
        exists = valToCheck in self.actualSet
        self.lock.release()
        return exists

    def add(self,item):
        self.lock.acquire()
        self.actualSet.add(item)
        self.lock.release()
        