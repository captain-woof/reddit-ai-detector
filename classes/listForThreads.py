import threading

class ListForThreads:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.actualList = []
        self.enumIndex = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            self.lock.acquire()
            next = self.actualList[self.enumIndex]
            self.enumIndex += 1
            self.lock.release()
            return next
        except IndexError:
            self.lock.release()
            raise StopIteration

    def __len__(self):
        self.lock.acquire()
        length = len(self.actualList)
        self.lock.release()
        return length
    
    def __list__(self):
        self.lock.acquire()
        actualList = self.actualList.copy()
        self.lock.release()
        return actualList

    def append(self,item):
        self.lock.acquire()
        self.actualList.append(item)
        self.lock.release()

    def pop(self):
        try:
            self.lock.acquire()
            item = self.actualList.pop()
            self.lock.release()
            return item
        except IndexError:
            self.lock.release()
            raise IndexError
        
    def clear(self):
        self.lock.acquire()
        self.actualList.clear()
        self.lock.release()